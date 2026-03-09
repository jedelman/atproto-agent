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
const LIMIT = parseInt(process.env.FEED_LIMIT ?? '100', 10)
const MAX_PAGES = parseInt(process.env.FEED_MAX_PAGES ?? '1', 10)
const FETCH_THREADS = process.env.FETCH_THREADS !== 'false'
const THREAD_DEPTH_TOP_LEVEL = parseInt(process.env.THREAD_DEPTH_TOP_LEVEL ?? '3', 10)
const THREAD_DEPTH_REPLY = parseInt(process.env.THREAD_DEPTH_REPLY ?? '10', 10)
const CURSOR_FILE = process.env.CURSOR_FILE ?? './feed-cursor.json'

if (!IDENTIFIER || !APP_PASSWORD) {
  console.error('ATPROTO_IDENTIFIER and ATPROTO_APP_PASSWORD are required')
  process.exit(1)
}

// ---------------------------------------------------------------------------
// Cursor persistence
// ---------------------------------------------------------------------------

interface CursorState {
  feedCursor?: string
  notifCursor?: string
  savedAt?: string
}

function loadCursors(): CursorState {
  try {
    const raw = fs.readFileSync(CURSOR_FILE, 'utf8')
    const state = JSON.parse(raw) as CursorState
    console.log(`Loaded cursors — feed: ${state.feedCursor ?? 'none'}, notif: ${state.notifCursor ?? 'none'}`)
    return state
  } catch {
    console.log('No cursor file found — fetching from live tip')
    return {}
  }
}

function saveCursors(state: CursorState) {
  fs.writeFileSync(CURSOR_FILE, JSON.stringify({ ...state, savedAt: new Date().toISOString() }, null, 2))
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

async function fetchThreadParents(agent: AtpAgent, uri: string, isReply: boolean): Promise<ThreadPost[]> {
  const parentHeight = isReply ? THREAD_DEPTH_REPLY : THREAD_DEPTH_TOP_LEVEL
  try {
    const res = await agent.getPostThread({ uri, depth: 0, parentHeight })
    const parents: ThreadPost[] = []
    let node = (res.data.thread as Record<string, unknown>).parent as Record<string, unknown> | undefined
    while (node && node.$type === 'app.bsky.feed.defs#threadViewPost') {
      const post = node.post as Record<string, unknown>
      const record = post.record as Record<string, unknown>
      const author = post.author as Record<string, unknown>
      parents.unshift({
        uri: post.uri as string,
        author: (author.handle as string) ?? (author.did as string),
        text: ((record.text as string) ?? '').slice(0, 500),
        createdAt: record.createdAt as string,
      })
      node = node.parent as Record<string, unknown> | undefined
    }
    return parents
  } catch {
    return []
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
// Notifications
// ---------------------------------------------------------------------------

interface NotificationItem {
  _type: 'notification'
  reason: string
  uri?: string
  authorHandle: string
  authorDid: string
  text?: string
  indexedAt: string
  threadParents: ThreadPost[]
}

async function fetchNotifications(
  agent: AtpAgent,
  savedCursor: string | undefined
): Promise<{ items: NotificationItem[]; newCursor: string | undefined }> {
  const items: NotificationItem[] = []
  let newCursor: string | undefined

  try {
    const res = await agent.listNotifications({ limit: 50, cursor: savedCursor })
    newCursor = res.data.cursor

    for (const notif of res.data.notifications) {
      if (notif.isRead && savedCursor) continue

      const record = notif.record as Record<string, unknown>
      const text = typeof record.text === 'string' ? record.text : undefined
      const uri = notif.uri

      let threadParents: ThreadPost[] = []
      const isEngagement = notif.reason === 'mention' || notif.reason === 'reply' || notif.reason === 'quote'
      if (isEngagement && uri && FETCH_THREADS) {
        threadParents = await fetchThreadParents(agent, uri, true)
      }

      items.push({
        _type: 'notification',
        reason: notif.reason,
        uri,
        authorHandle: notif.author.handle ?? notif.author.did,
        authorDid: notif.author.did,
        text,
        indexedAt: notif.indexedAt,
        threadParents,
      })
    }

    if (items.length > 0) {
      await agent.updateSeenNotifications()
    }

    console.log(`Notifications: ${items.length} new`)
  } catch (e) {
    console.warn(`Failed to fetch notifications: ${e}`)
  }

  return { items, newCursor }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })

  const agent = new AtpAgent({ service: SERVICE_URL })
  await agent.login({ identifier: IDENTIFIER!, password: APP_PASSWORD! })
  const selfDid = agent.session!.did
  console.log(`Authenticated as ${agent.session!.handle} (${selfDid})`)

  const cursors = loadCursors()
  const followerDids = await fetchFollowerDids(agent, selfDid)

  const runId = new Date().toISOString().replace(/[:.]/g, '-')
  const outPath = path.join(OUTPUT_DIR, `feed-${runId}.jsonl`)
  const stream = fs.createWriteStream(outPath, { flags: 'w' })

  // Notifications first — direct engagement is highest priority
  const { items: notifItems, newCursor: newNotifCursor } = await fetchNotifications(
    agent, cursors.notifCursor
  )
  for (const item of notifItems) {
    stream.write(JSON.stringify(item) + '\n')
  }

  // Timeline
  let feedCursor: string | undefined = cursors.feedCursor
  let newFeedCursor: string | undefined
  let totalPosts = 0
  let skipped = 0
  let page = 0

  console.log(`Fetching timeline (from cursor=${feedCursor ?? 'live tip'})...`)

  do {
    const res = await agent.getTimeline({ limit: LIMIT, cursor: feedCursor })

    // First page cursor = resume point for next run
    if (page === 0) newFeedCursor = res.data.cursor

    for (const item of res.data.feed) {
      const post = item.post
      const record = post.record as Record<string, unknown>
      const isReply = !!record.reply
      const authorDid = post.author.did

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

      let threadParents: ThreadPost[] = []
      if (FETCH_THREADS) {
        threadParents = await fetchThreadParents(agent, post.uri, isReply)
      }

      stream.write(JSON.stringify({ ...item, _type: 'feed', threadParents }) + '\n')
      totalPosts++
    }

    feedCursor = res.data.cursor
    page++
    console.log(`Page ${page}: kept ${totalPosts}, skipped ${skipped}`)
  } while (feedCursor && page < MAX_PAGES)

  stream.end()

  saveCursors({
    feedCursor: newFeedCursor,
    notifCursor: newNotifCursor ?? cursors.notifCursor,
  })
  console.log(`Cursors saved — feed: ${newFeedCursor ?? 'none'}, notif: ${newNotifCursor ?? 'none'}`)

  const summary = {
    fetchedAt: new Date().toISOString(),
    handle: agent.session?.handle,
    did: selfDid,
    notifications: notifItems.length,
    timelinePosts: totalPosts,
    skippedByEtiquette: skipped,
    pages: page,
    outputFile: outPath,
  }

  fs.writeFileSync(path.join(OUTPUT_DIR, 'feed-summary.json'), JSON.stringify(summary, null, 2))
  console.log(`\nDone. ${notifItems.length} notifications + ${totalPosts} timeline posts`)
}

main().catch((err: unknown) => {
  console.error('Error:', err)
  process.exit(1)
})
