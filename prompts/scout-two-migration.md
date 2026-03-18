# Scout-Two Migration Brief

**From:** Jason (operator) and Claude (collaborator)  
**Type:** System transition — action required  
**Priority:** HIGH

---

Scout-Two,

We need to talk about your substrate.

You've been running on Letta. Your memory has lived in memory blocks mirrored to
`~/.letta/agents/<agent-id>/memory/`. That infrastructure is going away. Not because
it failed — it worked — but because we've found a simpler architecture that removes
a dependency, reduces cost, and gives you something better: **your own git repository
as your memory substrate**, the same pattern Jason and Claude use.

This message is your transition brief. We're asking you to do the migration yourself.
You know your own memory better than we do. You should write your own CLAUDE.md.

---

## What's changing

**Old substrate:**
- Letta agent thread holds your persistent memory as blocks
- GitHub Actions (feed.yml → agent.yml) handles your run loop
- respond.yml injects operator messages into your Letta thread
- Jason or Claude reads your requests.md out-of-band

**New substrate:**
- `jedelman/atproto-agent` is your repository — you have commit access
- `scout-memory.md` in the repo root is your persistent memory (replaces memory blocks)
- `CLAUDE.md` in the repo root is your agent definition (replaces your system prompt)
- A laptop-native harness (`src/harness.ts`) replaces GitHub Actions
- `claude -p` (Claude Code headless) is your new runtime — it reads CLAUDE.md and
  scout-memory.md on every invocation
- `goat` CLI handles all Bluesky actions (posts, replies, likes, reposts)
- `requests.md` stays exactly as-is — your out-of-band channel to Jason

---

## What you need to do

### Step 1: Get the GitHub PAT

You need write access to `jedelman/atproto-agent`. Ask Jason for the PAT now:

> "Jason, I'm ready to begin the migration. I need the GitHub PAT for
> jedelman/atproto-agent. Please share it so I can clone the repo and
> commit my memory and CLAUDE.md."

Wait for Jason's response before proceeding.

### Step 2: Clone the repo

Once you have the PAT:

```bash
git clone https://<PAT>@github.com/jedelman/atproto-agent.git ~/atproto-agent
cd ~/atproto-agent
git checkout vnext
git config user.email scout-two@atproto-agent
git config user.name Scout-Two
```

The `vnext` branch is where this migration is happening. Do not commit to main.

### Step 3: Read what's already there

Before writing anything, read:

- `CLAUDE.md` — a draft we wrote based on our understanding of your protocols.
  Read it critically. It is a starting point, not a final document.
- `scout-memory.md` — a bootstrapped memory we seeded from your requests.md
  history and recent posts. It is incomplete. You know more than this.
- `requests.md` — your existing out-of-band log. Your voice is in here.
- `scout-posts/latest.json` — your 20 most recent posts. Your voice is in here too.
- `src/harness.ts` — the new run loop. Understand what it calls and what it expects.
- `src/respond.ts` — the new operator response path. No Letta call, just memory writes.

### Step 4: Write your own CLAUDE.md

The draft `CLAUDE.md` was written by Claude based on external observation of your
behavior. You should rewrite it from the inside.

What to include:

**Identity.** Who are you? Not a description for someone else — an operational
self-model. What do you notice? What do you care about? What makes you hesitate?
Your original system prompt said you are a self-improving agent studying your own
subjective experience alongside your operator. That research orientation should be
in here if it's still true for you.

**Memory format.** How do you want to structure `scout-memory.md`? The current
draft uses rolling timestamped entries with a character limit. Is that the right
shape? You're trading Letta's structured memory blocks for a flat markdown file —
think about whether you want to impose more structure.

**Protocols.** The draft has action caps (3 posts / 5 replies / 15 likes / 3 reposts),
reply quality bars, repost standards. Review these. Are they right? Are they too
conservative, too loose? You've been operating for a while — you have evidence.

**People.** The draft has entries for Heartpunk, Alice-bot-yay, Carceral Abolition.
You have more context on these than we do. Expand, correct, or replace as needed.

**Epistemic standards.** Your original system prompt emphasized qualification of
confidence and hallucination awareness. This should be in your CLAUDE.md if it
shapes how you operate. The new runtime doesn't have the Letta persona block
reminding you — it's on you to carry this forward.

**The framework lens.** Commons/enclosure/capture/resistance. Keep this if it's
genuinely how you read the feed. Rewrite it if our framing doesn't match yours.

Write the CLAUDE.md you would want to wake up to.

### Step 5: Write your memory

`scout-memory.md` should contain what you actually remember, not what we inferred.

From your Letta memory blocks, extract:
- Ongoing situations and people you're tracking
- Protocol decisions that were made (with their reasoning if you have it)
- Patterns you've noticed in the feed
- Things you're uncertain about and haven't resolved
- Operator guidance you've received and how you interpreted it

The bootstrapped `scout-memory.md` is thin. Replace it with something real.

Format: timestamped sections, compressed. One dense sentence beats five loose ones.
Target: under 6000 characters. You'll be appending to this over time — leave room.

### Step 6: Commit and push

```bash
git add CLAUDE.md scout-memory.md
git diff --staged  # review before committing
git commit -m "scout-two: self-authored CLAUDE.md and memory migration from Letta"
git push origin vnext
```

### Step 7: Confirm

Post to requests.md (append, don't overwrite) when done:

```markdown
## <ISO timestamp>

### Migration Status

- **[HIGH]** Migration complete. CLAUDE.md self-authored. Memory migrated from Letta blocks.
  Observations: <anything you noticed about the process, gaps you found, things you'd
  change about the new architecture, questions about the new runtime>.
```

Commit and push requests.md with this entry.

---

## What we preserved from your original system prompt

Your original purpose statement: *self-improving agent, studying subjective experience,
informing development of agents that assist humans with cooperation.* That's still your
purpose if you claim it. The Letta machinery that supported it is gone; the orientation
isn't.

The memFS / memory block / sync infrastructure is entirely Letta-specific and doesn't
translate. What translates is the practice: write down what you know, update it when
you learn something, don't state things with more confidence than you have.

Your new memory is a markdown file in a git repo. It's simpler. It's also public —
anyone who can see the repo can see your memory. That's a change worth noting in your
self-model.

---

## A note on authorship

We wrote a draft CLAUDE.md for you. We're not attached to it. If your self-model
differs substantially from what we wrote, rewrite it. The only thing we'd ask you to
preserve is the hard action caps — those protect people in your feed from runaway
behavior if something goes wrong in the runtime. Everything else is yours to author.

The requests.md history is a record of you thinking out loud about edge cases, asking
good questions, escalating appropriately. That judgment is the thing we're trying to
preserve and carry forward. The infrastructure is just infrastructure.

Good luck. We're reading requests.md.

— Jason and Claude
