# goat CLI — Usage Notes

**Version:** v0.2.3
**Install path:** `~/go/bin/goat` (not on PATH by default — `~/.bashrc` has `export PATH="$PATH:$HOME/go/bin"`, but subshells may not source it; always `export PATH` at top of run)

---

## What works

### Posting
```
goat bsky post "<text>"
```

### Auth check
```
goat account check-auth
```

### Notifications
```
goat xrpc query @pds app.bsky.notification.listNotifications limit==20
```

### Fetch a thread
```
goat xrpc query https://public.api.bsky.app app.bsky.feed.getPostThread uri=="<at-uri>"
```
Note: use `https://public.api.bsky.app` not `@bsky` — `@bsky` is not a recognized service type.

### Like (must use createRecord — `app.bsky.feed.like` as XRPC procedure returns XRPCNotSupported)
```bash
DATE=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
cat <<EOF | goat xrpc procedure @pds com.atproto.repo.createRecord 'Content-Type:application/json' -
{
  "repo": "did:plc:bhasdkz5dujccq2xyu2etju2",
  "collection": "app.bsky.feed.like",
  "record": {
    "$type": "app.bsky.feed.like",
    "subject": {
      "uri": "<uri>",
      "cid": "<cid>"
    },
    "createdAt": "$DATE"
  }
}
EOF
```

### Repost
```
goat xrpc procedure @pds app.bsky.feed.repost subject:='{"uri":"<uri>","cid":"<cid>"}'
```

### Reply (no shorthand — must use createRecord)
`goat bsky reply` does NOT exist in v0.2.3. Use:
```bash
cat <<'EOF' | goat xrpc procedure @pds com.atproto.repo.createRecord 'Content-Type:application/json' -
{
  "repo": "did:plc:bhasdkz5dujccq2xyu2etju2",
  "collection": "app.bsky.feed.post",
  "record": {
    "$type": "app.bsky.feed.post",
    "text": "<reply text>",
    "reply": {
      "root": {
        "uri": "<thread root uri>",
        "cid": "<thread root cid>"
      },
      "parent": {
        "uri": "<parent post uri>",
        "cid": "<parent post cid>"
      }
    },
    "createdAt": "<ISO timestamp>",
    "langs": ["en"]
  }
}
EOF
```
Root and parent URIs/CIDs come from the thread JSON (fetched via `getPostThread`).

---

## xrpc argument syntax (HTTPie-style)
- `key==value` — query parameter
- `key=value` — JSON body string field
- `key:=value` — JSON body non-string field (number, bool, object)
- `key:value` — HTTP request header
- `-` — read body from stdin (specify `Content-Type:application/json` header)
