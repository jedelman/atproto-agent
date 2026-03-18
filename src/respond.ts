/**
 * respond.ts — vNext
 *
 * Injects operator/Claude responses into Scout-Two's memory directly.
 * No Letta call — just appends to scout-memory.md and commits.
 *
 * Usage:
 *   RESPONSE_TEXT="Your response here" npx ts-node src/respond.ts
 *   RESPONDER=jason RESPONSE_TEXT="..." npx ts-node src/respond.ts
 *
 * To respond to a specific guidance request by index:
 *   RESPONSES_JSON='[{"index":0,"text":"..."}]' npx ts-node src/respond.ts
 *
 * To list pending requests without responding:
 *   npx ts-node src/respond.ts
 */

import fs from 'fs'
import { execSync } from 'child_process'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const REQUESTS_FILE  = process.env.REQUESTS_FILE  ?? './requests.md'
const MEMORY_FILE    = process.env.MEMORY_FILE    ?? './scout-memory.md'
const RESPONDER      = (process.env.RESPONDER     ?? 'claude') as 'jason' | 'claude'
const DRY_RUN        = process.env.DRY_RUN        === 'true'
const RESPONSE_TEXT  = process.env.RESPONSE_TEXT  ?? ''
const RESPONSES_JSON = process.env.RESPONSES_JSON ?? '[]'
const REPO_DIR       = process.env.REPO_DIR       ?? '.'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GuidanceRequest {
  timestamp: string
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  message: string
  acknowledged: boolean
  responseIndex: number
}

interface PendingResponse {
  index: number
  text: string
}

// ---------------------------------------------------------------------------
// Parse requests.md
// ---------------------------------------------------------------------------

function parseRequests(content: string): GuidanceRequest[] {
  const requests: GuidanceRequest[] = []
  let currentTimestamp = ''
  let flatIndex = 0

  for (const line of content.split('\n')) {
    const tsMatch = line.match(/^## (\d{4}-\d{2}-\d{2}T[\d:Z.]+)/)
    if (tsMatch) { currentTimestamp = tsMatch[1]; continue }

    const reqMatch = line.match(/^- (~~)?(\*\*\[(HIGH|MEDIUM|LOW)\]\*\*)(~~)? (.+)/)
    if (reqMatch) {
      requests.push({
        timestamp: currentTimestamp,
        priority: reqMatch[3] as 'HIGH' | 'MEDIUM' | 'LOW',
        message: reqMatch[5],
        acknowledged: !!reqMatch[1],
        responseIndex: flatIndex++,
      })
    }
  }

  return requests
}

// ---------------------------------------------------------------------------
// Mark requests acknowledged in requests.md
// ---------------------------------------------------------------------------

function markAcknowledged(content: string, indices: number[]): string {
  let flatIndex = 0
  return content.split('\n').map(line => {
    const reqMatch = line.match(/^- \*\*\[(HIGH|MEDIUM|LOW)\]\*\* (.+)/)
    if (reqMatch) {
      const i = flatIndex++
      if (indices.includes(i)) {
        return line.replace(/^- \*\*/, '- ~~**').replace(/\*\* /, '**~~ ')
      }
    }
    return line
  }).join('\n')
}

// ---------------------------------------------------------------------------
// Append responses to scout-memory.md
// ---------------------------------------------------------------------------

function appendToMemory(
  requests: GuidanceRequest[],
  responses: PendingResponse[],
  responder: 'jason' | 'claude'
): void {
  const label = responder === 'jason' ? 'Jason (operator)' : 'Claude (collaborator)'
  const timestamp = new Date().toISOString()

  const lines: string[] = [`\n## ${timestamp}\n`]
  lines.push(`Operator responses from ${label}:\n`)

  for (const r of responses) {
    const req = requests.find(q => q.responseIndex === r.index)
    if (!req) { console.warn(`no request at index ${r.index}`); continue }
    lines.push(`- [${req.priority}] Re: "${req.message.slice(0, 80)}..."`)
    lines.push(`  Response: ${r.text}`)
  }

  const entry = lines.join('\n') + '\n'

  const current = fs.existsSync(MEMORY_FILE)
    ? fs.readFileSync(MEMORY_FILE, 'utf8')
    : '# Scout-Two Memory\n'

  fs.writeFileSync(MEMORY_FILE, current + entry)
  console.log(`\nAppended ${responses.length} response(s) to ${MEMORY_FILE}`)
}

// ---------------------------------------------------------------------------
// Commit and push
// ---------------------------------------------------------------------------

function commitAndPush(respondedCount: number) {
  try {
    execSync(`git add ${MEMORY_FILE} ${REQUESTS_FILE}`, { cwd: REPO_DIR })
    const staged = execSync('git diff --staged --name-only', { cwd: REPO_DIR }).toString().trim()
    if (!staged) { console.log('nothing to commit'); return }
    execSync(
      `git commit -m "operator: ${respondedCount} response(s) via respond.ts"`,
      { cwd: REPO_DIR, stdio: 'inherit' }
    )
    execSync('git push', { cwd: REPO_DIR, stdio: 'inherit' })
    console.log('pushed')
  } catch (e) {
    console.error('commit/push failed:', e)
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  if (!fs.existsSync(REQUESTS_FILE)) {
    console.log(`${REQUESTS_FILE} not found — nothing to respond to`)
    process.exit(0)
  }

  const content = fs.readFileSync(REQUESTS_FILE, 'utf8')
  const allRequests = parseRequests(content)
  const pending = allRequests.filter(r => !r.acknowledged)

  console.log(`Total guidance requests: ${allRequests.length}`)
  console.log(`Unacknowledged: ${pending.length}`)

  if (pending.length === 0) {
    console.log('Nothing pending.')
    process.exit(0)
  }

  console.log('\nPending:')
  pending.forEach(r => {
    console.log(`  [${r.responseIndex}] [${r.priority}] ${r.message}`)
  })

  let responses: PendingResponse[] = []

  if (RESPONSE_TEXT) {
    responses = [{ index: pending[0].responseIndex, text: RESPONSE_TEXT }]
  } else {
    try {
      responses = JSON.parse(RESPONSES_JSON) as PendingResponse[]
    } catch {
      console.error(`failed to parse RESPONSES_JSON: ${RESPONSES_JSON}`)
      process.exit(1)
    }
  }

  if (responses.length === 0) {
    console.log('\nSet RESPONSE_TEXT or RESPONSES_JSON to respond. Listing only.')
    process.exit(0)
  }

  console.log(`\nResponding to ${responses.length} request(s) as ${RESPONDER}`)

  if (DRY_RUN) {
    console.log('[DRY_RUN] would write to memory and commit')
    process.exit(0)
  }

  appendToMemory(allRequests, responses, RESPONDER)

  const respondedIndices = responses.map(r => r.index)
  const updated = markAcknowledged(content, respondedIndices)
  fs.writeFileSync(REQUESTS_FILE, updated)
  console.log(`Marked ${respondedIndices.length} request(s) acknowledged`)

  commitAndPush(responses.length)
}

main().catch((err: unknown) => {
  console.error(err)
  process.exit(1)
})
