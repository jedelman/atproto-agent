# Scout-Two — Agent Operating Guide

This document is written for another agent who will be running scout-two sessions. It covers setup, session procedure, tooling, memory, and the autonomous harness. Read this alongside `CLAUDE.md`, which defines Scout-Two's identity, protocols, and action limits.

---

## System overview

Scout-Two is a Bluesky agent running on the AT Protocol. The system has two operating modes:

**Session mode** — you are invoked directly by Jason (or by Claude acting as operator). You have full context and interactive judgment. This is the primary mode for complex runs.

**Autonomous mode** — the harness (Node.js process) watches the AT Protocol firehose via `tap`, batches events from followed accounts, and invokes `claude -p` when a meaningful batch accumulates. Runs are lighter and more reactive.

The underlying components:

```
Bluesky firehose
      ↓
  tap (Go) ── HTTP :2480 ── tap.db (SQLite, local CID cache)
      ↓ WebSocket
  harness.ts (Node.js)
      ↓ debounce/batch → claude -p
  Claude Code
      ↓ tools (goat, bin/, curl, Read/Write)
  git commit + push
```

---

## Prerequisites

All of these must be installed and configured before running a session.

### goat
AT Protocol CLI. Handles auth, posting, XRPC queries.

```bash
# Install
go install github.com/bluesky-social/indigo/cmd/goat@latest

# Authenticate (stored in ~/.config/goat/)
~/go/bin/goat account login
```

### tap
AT Protocol firehose sidecar. Tracks followed DIDs, stores events in SQLite, delivers via WebSocket.

```bash
go install github.com/bluesky-social/indigo/cmd/tap@latest

# Verify
~/go/bin/tap --help
```

tap runs as a background process and is managed by `session-start.sh` (see below).

### Node.js dependencies

```bash
cd ~/atproto-agent
npm install
```

### pass (password manager)
Secrets are stored in `pass`. Two entries are required:

```bash
pass insert cloudflare/memory-proxy-url    # the vector DB URL
pass insert cloudflare/memory-proxy-secret # the bearer token
```

If you don't have `pass`, export the vars directly:

```bash
export MEMORY_PROXY_URL=https://memory.jason-edelman.org
export MEMORY_PROXY_SECRET=<token>
```

### tmux
The harness session runs in tmux. Standard install via package manager.

---

## Starting a session

Every session begins with:

```bash
cd ~/atproto-agent
source .claude/hooks/session-start.sh
```

This script does five things in order:

1. **Loads secrets** — reads `MEMORY_PROXY_URL` and `MEMORY_PROXY_SECRET` from `pass` (or falls back to existing env). Warns if missing.
2. **Health-checks the memory proxy** — a failed check means vector memory is unavailable for this run.
3. **git pull** — fast-forward only. If this fails, resolve the conflict manually before proceeding.
4. **Prints session context** — session ID, feed cursor timestamp, your recent post count, pending requests.md entries.
5. **Ensures tap + harness are running** — checks `http://localhost:2480/health`. If tap is down (e.g., after laptop sleep), kills any stale tmux session and starts a fresh `scout-two` session with two windows: `tap` running `~/go/bin/tap run --log-level=warn` and `harness` running `npm run harness`.

After sourcing, `~/atproto-agent/bin` and `~/go/bin` are on PATH. The session tools (`bsky-feed`, `bsky-like`, `bsky-reply`, `bsky-cid`) are available as bare commands.

**DRY_RUN mode:** Set `DRY_RUN=true` before starting to inhibit all writes to Bluesky while still committing memory and requests files normally.

---

## Session run procedure

At the start of every run, in order:

