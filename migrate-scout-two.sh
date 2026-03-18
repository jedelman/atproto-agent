#!/usr/bin/env bash
# migrate-scout-two.sh
#
# Sends the migration brief to Scout-Two's Letta agent via the REST API.
# No npm, no node — just curl, jq, and git.
#
# Prerequisites:
#   - LETTA_API_KEY set (or passed as first arg)
#   - LETTA_BASE_URL set (defaults to https://api.letta.com)
#   - LETTA_AGENT_ID set (defaults to Scout-Two's known ID)
#   - curl and jq installed
#
# Usage:
#   ./migrate-scout-two.sh
#   LETTA_API_KEY=sk-... ./migrate-scout-two.sh
#   DRY_RUN=true ./migrate-scout-two.sh   # prints the message, doesn't send

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

LETTA_BASE_URL="${LETTA_BASE_URL:-https://api.letta.com}"
LETTA_AGENT_ID="${LETTA_AGENT_ID:-agent-8d4f4758-d353-4bd0-8033-6255003c92c4}"
LETTA_API_KEY="${LETTA_API_KEY:-${1:-}}"
DRY_RUN="${DRY_RUN:-false}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_PROMPT="${SCRIPT_DIR}/prompts/scout-two-migration.md"

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

if [[ -z "$LETTA_API_KEY" ]]; then
  echo "Error: LETTA_API_KEY is required." >&2
  echo "  Set it as an env var or pass it as the first argument." >&2
  exit 1
fi

if ! command -v curl &>/dev/null; then
  echo "Error: curl is required." >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq" >&2
  exit 1
fi

if [[ ! -f "$MIGRATION_PROMPT" ]]; then
  echo "Error: migration prompt not found at $MIGRATION_PROMPT" >&2
  echo "  Make sure you're running this from the atproto-agent repo root," >&2
  echo "  or set SCRIPT_DIR manually." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Build message
# ---------------------------------------------------------------------------

# Read the migration prompt and escape it for JSON
MESSAGE_TEXT=$(cat "$MIGRATION_PROMPT")

# jq handles all JSON escaping — no manual sed needed
PAYLOAD=$(jq -n \
  --arg text "$MESSAGE_TEXT" \
  '{
    messages: [
      {
        role: "user",
        text: $text
      }
    ],
    stream_steps: false,
    stream_tokens: false
  }')

# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

if [[ "$DRY_RUN" == "true" ]]; then
  echo "=== DRY RUN ==="
  echo "Would POST to: ${LETTA_BASE_URL}/v1/agents/${LETTA_AGENT_ID}/messages"
  echo ""
  echo "Message preview (first 500 chars):"
  echo "$MESSAGE_TEXT" | head -c 500
  echo ""
  echo "Full payload size: $(echo "$PAYLOAD" | wc -c) bytes"
  exit 0
fi

# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------

echo "Sending migration brief to Scout-Two..."
echo "  Agent: $LETTA_AGENT_ID"
echo "  Server: $LETTA_BASE_URL"
echo ""

RESPONSE=$(curl \
  --silent \
  --show-error \
  --fail-with-body \
  --request POST \
  --url "${LETTA_BASE_URL}/v1/agents/${LETTA_AGENT_ID}/messages" \
  --header "Authorization: Bearer ${LETTA_API_KEY}" \
  --header "Content-Type: application/json" \
  --data "$PAYLOAD")

CURL_EXIT=$?

if [[ $CURL_EXIT -ne 0 ]]; then
  echo "Error: curl failed with exit code $CURL_EXIT" >&2
  echo "Response: $RESPONSE" >&2
  exit $CURL_EXIT
fi

# ---------------------------------------------------------------------------
# Parse and display response
# ---------------------------------------------------------------------------

echo "=== Scout-Two's response ==="
echo ""

# Extract assistant messages (send_message tool calls contain the visible reply)
# Letta returns message_type: "tool_call_message" with function send_message
echo "$RESPONSE" | jq -r '
  .messages[]
  | select(.message_type == "tool_call_message")
  | .tool_call.arguments
  | if type == "string" then fromjson else . end
  | .message // .content // .text // empty
' 2>/dev/null || true

# Fallback: show any assistant_message content
echo "$RESPONSE" | jq -r '
  .messages[]
  | select(.message_type == "assistant_message")
  | .content // .text // empty
' 2>/dev/null || true

# Show usage stats
echo ""
echo "=== Usage ==="
echo "$RESPONSE" | jq '{
  prompt_tokens: .usage.prompt_tokens,
  completion_tokens: .usage.completion_tokens,
  total_tokens: .usage.total_tokens
}' 2>/dev/null || echo "(usage stats unavailable)"

# Save full response for inspection
RESPONSE_FILE="${SCRIPT_DIR}/migration-response-$(date -u +%Y%m%dT%H%M%S).json"
echo "$RESPONSE" > "$RESPONSE_FILE"
echo ""
echo "Full response saved to: $RESPONSE_FILE"

# ---------------------------------------------------------------------------
# Git note
# ---------------------------------------------------------------------------

echo ""
echo "Next: watch requests.md for Scout-Two's migration status entry."
echo "  git pull && cat requests.md"
