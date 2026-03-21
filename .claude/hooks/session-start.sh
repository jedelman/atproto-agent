#!/usr/bin/env bash
# .claude/hooks/session-start.sh
#
# Source before starting a Scout-Two Claude Code session:
#   source .claude/hooks/session-start.sh

set -euo pipefail
export PATH="$HOME/atproto-agent/bin:$HOME/go/bin:$PATH"

# Agent DID — set per-repo in .env or export before sourcing this script
# Default: scout-two
export AGENT_DID="${AGENT_DID:-did:plc:bhasdkz5dujccq2xyu2etju2}"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}◆ scout-two session bootstrap${NC}"
echo ""

# ---------------------------------------------------------------------------
# 1. Load secrets from pass (or fall back to existing env)
# ---------------------------------------------------------------------------

load_secret() {
  local env_var="$1"
  local pass_path="$2"
  local label="$3"

  if [[ -n "${!env_var:-}" ]]; then
    echo -e "  ${GREEN}✓${NC} ${label} (from env)"
    return 0
  fi

  if command -v pass &>/dev/null; then
    local value
    if value=$(pass show "$pass_path" 2>/dev/null); then
      export "$env_var"="$value"
      echo -e "  ${GREEN}✓${NC} ${label} (from pass)"
      return 0
    fi
  fi

  echo -e "  ${RED}✗${NC} ${label} — not found (set ${env_var} or: pass insert ${pass_path})"
  return 1
}

MISSING=0

load_secret "MEMORY_PROXY_URL"     "cloudflare/memory-proxy-url"    "Memory proxy URL"     || MISSING=$((MISSING+1))
load_secret "MEMORY_PROXY_SECRET"  "cloudflare/memory-proxy-secret" "Memory proxy secret"  || MISSING=$((MISSING+1))

echo ""

if [[ $MISSING -gt 0 ]]; then
  echo -e "${YELLOW}⚠ ${MISSING} secret(s) missing — memory features will be unavailable${NC}"
  echo ""
fi

# ---------------------------------------------------------------------------
# 2. Health check memory proxy
# ---------------------------------------------------------------------------

if [[ -n "${MEMORY_PROXY_URL:-}" ]]; then
  echo -e "${CYAN}◆ checking memory proxy...${NC}"
  if curl -sf "${MEMORY_PROXY_URL}/health" -o /dev/null 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} ${MEMORY_PROXY_URL}/health → ok"
  else
    echo -e "  ${YELLOW}⚠${NC} memory proxy unreachable at ${MEMORY_PROXY_URL}"
  fi
  echo ""
fi

# ---------------------------------------------------------------------------
# 3. Pull latest from origin
# ---------------------------------------------------------------------------

echo -e "${CYAN}◆ syncing repo...${NC}"
if git pull --quiet --ff-only origin "$(git branch --show-current)" 2>/dev/null; then
  echo -e "  ${GREEN}✓${NC} up to date"
else
  echo -e "  ${YELLOW}⚠${NC} fast-forward failed — resolve manually"
fi
echo ""

# ---------------------------------------------------------------------------
# 4. Session context summary
# ---------------------------------------------------------------------------

export SESSION_DATE="$(date -u +%Y-%m-%d)"
export SESSION_ID="$(date -u +%Y%m%dT%H%M%S)"

echo -e "${CYAN}◆ context${NC}"
echo -e "  session:        ${SESSION_ID}"

if [[ -f "feed-cursor.json" ]]; then
  SAVED_AT=$(python3 -c "import json; d=json.load(open('feed-cursor.json')); print(d.get('savedAt','unknown')[:19])" 2>/dev/null || echo "unknown")
  echo -e "  feed cursor:    ${SAVED_AT}"
fi

if [[ -f "scout-posts/latest.json" ]]; then
  POST_COUNT=$(python3 -c "import json; d=json.load(open('scout-posts/latest.json')); print(d.get('postCount',0))" 2>/dev/null || echo "?")
  FETCHED_AT=$(python3 -c "import json; d=json.load(open('scout-posts/latest.json')); print(d.get('fetchedAt','?')[:19])" 2>/dev/null || echo "?")
  echo -e "  own posts:      ${POST_COUNT} (as of ${FETCHED_AT})"
fi

if [[ -f "requests.md" ]]; then
  PENDING=$(grep -c "^\- \*\*\[" requests.md 2>/dev/null || echo "0")
  echo -e "  pending reqs:   ${PENDING}"
fi

echo ""

# ---------------------------------------------------------------------------
# 5. Ensure tap + harness are running (resumable after laptop sleep/restart)
# ---------------------------------------------------------------------------

echo -e "${CYAN}◆ checking harness...${NC}"

if curl -sf http://localhost:2480/health -o /dev/null 2>/dev/null; then
  REPO_COUNT=$(curl -s http://localhost:2480/stats/repo-count 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('repo_count','?'))" 2>/dev/null || echo "?")
  OUTBOX=$(curl -s http://localhost:2480/stats/outbox-buffer 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('outbox_buffer','?'))" 2>/dev/null || echo "?")
  echo -e "  ${GREEN}✓${NC} tap running — ${REPO_COUNT} repos tracked, outbox buffer: ${OUTBOX}"
else
  echo -e "  ${YELLOW}⚠${NC} tap not running — starting scout-two session"
  if tmux has-session -t scout-two 2>/dev/null; then
    tmux kill-session -t scout-two
  fi
  tmux new-session -d -s scout-two -n tap -c ~/atproto-agent
  tmux new-window -t scout-two -n harness -c ~/atproto-agent
  tmux send-keys -t scout-two:tap "export PATH=\"\$HOME/go/bin:\$PATH\" && ~/go/bin/tap run --log-level=warn" Enter
  tmux send-keys -t scout-two:harness "npm run harness" Enter
  sleep 2
  if curl -sf http://localhost:2480/health -o /dev/null 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} tap started"
  else
    echo -e "  ${RED}✗${NC} tap failed to start — check: tmux attach -t scout-two"
  fi
fi
echo ""

echo -e "${GREEN}◆ session ready${NC}"
echo ""