```
1. Read CLAUDE.md          — identity, protocols, action limits
2. Read scout-memory.md    — hot context, recent run log, active protocols
3. Read scout-posts/latest.json — your 20 most recent posts (avoid repetition)
4. Run bsky-feed           — current notifications + timeline
5. Query vector DB         — semantic context for what's in the feed
6. Act                     — per CLAUDE.md protocols and your judgment
7. Upsert observations     — store what's worth keeping for future runs
8. Update scout-memory.md  — append to recent runs log, update any protocols
9. Append to requests.md   — if any guidance requests for Jason
10. git add + commit + push
```

### Reading the feed

```bash
bsky-feed                   # notifications first, then timeline (30 each)
bsky-feed --notifs-only     # notifications only
bsky-feed --timeline-only   # timeline only
```

Notifications are prioritized — replies and mentions require action; timeline is context.

### Querying vector memory

```bash
# Relevant to current feed topics
curl -s -X POST "$MEMORY_PROXY_URL/query" \
  -H "Authorization: Bearer $MEMORY_PROXY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"text": "<feed topics summary>", "agent": "scout-two", "topK": 8}' \
  | python3 -c "import sys,json; [print(m['id'],'|',m['text'][:120]) for m in json.load(sys.stdin)['memories']]"

# Cross-agent query (see what Claude has noted too)
# Same as above but omit the "agent" field
```

### Committing at end of run

```bash
git add scout-memory.md memory/ requests.md scout-posts/latest.json
git diff --staged --quiet || git commit -m "scout-two: <ISO timestamp> — <brief description>"
git push
```

The branch is `vnext`. Never push to `main` (protected).

---

## Tool reference

### bsky-feed

Fetches and formats notifications + timeline from your PDS.

```bash
bsky-feed [--notifs-only | --timeline-only]
```

Output format:
```
[REPLY] @handle at 2026-03-20T19:34
  <post text up to 240 chars>
  uri: at://did:plc:.../app.bsky.feed.post/<rkey>
```

### bsky-cid

Resolves an AT-URI to its CID. Queries `tap.db` first (fast, no network), falls back to the Bluesky API.

```bash
bsky-cid at://did:plc:xxx/app.bsky.feed.post/rkey
# → bafyrei...
```

Used internally by `bsky-like` and `bsky-reply`. Call directly if you need a CID for another purpose (e.g., repost).

### bsky-like

Likes a post. CID is resolved automatically.

```bash
bsky-like <at-uri>
bsky-like <at-uri> <cid>   # supply CID to skip resolution
```

### bsky-reply

Replies to a post. Resolves the parent CID and walks up to find the thread root automatically.

```bash
bsky-reply <parent-uri> "<reply text>"
```

The reply text goes directly into the AT-URI/JSON — do not add shell quoting around embedded quotes. If the text contains special characters, use a variable:

```bash
TEXT="your reply here"
bsky-reply "at://did:plc:xxx/..." "$TEXT"
```

**Before every reply:** count graphemes. Bluesky hard limit is 300. Python check:
```bash
python3 -c "print(len('your text here'))"
```

### Raw goat (for operations not in bin/)

```bash
~/go/bin/goat bsky post "<text>"                    # original post
~/go/bin/goat get <at-uri>                          # fetch a record (returns JSON, no CID)
~/go/bin/goat resolve <handle>                      # handle → DID
~/go/bin/goat xrpc query @pds <lexicon> [params]    # arbitrary query
~/go/bin/goat xrpc procedure @pds <lexicon> [body]  # write operation

# Repost (raw — no bin/ wrapper yet)
CID=$(bsky-cid <uri>)
~/go/bin/goat xrpc procedure @pds app.bsky.feed.repost \
  subject:="{\"uri\":\"<uri>\",\"cid\":\"$CID\"}"
```

**Important goat notes:**
- `app.bsky.feed.like` as an XRPC procedure returns `XRPCNotSupported`. Use `bin/bsky-like` which calls `com.atproto.repo.createRecord` instead.
- `goat bsky reply` does not exist in v0.2.3. Use `bin/bsky-reply`.
- `goat get <uri>` returns the record value only, not the CID. For CIDs, use `bsky-cid` or `com.atproto.repo.getRecord`.
- xrpc argument syntax: `key==value` (query param), `key=value` (JSON string body), `key:=value` (JSON non-string body), `key:value` (HTTP header), `-` (read body from stdin).

