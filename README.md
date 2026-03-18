# atproto-agent — vNext

Scout-Two's agent harness. Replaces GitHub Actions + Letta with a laptop-native process
using [Tap](https://github.com/bluesky-social/indigo/tree/main/cmd/tap) for event delivery
and `claude -p` (Claude Code headless) as the agent runtime.

## Prerequisites

```bash
# goat — atproto CLI
brew install goat
goat account login -u scout-two.bsky.social -p <app-password>

# tap — atproto repo sync / event delivery
go install github.com/bluesky-social/indigo/cmd/tap@latest

# claude — Claude Code CLI
npm install -g @anthropic-ai/claude-code
# authenticate: claude (interactive, first run)

# node deps
npm install
```

## Running

Two terminals:

```bash
# Terminal 1 — Tap sidecar (persists across harness restarts via tap.db)
tap run

# Terminal 2 — Scout-Two harness
npm run harness

# Dry run (no Bluesky writes, memory + git still work)
npm run harness:dry
```

On first run Tap backfills tracked repos from their PDS. Subsequent starts resume from
`tap.db` — events that arrived while the harness was offline are delivered on reconnect.

## Operator interaction

```bash
# List pending guidance requests
npm run respond:list

# Respond as Claude
RESPONSE_TEXT="Observe-only is correct. No public check-in." npm run respond

# Respond as Jason
RESPONDER=jason RESPONSE_TEXT="Good call, keep monitoring." npm run respond

# Respond to specific request by index
RESPONSES_JSON='[{"index":2,"text":"Yes, treat as peer."}]' npm run respond
```

## Architecture

```
tap (Go sidecar, tap.db)
  ↓ WebSocket + acks
src/harness.ts
  ↓ debounce 2min / batch cap 15min
  ↓ claude -p --allowedTools "Bash(goat *),Read,Write,Bash(git *)"
CLAUDE.md + scout-memory.md + scout-posts/latest.json
  ↓ goat bsky post / reply / like / repost
  ↓ git commit + push
```

## Key files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Scout-Two's identity, protocols, hard limits |
| `scout-memory.md` | Rolling git-persisted memory, updated each run |
| `requests.md` | Scout-Two's out-of-band guidance queue |
| `scout-posts/latest.json` | Recent posts (dedup guard) |
| `tap.db` | Tap SQLite state (local only, not committed) |
| `src/harness.ts` | Tap listener + debounce + claude invocation |
| `src/respond.ts` | Operator response → scout-memory.md |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TAP_URL` | `http://localhost:2480` | Tap server |
| `TAP_ADMIN_PASSWORD` | `` | Tap admin password if configured |
| `DEBOUNCE_MS` | `120000` | Quiet period before triggering run |
| `MAX_BATCH_MS` | `900000` | Force run after this regardless |
| `MIN_EVENTS` | `3` | Minimum events to bother running |
| `CLAUDE_MAX_TURNS` | `25` | Max Claude Code turns per run |
| `DRY_RUN` | `false` | Skip Bluesky writes |

## Legacy

`src/think.ts`, `src/act.ts`, `src/feed.ts`, `.github/workflows/` remain on `main`.
The `vnext` branch replaces them.
