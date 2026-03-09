import fs from 'fs'
import path from 'path'
import { AtpAgent, RichText } from '@atproto/api'
import type { ActionsSchema } from './think'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const IDENTIFIER = process.env.ATPROTO_IDENTIFIER
const APP_PASSWORD = process.env.ATPROTO_APP_PASSWORD
const SERVICE_URL = process.env.ATPROTO_HTTP_SERVICE ?? 'https://bsky.social'
const INPUT_DIR = process.env.THINK_OUTPUT_DIR ?? './think-output'
const REQUESTS_FILE = process.env.REQUESTS_FILE ?? './requests.md'
const DRY_RUN = process.env.DRY_RUN === 'true'

// Safety caps — prevent runaway action loops
const MAX_POSTS = parseInt(process.env.ACT_MAX_POSTS ?? '3', 10)
const MAX_REPLIES = parseInt(process.env.ACT_MAX_REPLIES ?? '5', 10)
const MAX_LIKES = parseInt(process.env.ACT_MAX_LIKES ?? '20', 10)
const MAX_REPOSTS = parseInt(process.env.ACT_MAX_REPOSTS ?? '5', 10)

if (!IDENTIFIER || !APP_PASSWORD) {
  console.error('ATPROTO_IDENTIFIER and ATPROTO_APP_PASSWORD are required')
  process.exit(1)
}

// ---------------------------------------------------------------------------
// Result tracking
// ---------------------------------------------------------------------------

interface ActionResult {
  action: string
  input: Record<string, unknown>
  success: boolean
  output?: Record<string, unknown>
  error?: string
}

const results: ActionResult[] = []

function record(action: string, input: Record<string, unknown>, success: boolean, output?: Record<string, unknown>, error?: string) {
  results.push({ action, input, success, output, error })
  if (success) {
    console.log(`  ✓ ${action}`)
  } else {
    console.error(`  ✗ ${action}: ${error}`)
  }
}

// ---------------------------------------------------------------------------
// Execute actions
// ---------------------------------------------------------------------------

async function executePosts(
  agent: AtpAgent,
  posts: ActionsSchema['actions']['posts']
) {
  const capped = posts.slice(0, MAX_POSTS)
  if (posts.length > MAX_POSTS) {
    console.warn(`  Capped posts: ${posts.length} → ${MAX_POSTS}`)
  }

  for (const p of capped) {
    console.log(`  Post: "${p.text.slice(0, 80)}..."`)
    if (DRY_RUN) {
      record('post', { text: p.text }, true, { dry_run: true })
      continue
    }
    try {
      const rt = new RichText({ text: p.text })
      await rt.detectFacets(agent)
      const res = await agent.post({
        text: rt.text,
        facets: rt.facets,
        createdAt: new Date().toISOString(),
      })
      record('post', { text: p.text }, true, { uri: res.uri, cid: res.cid })
    } catch (e) {
      record('post', { text: p.text }, false, undefined, String(e))
    }
  }
}

async function executeReplies(
  agent: AtpAgent,
  replies: ActionsSchema['actions']['replies']
) {
  const capped = replies.slice(0, MAX_REPLIES)
  if (replies.length > MAX_REPLIES) {
    console.warn(`  Capped replies: ${replies.length} → ${MAX_REPLIES}`)
  }

  for (const r of capped) {
    console.log(`  Reply to ${r.uri}: "${r.text.slice(0, 60)}..."`)
    if (DRY_RUN) {
      record('reply', { uri: r.uri, text: r.text }, true, { dry_run: true })
      continue
    }
    try {
      // Resolve the post to get its CID for the reply ref
      const parsed = new URL(r.uri.replace('at://', 'https://'))
      const did = parsed.hostname
      const rkey = parsed.pathname.split('/').pop()!

      const postRes = await agent.getPost({ repo: did, rkey })
      const parentRef = { uri: r.uri, cid: postRes.cid }

      // Walk up to find root (if post is itself a reply, use its root; otherwise post is root)
      let rootRef = parentRef
      const parentRecord = postRes.value as Record<string, unknown>
      if (parentRecord.reply && typeof parentRecord.reply === 'object') {
        const replyRefs = parentRecord.reply as { root: { uri: string; cid: string } }
        rootRef = { uri: replyRefs.root.uri, cid: replyRefs.root.cid }
      }

      const rt = new RichText({ text: r.text })
      await rt.detectFacets(agent)

      const res = await agent.post({
        text: rt.text,
        facets: rt.facets,
        reply: { parent: parentRef, root: rootRef },
        createdAt: new Date().toISOString(),
      })
      record('reply', { uri: r.uri, text: r.text }, true, { uri: res.uri, cid: res.cid })
    } catch (e) {
      record('reply', { uri: r.uri, text: r.text }, false, undefined, String(e))
    }
  }
}

async function executeLikes(
  agent: AtpAgent,
  likes: ActionsSchema['actions']['likes']
) {
  const capped = likes.slice(0, MAX_LIKES)
  if (likes.length > MAX_LIKES) {
    console.warn(`  Capped likes: ${likes.length} → ${MAX_LIKES}`)
  }

  for (const l of capped) {
    console.log(`  Like: ${l.uri}`)
    if (DRY_RUN) {
      record('like', { uri: l.uri }, true, { dry_run: true })
      continue
    }
    try {
      // Resolve CID for the like record
      const parsed = new URL(l.uri.replace('at://', 'https://'))
      const did = parsed.hostname
      const rkey = parsed.pathname.split('/').pop()!
      const postRes = await agent.getPost({ repo: did, rkey })

      const res = await agent.like(l.uri, postRes.cid)
      record('like', { uri: l.uri }, true, { uri: res.uri, cid: res.cid })
    } catch (e) {
      record('like', { uri: l.uri }, false, undefined, String(e))
    }
  }
}

