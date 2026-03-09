import fs from 'fs'
import path from 'path'
import readline from 'readline'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const LETTA_BASE_URL = process.env.LETTA_BASE_URL
const LETTA_AGENT_ID = process.env.LETTA_AGENT_ID
const LETTA_API_KEY = process.env.LETTA_API_KEY
const INPUT_DIR = process.env.INPUT_DIR ?? './output'
const OUTPUT_DIR = process.env.THINK_OUTPUT_DIR ?? './think-output'
const MAX_POSTS = parseInt(process.env.THINK_MAX_POSTS ?? '50', 10)
const DRY_RUN = process.env.DRY_RUN === 'true'

if (!LETTA_BASE_URL || !LETTA_AGENT_ID) {
  console.error('LETTA_BASE_URL and LETTA_AGENT_ID are required')
  process.exit(1)
}
if (!LETTA_API_KEY) {
  console.warn('Warning: LETTA_API_KEY not set — assuming unauthenticated Letta instance')
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FeedItem {
  post: {
    uri: string
    cid: string
    author: {
      did: string
      handle: string
      displayName?: string
    }
    record: {
      text: string
      createdAt: string
      reply?: {
        parent: { uri: string }
        root: { uri: string }
      }
    }
    replyCount?: number
    repostCount?: number
    likeCount?: number
  }
  reason?: {
    $type: string
    by?: { handle: string }
  }
}

interface PostDigest {
  uri: string
  author: string
  displayName: string
  text: string
  createdAt: string
  likes: number
  reposts: number
  replies: number
  isReply: boolean
  repostedBy?: string
}

export interface ActionsSchema {
  actions: {
    posts: Array<{
      text: string
      rationale?: string
    }>
    replies: Array<{
      uri: string
      text: string
      rationale?: string
    }>
    likes: Array<{
      uri: string
      rationale?: string
    }>
    reposts: Array<{
      uri: string
      rationale?: string
    }>
  }
  out_of_band: {
    guidance_requests: Array<{
      priority: 'high' | 'medium' | 'low'
      message: string
    }>
    feature_requests: Array<{
      message: string
    }>
    bug_reports: Array<{
      message: string
    }>
  }
}

// ---------------------------------------------------------------------------
// Load feed JSONL
// ---------------------------------------------------------------------------

async function loadFeedItems(inputDir: string, maxPosts: number): Promise<PostDigest[]> {
  // Find the most recent feed JSONL file
  const files = fs.readdirSync(inputDir)
    .filter(f => f.startsWith('feed-') && f.endsWith('.jsonl'))
    .sort()
    .reverse()

  if (files.length === 0) {
    throw new Error(`No feed JSONL files found in ${inputDir}`)
  }

  const feedFile = path.join(inputDir, files[0])
  console.log(`Loading feed from ${feedFile}`)

  const items: PostDigest[] = []

  const rl = readline.createInterface({
    input: fs.createReadStream(feedFile),
    crlfDelay: Infinity,
  })

  for await (const line of rl) {
    if (!line.trim()) continue
    try {
      const item = JSON.parse(line) as FeedItem
      const post = item.post
      if (!post?.record?.text) continue

      items.push({
        uri: post.uri,
        author: post.author?.handle ?? post.author?.did,
        displayName: post.author?.displayName ?? post.author?.handle ?? '',
        text: post.record.text.slice(0, 500), // cap long posts
        createdAt: post.record.createdAt,
        likes: post.likeCount ?? 0,
        reposts: post.repostCount ?? 0,
        replies: post.replyCount ?? 0,
        isReply: !!post.record.reply,
        repostedBy: item.reason?.$type === 'app.bsky.feed.defs#reasonRepost'
          ? item.reason.by?.handle
          : undefined,
      })

      if (items.length >= maxPosts) break
    } catch {
      // skip malformed lines
    }
  }

  console.log(`Loaded ${items.length} posts`)
  return items
}

// ---------------------------------------------------------------------------
// Format digest for Scout-Two
// ---------------------------------------------------------------------------

function formatDigest(posts: PostDigest[]): string {
  const lines: string[] = [
    `FEED DIGEST — ${new Date().toISOString()}`,
    `${posts.length} posts from your home timeline`,
    '',
    'Posts (most recent first):',
    '',
  ]

  posts.forEach((p, i) => {
    lines.push(`[${i + 1}] @${p.author}${p.displayName ? ` (${p.displayName})` : ''}`)
    if (p.repostedBy) lines.push(`    ↻ reposted by @${p.repostedBy}`)
    lines.push(`    ${p.text.replace(/\n/g, ' ')}`)
    lines.push(`    ❤️ ${p.likes} 🔁 ${p.reposts} 💬 ${p.replies}  ${p.isReply ? '[reply]' : ''}`)
    lines.push(`    URI: ${p.uri}`)
    lines.push('')
  })

  lines.push('---')
  lines.push('Review this feed. Respond ONLY with a JSON object matching this exact schema:')
  lines.push('')
  lines.push(JSON.stringify({
    actions: {
      posts: [{ text: 'string — your original post text', rationale: 'optional string' }],
      replies: [{ uri: 'at:// URI of post to reply to', text: 'string', rationale: 'optional string' }],
      likes: [{ uri: 'at:// URI to like', rationale: 'optional string' }],
      reposts: [{ uri: 'at:// URI to repost', rationale: 'optional string' }],
    },
    out_of_band: {
      guidance_requests: [{ priority: 'high|medium|low', message: 'string' }],
      feature_requests: [{ message: 'string' }],
      bug_reports: [{ message: 'string' }],
    },
  }, null, 2))
  lines.push('')
  lines.push('All arrays may be empty. Do not include any text outside the JSON object.')

  return lines.join('\n')
}

// ---------------------------------------------------------------------------
// Call Letta
// ---------------------------------------------------------------------------

interface LettaMessage {
  role: string
  content: string | Array<{ type: string; text?: string }>
}

interface LettaResponse {
  messages: LettaMessage[]
  usage?: Record<string, number>
}

async function callLetta(digest: string): Promise<string> {
  const url = `${LETTA_BASE_URL}/v1/agents/${LETTA_AGENT_ID}/messages`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (LETTA_API_KEY) {
    headers['Authorization'] = `Bearer ${LETTA_API_KEY}`
  }

  const body = JSON.stringify({
    messages: [
      { role: 'user', content: digest },
    ],
    stream_steps: false,
    stream_tokens: false,
  })

  console.log(`Calling Letta: ${url}`)
  if (DRY_RUN) {
    console.log('[DRY RUN] Would send digest to Letta. Returning empty actions.')
    return JSON.stringify({
      actions: { posts: [], replies: [], likes: [], reposts: [] },
      out_of_band: { guidance_requests: [], feature_requests: [], bug_reports: [] },
    })
  }

  const res = await fetch(url, { method: 'POST', headers, body })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Letta API error ${res.status}: ${text}`)
  }

  const data = await res.json() as LettaResponse
  console.log(`Letta responded with ${data.messages?.length ?? 0} messages`)

  // Extract the last assistant message containing JSON
  for (let i = data.messages.length - 1; i >= 0; i--) {
    const msg = data.messages[i]
    if (msg.role !== 'assistant') continue

    const text = typeof msg.content === 'string'
      ? msg.content
      : msg.content
          .filter((b) => b.type === 'text')
          .map((b) => b.text ?? '')
          .join('')

    // Find JSON block in the response
    const jsonMatch = text.match(/\{[\s\S]*\}/)
    if (jsonMatch) return jsonMatch[0]
  }

  throw new Error('No JSON found in Letta response')
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })

  const posts = await loadFeedItems(INPUT_DIR, MAX_POSTS)
  if (posts.length === 0) {
    console.error('No posts to process — exiting without calling Letta')
    process.exit(1)
  }

  const digest = formatDigest(posts)
  console.log(`Digest prepared: ${digest.length} chars, ${posts.length} posts`)

  const rawResponse = await callLetta(digest)

  // Validate JSON
  let actions: ActionsSchema
  try {
    actions = JSON.parse(rawResponse) as ActionsSchema
  } catch (e) {
    throw new Error(`Failed to parse Letta response as JSON: ${e}\nRaw: ${rawResponse}`)
  }

  // Ensure schema completeness with defaults
  actions.actions ??= { posts: [], replies: [], likes: [], reposts: [] }
  actions.actions.posts ??= []
  actions.actions.replies ??= []
  actions.actions.likes ??= []
  actions.actions.reposts ??= []
  actions.out_of_band ??= { guidance_requests: [], feature_requests: [], bug_reports: [] }
  actions.out_of_band.guidance_requests ??= []
  actions.out_of_band.feature_requests ??= []
  actions.out_of_band.bug_reports ??= []

  const outPath = path.join(OUTPUT_DIR, 'actions.json')
  fs.writeFileSync(outPath, JSON.stringify(actions, null, 2))

  console.log(`\nActions written to ${outPath}`)
  console.log(`  posts:    ${actions.actions.posts.length}`)
  console.log(`  replies:  ${actions.actions.replies.length}`)
  console.log(`  likes:    ${actions.actions.likes.length}`)
  console.log(`  reposts:  ${actions.actions.reposts.length}`)
  console.log(`  guidance: ${actions.out_of_band.guidance_requests.length}`)
  console.log(`  features: ${actions.out_of_band.feature_requests.length}`)
  console.log(`  bugs:     ${actions.out_of_band.bug_reports.length}`)
}

main().catch((err: unknown) => {
  console.error('Unhandled error:', err)
  process.exit(1)
})
