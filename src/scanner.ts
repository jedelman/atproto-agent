import fs from 'fs'
import path from 'path'
import { Firehose } from '@atproto/sync'
import { IdResolver } from '@atproto/identity'
import type { CommitEvt, Event } from '@atproto/sync'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const SCAN_DURATION_MS = parseInt(process.env.SCAN_DURATION_MS ?? '300000', 10) // 5 min default
const OUTPUT_DIR = process.env.OUTPUT_DIR ?? './output'
const CURSOR_FILE = process.env.CURSOR_FILE ?? './cursor.json'
const MAX_SAMPLE_PER_COLLECTION = parseInt(process.env.MAX_SAMPLE_PER_COLLECTION ?? '5', 10)
const SERVICE_URL = process.env.ATPROTO_SERVICE ?? 'wss://bsky.network'
// When true, skips DID key verification (faster; set false to authenticate commits)
const UNAUTHENTICATED = process.env.ATPROTO_UNAUTHENTICATED !== 'false'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

type CollectionStats = {
  creates: number
  updates: number
  deletes: number
  samples: Record<string, unknown>[]
}

const collectionStats: Map<string, CollectionStats> = new Map()
let totalEvents = 0
let lastSeq: number | undefined

const recordsStream: fs.WriteStream = (() => {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })
  const runId = new Date().toISOString().replace(/[:.]/g, '-')
  const filePath = path.join(OUTPUT_DIR, `records-${runId}.jsonl`)
  console.log(`Writing records to ${filePath}`)
  return fs.createWriteStream(filePath, { flags: 'w' })
})()

// ---------------------------------------------------------------------------
// Cursor persistence
// ---------------------------------------------------------------------------

function loadCursor(): number | undefined {
  try {
    const raw = fs.readFileSync(CURSOR_FILE, 'utf8')
    const data = JSON.parse(raw)
    console.log(`Resuming from cursor seq=${data.seq}`)
    return data.seq
  } catch {
    console.log('No cursor found, starting from live tip')
    return undefined
  }
}

function saveCursor(seq: number) {
  fs.writeFileSync(CURSOR_FILE, JSON.stringify({ seq, savedAt: new Date().toISOString() }))
}

// ---------------------------------------------------------------------------
// Event handler
// ---------------------------------------------------------------------------

function getOrCreateStats(collection: string): CollectionStats {
  if (!collectionStats.has(collection)) {
    collectionStats.set(collection, { creates: 0, updates: 0, deletes: 0, samples: [] })
  }
  return collectionStats.get(collection)!
}

function handleEvent(evt: Event) {
  totalEvents++

  if (evt.event === 'create' || evt.event === 'update' || evt.event === 'delete') {
    const commit = evt as CommitEvt
    const stats = getOrCreateStats(commit.collection)

    if (commit.event === 'create') stats.creates++
    else if (commit.event === 'update') stats.updates++
    else if (commit.event === 'delete') stats.deletes++

    lastSeq = commit.seq

    // Write full record to JSONL (deletes have no record body)
    const line: Record<string, unknown> = {
      seq: commit.seq,
      time: commit.time,
      event: commit.event,
      did: commit.did,
      collection: commit.collection,
      rkey: commit.rkey,
      uri: commit.uri.toString(),
    }
    if (commit.event !== 'delete') {
      line.record = (commit as Extract<CommitEvt, { event: 'create' }>).record
      // Collect samples per collection
      if (stats.samples.length < MAX_SAMPLE_PER_COLLECTION) {
        stats.samples.push({
          uri: line.uri,
          record: line.record,
        })
      }
    }

    recordsStream.write(JSON.stringify(line) + '\n')
  } else if (evt.event === 'identity') {
    lastSeq = evt.seq
    const stats = getOrCreateStats('_identity')
    stats.creates++
  } else if (evt.event === 'account') {
    lastSeq = evt.seq
    const stats = getOrCreateStats('_account')
    stats.creates++
  }
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

function writeSummary() {
  const summary = {
    scannedAt: new Date().toISOString(),
    durationMs: SCAN_DURATION_MS,
    service: SERVICE_URL,
    totalEvents,
    lastSeq,
    collections: Object.fromEntries(
      [...collectionStats.entries()]
        .sort((a, b) => {
          const totalA = a[1].creates + a[1].updates + a[1].deletes
          const totalB = b[1].creates + b[1].updates + b[1].deletes
          return totalB - totalA
        })
        .map(([col, stats]) => [col, stats])
    ),
  }

  const summaryPath = path.join(OUTPUT_DIR, 'summary.json')
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2))
  console.log(`\nSummary written to ${summaryPath}`)
  console.log(`Total events: ${totalEvents}`)
  console.log(`Last seq: ${lastSeq}`)
  console.log(`\nTop collections:`)
  Object.entries(summary.collections)
    .slice(0, 15)
    .forEach(([col, stats]) => {
      const s = stats as CollectionStats
      console.log(`  ${col}: +${s.creates} ~${s.updates} -${s.deletes}`)
    })
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const cursor = loadCursor()

  const idResolver = new IdResolver()

  const firehose = new Firehose({
    service: SERVICE_URL,
    idResolver,
    unauthenticatedCommits: UNAUTHENTICATED,
    unauthenticatedHandles: true,
    getCursor: cursor !== undefined ? () => cursor : undefined,
    handleEvent,
    onError: (err: Error) => {
      // Log but don't crash — transient errors are common on the firehose
      console.error('Firehose error:', err.message)
    },
  })

  console.log(`Starting firehose scan for ${SCAN_DURATION_MS}ms against ${SERVICE_URL}`)

  // Start firehose (non-blocking — runs in background)
  firehose.start().catch((err: unknown) => {
    console.error('Fatal firehose error:', err)
    process.exit(1)
  })

  // Run for the configured duration
  await new Promise<void>((resolve) => setTimeout(resolve, SCAN_DURATION_MS))

  // Graceful shutdown
  await firehose.destroy()
  recordsStream.end()

  // Persist cursor and write summary
  if (lastSeq !== undefined) {
    saveCursor(lastSeq)
    console.log(`Cursor saved: seq=${lastSeq}`)
  }

  writeSummary()
}

main().catch((err: unknown) => {
  console.error('Unhandled error:', err)
  process.exit(1)
})
