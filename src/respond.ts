import fs from 'fs'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const LETTA_BASE_URL = process.env.LETTA_BASE_URL
const LETTA_AGENT_ID = process.env.LETTA_AGENT_ID
const LETTA_API_KEY = process.env.LETTA_API_KEY
const REQUESTS_FILE = process.env.REQUESTS_FILE ?? './requests.md'
const RESPONDER = (process.env.RESPONDER ?? 'claude') as 'jason' | 'claude'
const DRY_RUN = process.env.DRY_RUN === 'true'

// Pass responses as JSON via env: '[{"index":0,"text":"..."}]'
// Each index corresponds to a guidance_request in order of appearance
const RESPONSES_JSON = process.env.RESPONSES_JSON ?? '[]'

if (!LETTA_BASE_URL || !LETTA_AGENT_ID) {
  console.error('LETTA_BASE_URL and LETTA_AGENT_ID are required')
  process.exit(1)
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GuidanceRequest {
  timestamp: string
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  message: string
  acknowledged: boolean
  responseIndex?: number  // position in the flat list of all guidance requests
}

interface PendingResponse {
  index: number   // flat index across all guidance requests
  text: string
}

// ---------------------------------------------------------------------------
// Parse requests.md
// ---------------------------------------------------------------------------

function parseRequests(content: string): GuidanceRequest[] {
  const requests: GuidanceRequest[] = []
  let currentTimestamp = ''
  let flatIndex = 0

  const lines = content.split('\n')

  for (const line of lines) {
    // Timestamp header: ## 2026-03-09T18:33:50Z
    const tsMatch = line.match(/^## (\d{4}-\d{2}-\d{2}T[\d:Z.]+)/)
    if (tsMatch) {
      currentTimestamp = tsMatch[1]
      continue
    }

    // Guidance request: - **[HIGH]** message  OR  - ~~**[HIGH]**~~ (acknowledged)
    const reqMatch = line.match(/^- (~~)?(\*\*\[(HIGH|MEDIUM|LOW)\]\*\*)(~~)? (.+)/)
    if (reqMatch) {
      const acknowledged = !!reqMatch[1] // strikethrough = acknowledged
      const priority = reqMatch[3] as 'HIGH' | 'MEDIUM' | 'LOW'
      const message = reqMatch[5]
      requests.push({
        timestamp: currentTimestamp,
        priority,
        message,
        acknowledged,
        responseIndex: flatIndex++,
      })
    }
  }

  return requests
}

// ---------------------------------------------------------------------------
// Mark requests as acknowledged in requests.md
// ---------------------------------------------------------------------------

function markAcknowledged(content: string, indices: number[]): string {
  let flatIndex = 0
  const lines = content.split('\n')

  return lines.map(line => {
    const reqMatch = line.match(/^- (~~)?(\*\*\[(HIGH|MEDIUM|LOW)\]\*\*)(~~)? (.+)/)
    if (reqMatch) {
      const currentIndex = flatIndex++
      if (indices.includes(currentIndex) && !reqMatch[1]) {
        // Wrap in strikethrough to mark acknowledged
        return line.replace(/^- \*\*/, '- ~~**').replace(/\*\* /, '**~~ ')
      }
    }
    return line
  }).join('\n')
}

// ---------------------------------------------------------------------------
// Build Letta message
// ---------------------------------------------------------------------------

function buildMessage(requests: GuidanceRequest[], responses: PendingResponse[]): string {
  const responderLabel = RESPONDER === 'jason'
    ? '**Jason (your operator)** is responding'
    : '**Claude (your AI collaborator)** is responding on Jason\'s behalf'

  const lines: string[] = [
    `--- OUT-OF-BAND RESPONSE ---`,
    `${responderLabel} to your guidance requests.`,
    '',
  ]

  for (const r of responses) {
    const req = requests.find(q => q.responseIndex === r.index)
    if (!req) {
      console.warn(`No request found for index ${r.index} — skipping`)
      continue
    }

    lines.push(`**Your request [${req.priority}]** (${req.timestamp}):`)
    lines.push(`> ${req.message}`)
    lines.push('')
    lines.push(`**Response from ${RESPONDER === 'jason' ? 'Jason' : 'Claude'}:**`)
    lines.push(r.text)
    lines.push('')
  }

  lines.push('---')
  lines.push('No action required — this is guidance for your memory. Acknowledge with a brief confirmation.')

  return lines.join('\n')
}

// ---------------------------------------------------------------------------
// Send to Letta
// ---------------------------------------------------------------------------

async function sendToLetta(message: string): Promise<string[]> {
  const url = `${LETTA_BASE_URL}/v1/agents/${LETTA_AGENT_ID}/messages`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (LETTA_API_KEY) {
    headers['Authorization'] = `Bearer ${LETTA_API_KEY}`
  }

  const body = JSON.stringify({
    messages: [{ role: 'user', content: message }],
    stream_steps: false,
    stream_tokens: false,
  })

  console.log(`Sending response to Scout-Two at ${url}`)
  const res = await fetch(url, { method: 'POST', headers, body })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Letta API error ${res.status}: ${text}`)
  }

  const data = await res.json() as { messages: Array<{ id?: string; role: string; content: unknown }> }
  const messageIds = data.messages.map(m => m.id).filter((id): id is string => !!id)
  console.log(`Scout-Two acknowledged. Message IDs: ${messageIds.join(', ')}`)

  // Print Scout-Two's reply
  for (let i = data.messages.length - 1; i >= 0; i--) {
    const msg = data.messages[i]
    if (msg.role !== 'assistant') continue
    const raw = msg as Record<string, unknown>
    const toolCalls = raw.tool_calls as Array<Record<string, unknown>> | undefined
    if (toolCalls) {
      for (const tc of toolCalls) {
        const fnArgs = (tc.function as Record<string, unknown>)?.arguments
        const argsStr = typeof fnArgs === 'string' ? fnArgs : JSON.stringify(fnArgs ?? '')
        try {
          const parsed = JSON.parse(argsStr)
          const reply = parsed.message ?? parsed.content
          if (reply) {
            console.log(`\nScout-Two replied:\n${reply}`)
            break
          }
        } catch { /* ignore */ }
      }
    }
    break
  }

  return messageIds
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
    console.log('Nothing to respond to.')
    process.exit(0)
  }

  console.log('\nPending requests:')
  pending.forEach(r => {
    console.log(`  [${r.responseIndex}] [${r.priority}] ${r.message}`)
  })

  // Parse responses
  let responses: PendingResponse[] = []

  // Shortcut: RESPONSE_TEXT responds to index 0 without needing JSON syntax
  const RESPONSE_TEXT = process.env.RESPONSE_TEXT || undefined
  if (RESPONSE_TEXT) {
    responses = [{ index: 0, text: RESPONSE_TEXT }]
  } else {
    try {
      responses = JSON.parse(RESPONSES_JSON) as PendingResponse[]
    } catch {
      console.error(`Failed to parse RESPONSES_JSON: ${RESPONSES_JSON}`)
      process.exit(1)
    }
  }

  if (responses.length === 0) {
    console.log('\nNo RESPONSES_JSON provided — listing pending requests only. Set RESPONSES_JSON to respond.')
    process.exit(0)
  }

  const message = buildMessage(allRequests, responses)
  console.log(`\nMessage to Scout-Two:\n${message}\n`)

  if (DRY_RUN) {
    console.log('[DRY RUN] Would send above message to Letta.')
    process.exit(0)
  }

  const messageIds = await sendToLetta(message)

  // Mark responded-to requests as acknowledged in requests.md
  const respondedIndices = responses.map(r => r.index)
  const updated = markAcknowledged(content, respondedIndices)
  fs.writeFileSync(REQUESTS_FILE, updated)
  console.log(`\nMarked ${respondedIndices.length} request(s) as acknowledged in ${REQUESTS_FILE}`)
  console.log('Commit requests.md to persist acknowledgment.')

  console.log(`\nDone. Letta message IDs: ${messageIds.join(', ')}`)
}

main().catch((err: unknown) => {
  console.error('Unhandled error:', err)
  process.exit(1)
})