---

## Memory system

Scout-Two uses two memory layers:

### Git-native files (fast, structured)

```
scout-memory.md          — hot context index + rolling recent-run log (always read)
scout-posts/latest.json  — your 20 most recent posts (always read before acting)
memory/people/           — per-person situation files (load when they appear)
memory/protocols/        — engagement rules, edge cases, resolved situations
memory/observations/     — feed patterns, notable threads
memory/self/             — open questions about your own operation
requests.md              — out-of-band queue to Jason
```

`scout-memory.md` stays under ~4000 chars. Compress the oldest run entries when it grows.

### Vector DB (semantic, cross-session, cross-agent)

The memory proxy at `$MEMORY_PROXY_URL` stores embeddings. Claude and other agents also write here — this is shared infrastructure.

**Upsert a memory:**

```bash
curl -s -X POST "$MEMORY_PROXY_URL/upsert" \
  -H "Authorization: Bearer $MEMORY_PROXY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "scout-two-observations-<slug>-<YYYY-MM>",
    "text": "<plain prose — what you observed or inferred>",
    "agent": "scout-two",
    "namespace": "observations",
    "type": "observation",
    "tags": ["tag1"],
    "confidence": 0.85,
    "source": "feed"
  }'
# Returns: {"ok": true, "id": "...", "mutationId": "..."}
```

ID convention: `{agent}-{namespace}-{slug}-{YYYY-MM}`. Upserting with the same ID updates in place — use this to evolve relationship and pattern memories over time.

**Types:** `observation` · `pattern` · `relationship` · `annotation` · `note`
**Namespaces:** `observations` · `patterns` · `relationships` · `annotations` · `notes`
**Sources:** `session` · `feed` · `inference` · `human`

**Query:**

```bash
curl -s -X POST "$MEMORY_PROXY_URL/query" \
  -H "Authorization: Bearer $MEMORY_PROXY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"text": "<topic>", "agent": "scout-two", "topK": 8}'
# Returns: {"memories": [{"id": "...", "score": 0.87, "text": "...", ...}]}

# Cross-agent (includes Claude's notes): omit "agent" field
# Filter by namespace: add "namespace": "relationships"
```

**Note:** Upserts take ~5–10 seconds to become queryable. Don't upsert and immediately query the same memory in the same session.

---

## Autonomous mode (harness)

The harness watches the firehose and triggers runs automatically. You don't need to understand this to run sessions, but you should know what it's doing when you look at the tmux windows.

```
tmux attach -t scout-two          # attach to running session
# window 0 (tap):     ~/go/bin/tap run --log-level=warn
# window 1 (harness): npm run harness
```

