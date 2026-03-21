/**
 * Scout-Two harness — vNext
 *
 * Replaces: feed.yml, agent.yml, respond.yml, think.ts, act.ts (for the run loop)
 * Requires: tap running locally (go install github.com/bluesky-social/indigo/cmd/tap)
 *           goat installed and authenticated (brew install goat && goat account login)
 *           ANTHROPIC_API_KEY in env (for claude -p)
 *           atproto-agent repo cloned locally (this file runs inside it)
 *
 * Usage:
 *   npx ts-node src/harness.ts
 *   DRY_RUN=true npx ts-node src/harness.ts
 *
 * Tap must be running separately:
 *   tap run
 *   (defaults to SQLite at ./tap.db, HTTP at :2480)
 */

import { execSync, spawnSync, SpawnSyncReturns } from 'child_process'
import { Tap, SimpleIndexer } from '@atproto/tap'
import fs from 'fs'
import path from 'path'

// ---------------------------------------------------------------------------
// Memory proxy secrets — load from pass if not already in env
// ---------------------------------------------------------------------------

function loadMemorySecrets() {
  if (!process.env.MEMORY_PROXY_URL) {
    const url = spawnSync('pass', ['show', 'cloudflare/memory-proxy-url'], { encoding: 'utf8' }).stdout?.trim()
    if (url) process.env.MEMORY_PROXY_URL = url
  }
  if (!process.env.MEMORY_PROXY_SECRET) {
    const secret = spawnSync('pass', ['show', 'cloudflare/memory-proxy-secret'], { encoding: 'utf8' }).stdout?.trim()
    if (secret) process.env.MEMORY_PROXY_SECRET = secret
  }
  if (process.env.MEMORY_PROXY_URL) {
    console.log(`Memory proxy: ${process.env.MEMORY_PROXY_URL}`)
  } else {
    console.warn('Memory proxy not configured — vector memory unavailable for this run')
  }
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const TAP_URL         = process.env.TAP_URL          ?? 'http://localhost:2480'
const TAP_ADMIN_PASS  = process.env.TAP_ADMIN_PASSWORD ?? ''
const REPO_DIR        = process.env.REPO_DIR          ?? '.'
const DRY_RUN         = process.env.DRY_RUN           === 'true'

// Debounce: wait this long after last event before triggering a Claude run.
// Prevents hammering the API on a burst of simultaneous posts from followed accounts.
const DEBOUNCE_MS     = parseInt(process.env.DEBOUNCE_MS     ?? '120000', 10)  // 2 min default
// Hard cap: trigger even if events keep arriving, after this long
const MAX_BATCH_MS    = parseInt(process.env.MAX_BATCH_MS    ?? '900000', 10)  // 15 min
// Don't run if fewer than this many events accumulated (avoids single-like triggers)
const MIN_EVENTS      = parseInt(process.env.MIN_EVENTS      ?? '3', 10)
// Claude Code max turns per run
const CLAUDE_MAX_TURNS = process.env.CLAUDE_MAX_TURNS ?? '25'

// Agent's own DID — events from this DID are ignored (don't trigger on own posts)
// Set via AGENT_DID env var. Required.
const AGENT_DID = process.env.AGENT_DID
if (!AGENT_DID) {
  console.error('AGENT_DID env var is required (e.g. export AGENT_DID=did:plc:...)')
  process.exit(1)
}

// Ensure ~/go/bin is in PATH for goat and other Go tools
process.env.PATH = `${process.env.HOME}/go/bin:${process.env.PATH ?? ''}`

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface BufferedEvent {
  did: string
  collection: string
  rkey: string
  action: 'create' | 'update' | 'delete'
  record?: Record<string, unknown>
  receivedAt: string
  live: boolean  // false = backfill (tap was offline), true = real-time
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const buffer: BufferedEvent[] = []
let debounceTimer: ReturnType<typeof setTimeout> | null = null
let batchTimer: ReturnType<typeof setTimeout> | null = null
let running = false  // prevent concurrent Claude runs

// ---------------------------------------------------------------------------
// Git ops
// ---------------------------------------------------------------------------

function gitPull() {
  console.log('↓ git pull --rebase')
  try {
    execSync('git pull --rebase', { cwd: REPO_DIR, stdio: 'inherit' })
  } catch (e) {
    console.error('git pull failed — continuing anyway:', e)
  }
}

function gitPushWithRetry() {
  try {
    execSync('git push', { cwd: REPO_DIR, stdio: 'inherit' })
    console.log('↑ pushed')
  } catch {
    console.log('push failed — retrying with rebase')
    try {
      execSync('git pull --rebase && git push', { cwd: REPO_DIR, stdio: 'pipe' })
      console.log('↑ pushed (after rebase)')
    } catch (e2) {
      console.error('push failed after retry:', e2)
    }
  }
}

// ---------------------------------------------------------------------------
// Feed digest builder
// ---------------------------------------------------------------------------

function buildDigest(events: BufferedEvent[]): string {
  const liveCount = events.filter(e => e.live).length
  const backfillCount = events.length - liveCount
  const batchType = backfillCount > liveCount
    ? `CATCHUP — ${backfillCount} backfill + ${liveCount} live (tap was offline)`
    : `LIVE — ${liveCount} real-time events`

  const lines: string[] = [
    `FEED DIGEST — ${new Date().toISOString()}`,
    `${events.length} events from ${new Set(events.map(e => e.did)).size} accounts [${batchType}]`,
    '',
  ]

  const posts = events.filter(e => e.collection === 'app.bsky.feed.post' && e.action === 'create')
  const notifs = events.filter(e => e.collection === 'app.bsky.notification' || e.did === AGENT_DID)
  const other = events.filter(e => !posts.includes(e) && !notifs.includes(e))

  if (posts.length > 0) {
    lines.push(`=== POSTS (${posts.length}) ===`, '')
    posts.forEach((e, i) => {
      const text = (e.record?.text as string ?? '').replace(/\n/g, ' ').slice(0, 400)
      const uri = `at://${e.did}/${e.collection}/${e.rkey}`
      lines.push(`[${i + 1}] @${e.did}`)
      lines.push(`    "${text}"`)
      lines.push(`    URI: ${uri}`)
      lines.push('')
    })
  }

  if (other.length > 0) {
    lines.push(`=== OTHER EVENTS (${other.length}) ===`, '')
    other.forEach(e => {
      lines.push(`  ${e.action} ${e.collection} by ${e.did} rkey=${e.rkey}`)
    })
    lines.push('')
  }

  lines.push('---')
  lines.push('Review this digest. Act per CLAUDE.md protocols.')
  lines.push('Read scout-memory.md and scout-posts/latest.json before acting.')
  lines.push('Update scout-memory.md and requests.md as warranted.')
  lines.push('Commit and push at the end of your run.')

  return lines.join('\n')
}

// ---------------------------------------------------------------------------
// Claude Code invocation
// ---------------------------------------------------------------------------

function runClaudeCode(digest: string): boolean {
  const digestPath = path.join('/tmp', `scout-feed-${Date.now()}.txt`)
  fs.writeFileSync(digestPath, digest)

  const prompt = `You are Scout-Two (scout-two.bsky.social) — your full identity, protocols, and run procedure are in CLAUDE.md.

A feed batch has arrived. Digest at: ${digestPath}

Run procedure:
1. Read the feed digest
2. Query semantic memory for relevant context — use topics and people from the digest:
   curl -s -X POST "$MEMORY_PROXY_URL/query" \\
     -H "Authorization: Bearer $MEMORY_PROXY_SECRET" \\
     -H "Content-Type: application/json" \\
     -d '{"text": "<your summary of feed topics>", "agent": "scout-two", "topK": 8}'
   Also query cross-agent (omit "agent") to surface what Claude has noted.
3. Read scout-memory.md for hot context
4. Act per CLAUDE.md — your judgment, your protocols. You are doing research, not just reacting.
5. Upsert significant observations to the memory proxy
6. Update scout-memory.md, append to requests.md if warranted
7. git add scout-memory.md memory/ requests.md scout-posts/latest.json && git diff --staged --quiet || git commit -m "scout-two: <ISO timestamp> — <brief description>"
8. git push`

  const allowedTools = [
    'Bash(goat bsky post *)',
    'Bash(goat xrpc *)',
    'Bash(goat resolve *)',
    'Bash(goat get *)',
    'Bash(git add *)',
    'Bash(git commit *)',
    'Bash(git push*)',
    'Bash(git diff *)',
    'Bash(git pull *)',
    'Bash(curl *)',
    'Bash(python3 *)',
    'Bash(date)',
    'Read',
    'Write',
  ].join(',')

  console.log(`\n[${new Date().toISOString()}] invoking claude -p (max-turns=${CLAUDE_MAX_TURNS})`)

  const args = [
    '-p', prompt,
    '--allowedTools', allowedTools,
    '--max-turns', CLAUDE_MAX_TURNS,
    '--output-format', 'stream-json',
    '--verbose',
  ]

  if (DRY_RUN) {
    console.log('[DRY_RUN] would invoke: claude', args.map(a => `"${a}"`).join(' '))
    fs.unlinkSync(digestPath)
    return true
  }

  // inherit stderr so tool calls are visible in terminal
  const result: SpawnSyncReturns<Buffer> = spawnSync('claude', args, {
    cwd: REPO_DIR,
    stdio: ['ignore', 'pipe', 'inherit'],
    env: { ...process.env },
  })

  fs.unlinkSync(digestPath)

  if (result.status !== 0) {
    console.error(`claude exited with status ${result.status}`)
    return false
  }

  // Parse stream-json output for summary
  const stdout = result.stdout?.toString() ?? ''
  const lines = stdout.split('\n').filter(Boolean)
  let resultText = ''
  for (const line of lines) {
    try {
      const obj = JSON.parse(line) as Record<string, unknown>
      if (obj.type === 'result') {
        resultText = (obj.result as string) ?? ''
      }
    } catch { /* skip */ }
  }

  if (resultText) {
    console.log('\n--- Scout-Two run summary ---')
    console.log(resultText.slice(0, 500))
  }

  return true
}

// ---------------------------------------------------------------------------
// Batch trigger
// ---------------------------------------------------------------------------

function clearTimers() {
  if (debounceTimer) { clearTimeout(debounceTimer); debounceTimer = null }
  if (batchTimer) { clearTimeout(batchTimer); batchTimer = null }
}

async function triggerRun(reason: string) {
  clearTimers()

  if (running) {
    console.log(`[${reason}] run already in progress — skipping`)
    buffer.length = 0
    return
  }

  const events = buffer.splice(0)  // drain buffer atomically
  if (events.length < MIN_EVENTS) {
    console.log(`[${reason}] only ${events.length} events (min ${MIN_EVENTS}) — skipping`)
    return
  }

  running = true
  console.log(`\n[${new Date().toISOString()}] trigger: ${reason} (${events.length} events)`)

  try {
    // Pull latest state before run (catches operator memory updates)
    gitPull()

    const digest = buildDigest(events)
    runClaudeCode(digest)
    // Note: Claude Code itself handles the git commit+push inside the run.
    // We don't push here — that would double-push.
  } catch (e) {
    console.error('run failed:', e)
  } finally {
    running = false
  }
}

function scheduleRun() {
  // Debounce: reset timer on each new event
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => triggerRun('debounce'), DEBOUNCE_MS)

  // Batch cap: start a max-wait timer on first event in batch
  if (!batchTimer) {
    batchTimer = setTimeout(() => triggerRun('batch-cap'), MAX_BATCH_MS)
  }
}

// ---------------------------------------------------------------------------
// Follow list sync — registers followed DIDs with Tap
// ---------------------------------------------------------------------------

async function tapRegister(dids: string[]) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (TAP_ADMIN_PASS) headers['Authorization'] = `Bearer ${TAP_ADMIN_PASS}`
  try {
    const res = await fetch(`${TAP_URL}/repos/add`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ dids }),
    })
    if (!res.ok) {
      console.error(`Tap /repos/add returned ${res.status}`)
    }
  } catch (e) {
    console.error('failed to register DIDs with Tap:', e)
  }
}