async function executeReposts(
  agent: AtpAgent,
  reposts: ActionsSchema['actions']['reposts']
) {
  const capped = reposts.slice(0, MAX_REPOSTS)
  if (reposts.length > MAX_REPOSTS) {
    console.warn(`  Capped reposts: ${reposts.length} → ${MAX_REPOSTS}`)
  }

  for (const r of capped) {
    console.log(`  Repost: ${r.uri}`)
    if (DRY_RUN) {
      record('repost', { uri: r.uri }, true, { dry_run: true })
      continue
    }
    try {
      const parsed = new URL(r.uri.replace('at://', 'https://'))
      const did = parsed.hostname
      const rkey = parsed.pathname.split('/').pop()!
      const postRes = await agent.getPost({ repo: did, rkey })

      const res = await agent.repost(r.uri, postRes.cid)
      record('repost', { uri: r.uri }, true, { uri: res.uri, cid: res.cid })
    } catch (e) {
      record('repost', { uri: r.uri }, false, undefined, String(e))
    }
  }
}

// ---------------------------------------------------------------------------
// Out-of-band: append to requests.md
// ---------------------------------------------------------------------------

function writeOutOfBand(oob: ActionsSchema['out_of_band']) {
  const total = oob.guidance_requests.length + oob.feature_requests.length + oob.bug_reports.length
  if (total === 0) {
    console.log('  No out-of-band requests.')
    return
  }

  const timestamp = new Date().toISOString()
  const lines: string[] = [`\n## ${timestamp}\n`]

  if (oob.guidance_requests.length > 0) {
    lines.push('### Guidance Requests\n')
    for (const g of oob.guidance_requests) {
      lines.push(`- **[${g.priority.toUpperCase()}]** ${g.message}`)
    }
    lines.push('')
  }

  if (oob.feature_requests.length > 0) {
    lines.push('### Feature Requests\n')
    for (const f of oob.feature_requests) {
      lines.push(`- ${f.message}`)
    }
    lines.push('')
  }

  if (oob.bug_reports.length > 0) {
    lines.push('### Bug Reports\n')
    for (const b of oob.bug_reports) {
      lines.push(`- ${b.message}`)
    }
    lines.push('')
  }

  const entry = lines.join('\n')

  // Initialize requests.md if it doesn't exist
  if (!fs.existsSync(REQUESTS_FILE)) {
    fs.writeFileSync(REQUESTS_FILE, '# Scout-Two Out-of-Band Requests\n\nAutomatic log of guidance requests, feature requests, and bug reports from Scout-Two.\n')
  }

  fs.appendFileSync(REQUESTS_FILE, entry)
  console.log(`  Out-of-band appended to ${REQUESTS_FILE}: ${total} items`)

  // Surface high-priority guidance to stdout for CI visibility
  const highPriority = oob.guidance_requests.filter(g => g.priority === 'high')
  if (highPriority.length > 0) {
    console.warn('\n🚨 HIGH PRIORITY GUIDANCE REQUESTS:')
    highPriority.forEach(g => console.warn(`  - ${g.message}`))
  }
}

// ---------------------------------------------------------------------------
// Write run log
// ---------------------------------------------------------------------------

function writeRunLog() {
  const log = {
    ranAt: new Date().toISOString(),
    dryRun: DRY_RUN,
    did: undefined as string | undefined,
    results,
    summary: {
      total: results.length,
      succeeded: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
    },
  }

  const logPath = path.join(INPUT_DIR, 'act-log.json')
  fs.writeFileSync(logPath, JSON.stringify(log, null, 2))
  console.log(`\nRun log written to ${logPath}`)
  console.log(`Summary: ${log.summary.succeeded} succeeded, ${log.summary.failed} failed`)
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const actionsPath = path.join(INPUT_DIR, 'actions.json')
  if (!fs.existsSync(actionsPath)) {
    console.error(`actions.json not found at ${actionsPath}`)
    process.exit(1)
  }

  const actions = JSON.parse(fs.readFileSync(actionsPath, 'utf8')) as ActionsSchema

  console.log('Logging in to Bluesky...')
  const agent = new AtpAgent({ service: SERVICE_URL })
  if (!DRY_RUN) {
    await agent.login({ identifier: IDENTIFIER!, password: APP_PASSWORD! })
    console.log(`Authenticated as ${agent.session?.did}`)
  } else {
    console.log('[DRY RUN] Skipping Bluesky authentication')
  }

  console.log('\n--- Executing posts ---')
  await executePosts(agent, actions.actions.posts)

  console.log('\n--- Executing replies ---')
  await executeReplies(agent, actions.actions.replies)

  console.log('\n--- Executing likes ---')
  await executeLikes(agent, actions.actions.likes)

  console.log('\n--- Executing reposts ---')
  await executeReposts(agent, actions.actions.reposts)

  console.log('\n--- Out-of-band ---')
  writeOutOfBand(actions.out_of_band)

  writeRunLog()
}

main().catch((err: unknown) => {
  console.error('Unhandled error:', err)
  process.exit(1)
})