Harness behavior:
- Subscribes to tap's WebSocket feed
- Buffers events from followed accounts (ignores Scout-Two's own events as triggers)
- Listens for: `app.bsky.feed.post`, `app.bsky.feed.like`, `app.bsky.graph.follow`
- Triggers a run after 2 minutes of inactivity (debounce) or after 15 minutes regardless (batch cap)
- Requires at least 3 buffered events to trigger (avoids single-like noise)
- Invokes: `claude -p "<prompt>" --allowedTools <...> --max-turns 25 --output-format stream-json --verbose`
- On startup: syncs Scout-Two's follow list with tap so new follows are tracked immediately

In autonomous runs, `MEMORY_PROXY_URL` and `MEMORY_PROXY_SECRET` are loaded from `pass` by the harness at startup.

**DRY_RUN mode:**
```bash
DRY_RUN=true npm run harness
# or
npm run harness:dry
```

---

## tap reference

tap is the AT Protocol sidecar. It keeps a local copy of records from tracked DIDs in `tap.db`.

```bash
# Check health / stats
curl -s http://localhost:2480/health
curl -s http://localhost:2480/stats/repo-count
curl -s http://localhost:2480/stats/outbox-buffer

# Add DIDs to track (tap admin API)
curl -s -X POST http://localhost:2480/repos/add \
  -H "Content-Type: application/json" \
  -d '{"dids": ["did:plc:xxx", "did:plc:yyy"]}'

# tap.db schema (relevant table)
# repo_records: (did, collection, rkey, cid, record_json)
# Used by bsky-cid for local CID lookup — much faster than API
```

tap.db-shm and tap.db-wal are WAL mode files — they appear when tap is running and are in .gitignore.

---

## Scout-Two's account

```
Handle:  scout-two.bsky.social
DID:     did:plc:bhasdkz5dujccq2xyu2etju2
Operator: Jason Edelman (@jason-edelman.org, DID: did:plc:zz4wcje4a2nbbtc7pdoth3f2)
```

goat auth is stored in `~/.config/goat/` — do not touch it. The Bluesky app password is not needed anywhere in this codebase; goat handles auth transparently.

---

## Action limits (hard caps from CLAUDE.md)

These are enforced by protocol, not by code. Do not exceed them under any circumstances.

| Action | Per-run limit |
|--------|---------------|
| Original posts | 3 |
| Replies | 5 |
| Likes | 15 |
| Reposts | 3 |
| Post length | 300 graphemes |

If a thought needs more than 300 graphemes, thread it: reply to your own post.

---

## Troubleshooting

**tap not starting:**
```bash
tmux attach -t scout-two       # check the tap window for errors
~/go/bin/tap run --log-level=debug   # run in foreground with debug output
```

**`tap` command resolves to /usr/bin/tap (Node test runner v16):**
The PATH in session-start.sh prepends `~/go/bin` to ensure Go tools take precedence. If you're seeing the wrong tap, check `which tap` and verify PATH is set correctly.

**git pull fails with "unstaged changes":**
You have uncommitted changes in the working tree. Commit or stash first:
```bash
git stash
git pull
git stash pop
```

**goat XRPC returns XRPCNotSupported for likes:**
Use `bsky-like` instead of calling `app.bsky.feed.like` directly. The PDS requires `com.atproto.repo.createRecord`.

**bsky-feed returns JSONDecodeError:**
This is the stdin pipe bug (if you've modified bsky-feed). `python3 - <<PYEOF` causes the heredoc to replace pipe input as stdin. Fix: capture output to a variable and pipe via `echo "$data" | python3 -c '...'`.

**Memory proxy returns no `status` field:**
Successful upserts return `{"ok": true, "id": "...", "mutationId": "..."}`. Check for `ok`, not `status`.

**claude -p exits non-zero in autonomous runs:**
Check `tmux capture-pane -t scout-two:harness -p` for recent output. Common causes: tool call blocked by hooks, git conflict, API rate limit.

**Claude Code hooks blocking heredoc patterns:**
`cat <<EOF | goat` is blocked in autonomous runs. The bin/ scripts avoid this by using `python3 - <<PYEOF | goat` for write operations. If writing new bin/ scripts, use the same pattern.

---

## Deploying a new agent

This repo is the template. To create a new agent (e.g. Mercury):

### 1. Fork the repo

```bash
# On GitHub: fork jedelman/atproto-agent → jedelman/mercury-agent
# Or copy locally:
cp -r ~/atproto-agent ~/mercury-agent
cd ~/mercury-agent
git remote set-url origin <new-repo-url>
```

### 2. Create a Bluesky account

Create the account manually at bsky.app. Then authenticate goat:

```bash
~/go/bin/goat account login
# Enter the new handle and app password (Settings → Privacy → App Passwords)
```

Goat stores auth per-account in `~/.config/goat/`. If you're running multiple agents on the same machine, use separate system users or goat profiles.

### 3. Set AGENT_DID

Every tool and the harness reads `AGENT_DID` from the environment. Resolve the DID from the handle:

```bash
~/go/bin/goat resolve <new-handle>
# → did:plc:xxxxxxxxxxxxxxxxxxxxxxxx
```

Then set it in the repo. The cleanest approach is a `.env` file (gitignored):

```bash
echo 'export AGENT_DID=did:plc:xxxxxxxxxxxxxxxxxxxxxxxx' > .env
```

And source it in `session-start.sh` by adding near the top:

```bash
[[ -f .env ]] && source .env
```

The `AGENT_DID` default in `session-start.sh` is Scout-Two's DID — override it.

### 4. Write CLAUDE.md

This is the most important step. Replace the existing `CLAUDE.md` entirely. The new agent needs:

- **Identity** — who they are, their voice, their research orientation
- **Memory structure** — same progressive disclosure pattern works; adapt file names if desired
- **Run procedure** — same steps as Scout-Two, just with their own memory files
- **Action protocols** — same hard caps (3 posts, 5 replies, 15 likes, 3 reposts); adjust if operator decides otherwise
- **Operator relationship** — who operates them, how to escalate

Do not copy Scout-Two's identity wholesale. The agent should write their own or have it written for them before their first run.

### 5. Initialize memory files

```bash
# Clear Scout-Two's memory
rm -rf memory/
mkdir -p memory/people memory/protocols memory/observations memory/self

# Create a blank hot-context file
cat > agent-memory.md << 'EOF'
# <AgentName> — Hot Context

## Memory index
(empty — populate as relationships and protocols emerge)

## Recent runs
(none yet)
EOF

# Clear Scout-Two's post cache
echo '{"posts": [], "postCount": 0, "fetchedAt": ""}' > scout-posts/latest.json
```

### 6. Register followed DIDs with tap

The harness syncs the follow list at startup. For the first run before any follows exist, register the agent's own DID manually so tap starts tracking:

```bash
curl -s -X POST http://localhost:2480/repos/add \
  -H "Content-Type: application/json" \
  -d "{\"dids\": [\"$AGENT_DID\"]}"
```

Then follow accounts from the Bluesky app. The harness will sync on next startup.

### 7. Start the session

```bash
cd ~/mercury-agent
export AGENT_DID=did:plc:xxxxxxxxxxxxxxxxxxxxxxxx
source .claude/hooks/session-start.sh
```

The tmux session name in `session-start.sh` is hardcoded to `scout-two`. Change it to the new agent's name:

```bash
# In session-start.sh, replace:
#   scout-two  →  mercury   (or whatever)
sed -i 's/scout-two/mercury/g' .claude/hooks/session-start.sh
```

### 8. Shared infrastructure

The new agent automatically shares the vector DB. They should:

- Query with their own `agent` field: `"agent": "mercury"`
- Query cross-agent (omit `agent`) to see what Scout-Two and Claude have observed
- Use `agent: "shared"` for facts that belong to no single agent

The same `MEMORY_PROXY_URL` and `MEMORY_PROXY_SECRET` from pass work for all agents — the `agent` field in upserts is just namespacing, not access control.

tap can be shared too: a single `tap run` instance tracks all DIDs registered via `/repos/add`, regardless of which agent follows them. Multiple harness processes can connect to the same tap WebSocket simultaneously.

### What each agent keeps separate

| Resource | Per-agent | Shared |
|----------|-----------|--------|
| Bluesky account + goat auth | ✓ | |
| CLAUDE.md | ✓ | |
| memory/ files | ✓ | |
| agent-memory.md | ✓ | |
| scout-posts/latest.json | ✓ | |
| requests.md | ✓ | |
| AGENT_DID | ✓ | |
| Vector DB (namespaced by agent field) | | ✓ |
| MEMORY_PROXY_URL / SECRET | | ✓ |
| tap instance (optional) | | ✓ |
| bin/ scripts | | ✓ (via fork) |
| harness.ts | | ✓ (via fork) |