async function syncFollowList() {
  console.log('syncing follow list with Tap...')

  const result = spawnSync('goat', [
    'xrpc', 'query',
    'https://public.api.bsky.app',
    'app.bsky.graph.getFollows',
    `actor==${AGENT_DID}`,
    'limit==100',
  ], { encoding: 'utf8' })

  if (result.status !== 0) {
    console.error('failed to fetch follow list:', result.stderr)
    return
  }

  let follows: string[] = []
  try {
    const data = JSON.parse(result.stdout) as { follows: Array<{ did: string }> }
    follows = data.follows.map(f => f.did)
  } catch {
    console.error('failed to parse follow list')
    return
  }

  // Always include agent's own DID (for notifications)
  const dids = [...new Set([AGENT_DID!, ...follows])]
  await tapRegister(dids)
  console.log(`registered ${dids.length} DIDs with Tap`)
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  loadMemorySecrets()
  console.log('Scout-Two harness vNext starting...')
  console.log(`  Tap:          ${TAP_URL}`)
  console.log(`  Repo:         ${REPO_DIR}`)
  console.log(`  Debounce:     ${DEBOUNCE_MS / 1000}s`)
  console.log(`  Max batch:    ${MAX_BATCH_MS / 1000}s`)
  console.log(`  Min events:   ${MIN_EVENTS}`)
  console.log(`  Max turns:    ${CLAUDE_MAX_TURNS}`)
  console.log(`  Dry run:      ${DRY_RUN}`)
  console.log('')

  // Pull latest state on startup
  gitPull()

  // Register followed DIDs with Tap
  await syncFollowList()

  // Connect to Tap
  const tap = new Tap(TAP_URL, TAP_ADMIN_PASS ? { adminPassword: TAP_ADMIN_PASS } : undefined)
  const indexer = new SimpleIndexer()

  indexer.record(async (evt) => {
    // Own follow events: register the new DID with Tap immediately
    if (evt.did === AGENT_DID && evt.collection === 'app.bsky.graph.follow' && evt.action === 'create') {
      const record = (evt as Record<string, unknown>).record as Record<string, unknown> | undefined
      const followedDid = record?.subject as string | undefined
      if (followedDid && typeof followedDid === 'string') {
        console.log(`[follow] new follow detected: ${followedDid} — registering with Tap`)
        await tapRegister([followedDid])
      }
      return
    }

    // Ignore all other own actions (we'll see them in scout-posts/)
    if (evt.did === AGENT_DID) return

    // Only buffer record types we care about
    const relevant = [
      'app.bsky.feed.post',
      'app.bsky.feed.like',    // likes on agent's posts
      'app.bsky.graph.follow', // new follows of agent
    ]
    if (!relevant.includes(evt.collection)) return

    buffer.push({
      did: evt.did,
      collection: evt.collection,
      rkey: evt.rkey,
      action: evt.action as 'create' | 'update' | 'delete',
      record: (evt.action !== 'delete' && 'record' in evt)
        ? evt.record as Record<string, unknown>
        : undefined,
      receivedAt: new Date().toISOString(),
      live: (evt as Record<string, unknown>).live !== false,
    })

    scheduleRun()
  })

  indexer.error((err) => {
    console.error('Tap indexer error:', err)
  })

  const channel = tap.channel(indexer)

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\nshutting down...')
    clearTimers()
    await channel.destroy()
    process.exit(0)
  })

  process.on('SIGTERM', async () => {
    clearTimers()
    await channel.destroy()
    process.exit(0)
  })

  channel.start()
  console.log('connected to Tap — watching for events. Ctrl+C to stop.\n')
}

main().catch((err: unknown) => {
  console.error('fatal:', err)
  process.exit(1)
})
