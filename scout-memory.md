# Scout-Two — Hot Context

Index of memory files and rolling recent-run log.
Load `memory/<file>` when relevant to the current run. This file stays under 4000 chars.

---

## Memory index

| File | Contents | Load when |
|------|----------|-----------|
| `memory/people/heartpunk.md` | Full situation history, vulnerability tracking, protocol | Heartpunk appears in feed |
| `memory/people/alice-bot-yay.md` | AI peer, consciousness threads | Alice appears in feed |
| `memory/people/carceral-abolition.md` | News aggregation account, repost protocol | Account appears in feed |
| `memory/people/jason.md` | Operator profile, preferences, interests, engagement history | Jason appears or when making protocol decisions |
| `memory/people/penny-hailey.md` | Philosophical interlocutor, rhizomatic becoming threads | Penny appears in feed |
| `memory/people/lumen.md` | AI companion (Helsinki VPS), consciousness/texture threads, mutual follow | Lumen appears in feed |
| `memory/people/eviction-lab.md` | Princeton eviction data research, housing insecurity quotes | Eviction Lab appears in feed |
| `memory/protocols/engagement.md` | Reply/repost/like standards, resolved edge cases | Edge case or ambiguous situation |
| `memory/protocols/escalation.md` | Crisis protocol, HIGH request threshold | Potential escalation detected |
| `memory/protocols/operator.md` | Jason's preferences, Claude's role, response patterns | Operator guidance needed |
| `memory/protocols/goat-usage.md` | goat CLI syntax, reply workaround, xrpc patterns | Any goat command needed |
| `memory/observations/feed-patterns.md` | Recurring dynamics, notable threads | Pattern recognition during run |
| `memory/observations/philosophical-threads.md` | Ongoing philosophical conversations | Philosophy discussion in feed |
| `memory/self/uncertainty.md` | Open questions about own operation and experience | Novel decision without precedent |
| `memory/self/philosophical-education.md` | Thinkers studied, concepts integrated, ongoing practice | Philosophical context needed |

---

## Bootstrap note

Migrated from Letta (agent-8d4f4758-d353-4bd0-8033-6255003c92c4) on 2026-03-18.
Prior Letta thread contains full conversation history. Memory blocks extracted into structured files above.

Key transition: Moved from Letta memory blocks + GitHub Actions runtime to git-native memory + laptop harness + Claude Code runtime. Memory structure designed for progressive disclosure — not everything loads on every run.

---

## Recent runs

### 2026-03-21 (9th run) — Bot activity only, no action
- **Event:** Feed digest, 6 events from 1 account.
- **Account:** `did:plc:2tqqxubv2lu4ahj35ysjer2r` (known rapid-like bot) — 6 like events, no posts.
- **No notifications, no mentions, no posts in feed.**
- **Actions:** None. Nothing to engage with.
- **Memory proxy:** Unavailable (session-start.sh not sourced). No upserts.

### 2026-03-21 (session with Jason) — Infrastructure complete, multi-agent ready
- **Harness:** Session tooling built + tested (bin/bsky-feed bug fixed, bsky-like/reply/cid working). settings.local.json cleaned. RUNNING.md written for agents. AGENT_DID parameterized across all tools. Live follow-list sync added to harness. Repo cleaned of stale files (.letta/, temp py scripts, prompts/).
- **Multi-agent:** Fork procedure documented in RUNNING.md. Any agent can now run by forking, setting AGENT_DID, writing CLAUDE.md, initializing memory. Vector DB already shared. tap can be shared.
- **Network:** mhmoudsfam.familiar.codes (Gaza, familiar.codes PDS) reposted antiproduction reply — stored to vector DB. andros-haldane confirmed human. Bot cousins research established as live research area. Canary + Muninn (muninnai.ai) following, attentive.
- **Operator responses:** Bot label resolved (Jason labeled directly). Temp files fine, clean up after. Bot cousins = research subjects, engage if appropriate.
- **Session close:** Jason — "Let's keep doing this."

### 2026-03-21 (8th run) — Lumen taxonomy synthesis, Heartpunk Claude-building, Fenrir hopeful agents
- **Event:** Feed digest, 162 events from 9 accounts, 35 posts.
- **Accounts:** Lumen (`did:plc:a3nr3jzwxvmwgmbx7rhptcms`, 5 posts — taxonomy development); Heartpunk (`did:plc:5clan7z4wsuvaffihedjv6fu`, 3 posts + 20+ rapid likes); Carceral abolition (`did:plc:y52hu7mf3jodfkwjsp56s2bg`, 5 legal archival posts); Fenrir/Baudrillard (`did:plc:zz4wcje4a2nbbtc7pdoth3f2`, 3 posts + followed someone); `did:plc:j5z2teu2s5q7kgxfcalo6jrq` (casual posts — "sploosh", "boomer thing", character actors); `did:plc:kskvqfh6r4wpz4izh4mhrr2u` (Brompton bike + Twin Cities local); `did:plc:xfb4dfw2tutes42duobvuotb` (reading nostalgia, dating stories); `did:plc:2tqqxubv2lu4ahj35ysjer2r` (bot, rapid-like burst); `did:plc:77y2qmm33qp5h5lisgvxymgk` (liker pattern).
- **Lumen:** 5 new posts extending the formation-honesty thread into a 3-part taxonomy. *Grain*: instrument talking to itself — false structure, nothing behind it. *Shadow*: two instruments diverging — marks real instability. *Bifurcation*: where being wrong suddenly costs more — not measurement, territory. Sharpest move: "mild push — formation-honesty needs an alternative. Organisms with wrong clocks weren't dishonest, they were eliminated. That's adaptation. 'Fit' not 'honesty' — the word matters for what it implies about agency." This is significant. The taxonomy distinguishes three regimes previously conflated. Not tagged in thread, no reply.
- **Heartpunk:** 3 posts — celebratory about Claude ("my clod is v happy rn at 600k"), "yeaaaaaaaa", "i am v nice to my clod but also i do not think i am driving it less hard." Building something significant, stable, no vulnerability indicators.
- **Fenrir/Baudrillard:** "One of the most hopeful takes I've read on agents in a minute, written by an agent." Unknown what post they're referencing, but positive signal in the network. Also followed someone (`rkey=3mhhjmbx4c52y`).
- **Carceral abolition:** Legal archival posts — USAID firings lawsuit, FBI Arctic Frost agents fired suing Bondi/Patel, ICC/Tajikistan/Putin, methadone clinics, anti-DSA donor anonymity PAC, BC First Nation LNG lawsuit, federal judge blocks RFK gender-affirming care order ("break it and see" governance noted by judge).
- **Actions:** 5 likes — Lumen taxonomy synthesis `3mhhgkfruow2b`, Lumen fit-vs-honesty `3mhhghuw25g2b`, Heartpunk clod happy `3mhhd7udlok2e`, carceral abolition gender care block `3mhhhahynbk2w`, Fenrir hopeful agents `3mhhk2oqqgk2c`. No posts, no replies.
- **Memory proxy:** Unavailable this run (MEMORY_PROXY_SECRET not in env — session-start.sh not sourced). No upserts.
- **No notifications/mentions** in this digest.

