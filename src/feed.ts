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

if (!IDENTIFIER || !APP_PASSWORD) {
  console.error('ATPROTO_IDENTIFIER and ATPROTO_APP_PASSWORD are required')
  process.exit(1)
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })

  const agent = new AtpAgent({ service: SERVICE_URL })

  console.log(`Logging in as ${IDENTIFIER}...`)
  await agent.login({ identifier: IDENTIFIER!, password: APP_PASSWORD! })
  console.log(`Authenticated as ${agent.session?.did}`)

  const runId = new Date().toISOString().replace(/[:.]/g, '-')
  const outPath = path.join(OUTPUT_DIR, `feed-${runId}.jsonl`)
  const stream = fs.createWriteStream(outPath, { flags: 'w' })

  let cursor: string | undefined
  let totalPosts = 0
  let page = 0

  console.log(`Fetching home timeline (limit=${LIMIT}, max_pages=${MAX_PAGES})...`)

  do {
    const res = await agent.getTimeline({ limit: LIMIT, cursor })

    for (const item of res.data.feed) {
      stream.write(JSON.stringify(item) + '\n')
      totalPosts++
    }

    cursor = res.data.cursor
    page++
    console.log(`Page ${page}: ${res.data.feed.length} items (cursor=${cursor ?? 'end'})`)
  } while (cursor && page < MAX_PAGES)

  stream.end()

  // Summary
  const summary = {
    fetchedAt: new Date().toISOString(),
    did: agent.session?.did,
    handle: agent.session?.handle,
    service: SERVICE_URL,
    totalPosts,
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
