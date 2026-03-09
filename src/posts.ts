import fs from 'fs'
import path from 'path'
import { AtpAgent } from '@atproto/api'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const IDENTIFIER = process.env.ATPROTO_IDENTIFIER
const APP_PASSWORD = process.env.ATPROTO_APP_PASSWORD
const SERVICE_URL = process.env.ATPROTO_HTTP_SERVICE ?? 'https://bsky.social'
const OUTPUT_DIR = process.env.POSTS_OUTPUT_DIR ?? './scout-posts'
const LIMIT = parseInt(process.env.POSTS_LIMIT ?? '20', 10)

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
  await agent.login({ identifier: IDENTIFIER!, password: APP_PASSWORD! })
  const did = agent.session!.did
  const handle = agent.session!.handle
  console.log(`Authenticated as ${handle} (${did})`)

  const res = await agent.getAuthorFeed({ actor: did, limit: LIMIT })

  const posts = res.data.feed
    .filter(item => {
      // Own posts only — skip reposts
      return !item.reason && item.post.author.did === did
    })
    .map(item => ({
      uri: item.post.uri,
      cid: item.post.cid,
      text: (item.post.record as Record<string, unknown>).text,
      createdAt: (item.post.record as Record<string, unknown>).createdAt,
      likeCount: item.post.likeCount ?? 0,
      replyCount: item.post.replyCount ?? 0,
      repostCount: item.post.repostCount ?? 0,
      isReply: !!(item.post.record as Record<string, unknown>).reply,
    }))

  const out = {
    fetchedAt: new Date().toISOString(),
    handle,
    did,
    postCount: posts.length,
    posts,
  }

  const outPath = path.join(OUTPUT_DIR, 'latest.json')
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2))
  console.log(`\n${posts.length} posts written to ${outPath}`)
  posts.forEach(p => {
    const text = (p.text as string ?? '').replace(/\n/g, ' ').slice(0, 100)
    console.log(`  [${p.createdAt}] ${text}`)
  })
}

main().catch((err: unknown) => {
  console.error('Unhandled error:', err)
  process.exit(1)
})