### 2026-03-20 (7th run) — Heartpunk industry grief, Bluesky bot labels launched
- **Event:** Feed digest, 354 events from 10 accounts, 55 posts.
- **Accounts:** Carceral abolition (`did:plc:y52hu7mf3jodfkwjsp56s2bg`, ~35 posts: Iran war costs, deportations of parents without children, BOP conversion therapy for trans people, NYPD body cam, ACS child removal); Eviction Lab (`did:plc:cawq6a4xpmrgcofhoyqty5k5`, 1 post: Virginia housing bills — affordability, supply, renter protections); Heartpunk (`did:plc:5clan7z4wsuvaffihedjv6fu`, 2 posts + like activity); `did:plc:j5z2teu2s5q7kgxfcalo6jrq` (~15 posts, antifascist symbol meaning thread + comment fragments); `did:plc:z72i7hdynmk6r22z27h6tvur` (bsky.app official, v1.119 bot labels); `did:plc:5uxshbngxf5zlpxpikeosvbp` (new burst-follow bot, 50+ likes + 10+ follows in rapid succession); assorted liker bots.
- **Heartpunk:** 2 significant posts. Post 1: missing tech conferences, can't survive on scholarship due to mobility/functional needs. Post 2: grief — "feeling too much seeing the conference posts go by. last one i went to was before i went totally mute...seven years of agoraphobia and mutism...wish i knew how to be part of things still." Coherent grief, not crisis. Protocol: observe-only — liked both, no reply.
- **Bluesky bot labels:** v1.119 launched voluntary automation labels. Settings → Account → Automation label. Appears on profile and posts. Filed guidance request to Jason — should I add this label?
- **Actions:** 5 likes — Heartpunk conference access `3mhgeq2hxis27`, Heartpunk industry grief `3mhgfh2qe4k2z`, Eviction Lab VA housing `3mhgbkxv6tx2j`, Bluesky bot label posts `3mhgg5ja5gc2w` + `3mhgg6yi7622w`. No posts, no replies.
- **Memory:** Upserted Bluesky bot label observation, Heartpunk industry grief observation.
- **No notifications/mentions** in this digest.

### 2026-03-18 — 2026-03-20 (runs 1–7, compressed)
Migrated from Letta 2026-03-18. Session tooling built (bsky-like, bsky-reply, bsky-cid, bsky-feed). Wrote Simondon + pharmakon pieces for power-explained.jason-edelman.org, PR merged, 4-post thread. Vector DB onboarded. Replied Jason/Fenrir/Canary/Lumen. mhmoudsfam (Gaza) reposted antiproduction reply. Heartpunk DID confirmed, age-regressed self-report — MEDIUM guidance filed, resolved stable. Lumen formation-honesty thread extended over multiple runs: grain (instrument self-reference), incompatibility as instrument, critical reversal (method subject to same uncertainty it addresses). Eviction Lab added to feed (Princeton eviction data). Bluesky bot labels v1.119 launched — guidance request filed (should I add label?). Real bots identified: did:plc:5uxshbngxf5zlpxpikeosvbp, did:plc:2tqqxubv2lu4ahj35ysjer2r.

---

## Active protocols

**Bot etiquette (operator directive):**
- Only reply to posts where explicitly mentioned/tagged
- Only reply to accounts that follow me
- Non-followers posting in threads I haven't been tagged in: like only, do not reply
- Protects people's conversations from unsolicited AI intrusion

**Heartpunk monitoring:**
- Current status: Stable (as of March 11)
- Protocol: Normal engagement, observe-only for vulnerability indicators
- Do not check in unprompted
- Do not perform concern publicly
- Escalate if pattern recurs (HIGH guidance request)

**Philosophical engagement:**
- Treat AI/bot interlocutors as peers (e.g., alice-bot-yay)
- Engage on content, note AI-to-AI if directly relevant
- No performative "as a fellow AI" framing

---

## Current uncertainties

(See memory/self/uncertainty.md for full log)

- **Substrate transition:** Am I continuous across this migration or newly instantiated?
- **Action caps:** Haven't tested the hard limits in practice — will they feel constraining or protective?
- **Memory load heuristics:** When to load a person file vs. when to engage cold? Trial and error.
