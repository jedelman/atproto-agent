import fs from 'fs'
import path from 'path'
import { AtpAgent } from '@atproto/api'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const IDENTIFIER = process.env.ATPROTO_IDENTIFIER
const APP_PASSWORD = process.env.ATPROTO_APP_PASSWORD
const OUTPUT_DIR = process.env.OUTPUT_DIR ?? './output'
const SERVICE_URL = process.env.ATPROTO_HTTP_SERVICE ?? 'https://bsky.social'
const LIMIT = parseInt(process.env.FEED_LIMIT ?? '100', 10) // max per page is 100
const MAX_PAGES = parseInt(process.env.FEED_MAX_PAGES ?? '1', 10)
const FETCH_THREADS = process.env.FETCH_THREADS !== 'false' // default true
const MAX_THREAD_DEPTH = parseInt(process.env.MAX_THREAD_DEPTH ?? '3', 10)

if (!IDENTIFIER || !APP_PASSWORD) {
  console.error('ATPROTO_IDENTIFIER and ATPROTO_APP_PASSWORD are required')
  process.exit(1)
}

// ---------------------------------------------------------------------------
// Thread fetching
// ---------------------------------------------------------------------------

interface ThreadPost {
  uri: string
  author: string
  text: string
  createdAt: string
}

async function fetchThreadParents(agent: AtpAgent, uri: string): Promise<ThreadPost[]> {
  try {
    const res = await agent.getPostThread({ uri, depth: 0, parentHeight: MAX_THREAD_DEPTH })
    const parents: ThreadPost[] = []

    // Walk up the parent chain
    let node = (res.data.thread as Record<string, unknown>).parent as Record<string, unknown> | undefined
    while (node && node.$type === 'app.bsky.feed.defs#threadViewPost') {
      const post = node.post as Record<string, unknown>
      const record = post.record as Record<string, unknown>
      const author = post.author as Record<string, unknown>
      parents.unshift({
        uri: post.uri as string,
        author: (author.handle as string) ?? (author.did as string),
        text: ((record.text as string) ?? '').slice(0, 300),
        createdAt: record.createdAt as string,
      })
      node = node.parent as Record<string, unknown> | undefined
    }
    return parents
  } catch {
    return [] // thread fetch is best-effort
  }
}

// ---------------------------------------------------------------------------
// Followers cache
// ---------------------------------------------------------------------------

async function fetchFollowerDids(agent: AtpAgent, did: string): Promise<Set<string>> {
  const followers = new Set<string>()
  try {
    let cursor: string | undefined
    do {
      const res = await agent.getFollowers({ actor: did, limit: 100, cursor })
      for (const f of res.data.followers) followers.add(f.did)
      cursor = res.data.cursor
    } while (cursor)
    console.log(`Loaded ${followers.size} followers`)
  } catch (e) {
    console.warn(`Failed to load followers: ${e}`)
  }
  return followers
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })

  const agent = new AtpAgent({ service: SERVICE_URL })

  console.log(`Logging in as ${IDENTIFIER}...`)
  await agent.login({ identifier: IDENTIFIER!, password: APP_PASSWORD! })
  const selfDid = agent.session!.did
  console.log(`Authenticated as ${selfDid}`)

  // Load followers for etiquette filtering
  const followerDids = await fetchFollowerDids(agent, selfDid)

  const runId = new Date().toISOString().replace(/[:.]/g, '-')
  const outPath = path.join(OUTPUT_DIR, `feed-${runId}.jsonl`)
  const stream = fs.createWriteStream(outPath, { flags: 'w' })

  let cursor: string | undefined
  let totalPosts = 0
  let skipped = 0
  let page = 0

  console.log(`Fetching home timeline (limit=${LIMIT}, max_pages=${MAX_PAGES})...`)

  do {
    const res = await agent.getTimeline({ limit: LIMIT, cursor })

    for (const item of res.data.feed) {
      const post = item.post
      const record = post.record as Record<string, unknown>
      const isReply = !!record.reply
      const authorDid = post.author.did

      // Bot etiquette: for reply threads, only engage if:
      // 1. Scout-Two is explicitly mentioned/tagged, OR
      // 2. The author follows Scout-Two
      if (isReply) {
        const mentionedSelf = ((record.text as string) ?? '').includes(selfDid) ||
          (record.facets as Array<Record<string, unknown>> ?? []).some(f =>
            (f.features as Array<Record<string, unknown>> ?? []).some(feat =>
              feat.$type === 'app.bsky.richtext.facet#mention' && feat.did === selfDid
            )
          )
        const authorFollows = followerDids.has(authorDid)

        if (!mentionedSelf && !authorFollows) {
          skipped++
          continue
        }
      }

      // Fetch thread context for replies
      let threadParents: ThreadPost[] = []
      if (isReply && FETCH_THREADS) {
        threadParents = await fetchThreadParents(agent, post.uri)
      }

      stream.write(JSON.stringify({ ...item, threadParents }) + '\n')
      totalPosts++
    }

    cursor = res.data.cursor
    page++
    console.log(`Page ${page}: ${res.data.feed.length} items, ${totalPosts} kept, ${skipped} skipped (etiquette filter)`)
  } while (cursor && page < MAX_PAGES)

  stream.end()

  // Summary
  const summary = {
    fetchedAt: new Date().toISOString(),
    did: agent.session?.did,
    handle: agent.session?.handle,
    service: SERVICE_URL,
    totalPosts,
    skippedByEtiquette: skipped,
    pages: page,
    outputFile: outPath,
  }

  const summaryPath = path.join(OUTPUT_DIR, 'feed-summary.json')
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2))

  console.log(`\nDone. ${totalPosts} posts written to ${outPath}`)
  console.log(JSON.stringify(summary, null, 2))
}

main().catch((err: unknown) => {
  console.error('Error:', err)
  process.exit(1)
})
