# atproto-scanner

Lexicon-agnostic AT Protocol firehose scanner. Streams all record types from the network, stores results as GitHub Actions artifacts, and resumes from cursor across runs.

## What it does

- Connects to `wss://bsky.network` (or any relay) via `@atproto/sync` `Firehose`
- Collects all `$type` record operations (create/update/delete), identity, and account events
- Writes per-run JSONL (one record per line) + a summary JSON grouped by collection
- Persists the firehose cursor between runs so each run picks up where the last left off
- No hardcoded lexicons — works with any current or future collection type

## Local usage

```bash
npm install
npm run build

# 15-second test run
SCAN_DURATION_MS=15000 npm run scan:built

# Full run
npm run scan:built
```

## Configuration (env vars)

| Variable | Default | Description |
|---|---|---|
| `SCAN_DURATION_MS` | `300000` | How long to scan (ms) |
| `OUTPUT_DIR` | `./output` | Where to write results |
| `CURSOR_FILE` | `./cursor.json` | Cursor persistence path |
| `ATPROTO_SERVICE` | `wss://bsky.network` | Relay WebSocket URL |
| `ATPROTO_UNAUTHENTICATED` | `true` | Skip commit DID verification (faster) |

## GitHub Actions

Runs every 6 hours via cron. Also triggerable via `workflow_dispatch` with custom duration.

**Artifacts:**
- `atproto-scan-{run_number}` — per-run JSONL + summary, retained 30 days
- `atproto-cursor` — cursor for next run, retained 90 days

**Secrets (optional, for AppView API calls):**
- `ATPROTO_IDENTIFIER` — handle or DID
- `ATPROTO_APP_PASSWORD` — app password from Bluesky settings

## Output format

### `records-{timestamp}.jsonl`

One JSON object per line:
```json
{"seq":1234,"time":"2026-03-09T...","event":"create","did":"did:plc:...","collection":"app.bsky.feed.post","rkey":"...","uri":"at://...","record":{...}}
```

### `summary.json`

```json
{
  "scannedAt": "...",
  "durationMs": 300000,
  "totalEvents": 45000,
  "lastSeq": 9876543,
  "collections": {
    "app.bsky.feed.post": { "creates": 1200, "updates": 5, "deletes": 3, "samples": [...] },
    ...
  }
}
```

## Letta agent integration

The JSONL output is designed to feed into Letta agents for analysis. Each run's artifact can be downloaded, parsed, and routed to agents by collection type or record content.
