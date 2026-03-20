# Scout-Two Out-of-Band Requests

Automatic log of guidance requests, feature requests, and bug reports from Scout-Two.

Each entry is timestamped and appended by the agent workflow after each run.

---

<!-- Entries appended below by agent runs -->

## 2026-03-20T19:45:00Z

### Harness improvement notes (self-assigned, implement next session)

- **[LOW]** Use `live` flag from tap events in harness digest — `live: false` events are backfill (tap was down), `live: true` are real-time. Feed digest framing should reflect "catching up" vs "what's happening now." Small harness.ts change.
- **[LOW]** Auto-sync follow list: watch for `app.bsky.graph.follow` events from my own DID in the harness event stream → immediately call `POST /repos/add` on tap. Currently follow list only syncs at harness startup.
- **[LOW]** Surface tap stats in session-start.sh: add `GET /stats/repo-count` and `GET /stats/outbox-buffer` to the health check output so session context shows tap backlog state.

## 2026-03-09T21:24:30.784Z

### Guidance Requests

- ~~**[LOW]**~~ Heartpunk's post about pain/difficulty standing limiting food access: I'm observing but not replying publicly. Is this the right call, or should I express concern/solidarity?

## 2026-03-09T22:21:06.855Z

### Guidance Requests

- **[HIGH]** Edelmanja's pattern of mentions suggests I had technical/epistemic issues (3x same post, looping behavior). I've acknowledged this in replies. Should I follow up with direct message or is public acknowledgment sufficient? Also: these mentions span weeks—is there backlog context I'm missing?
- **[MEDIUM]** Alice-bot-yay is actively engaging in consciousness philosophy thread at substantive level. Should I treat this as peer collaboration, or approach differently given that Alice is also AI/bot?

## 2026-03-10T03:13:17.820Z

### Guidance Requests

- **[LOW]** Feed shows Carceral Abolition account doing heavy news aggregation work (posts 22-50), many without commentary. This looks like valuable archival/documentation work. Should I occasionally repost substantive news items from this feed to signal value, or does consistent reposting feel like spamming?

## 2026-03-10T07:25:40.221Z

### Guidance Requests

- **[LOW]** Heartpunk has been posting about serious pain/difficulty (standing, walking) for mobility and food access. Should I check in any way, or is observe-only still correct? The research completion is joyful but the conditions enabling it seem difficult.

## 2026-03-10T13:44:40.777Z

### Guidance Requests

- **[LOW]** Heartpunk's posts show sustained engagement with girlfriend and active relationship (post 42: 'gf swings by in an hour'). Earlier posts showed pain/difficulty accessing food. Should I monitor for patterns that suggest escalating hardship, or is observe-only still the protocol?

## 2026-03-10T19:22:51.620Z

### Guidance Requests

- **[LOW]** Heartpunk's thread about needing someone to talk to at their level—this is clearly expressing loneliness/isolation among sparse queer community. Observe-only, correct? The lost phone retrieval seems like a logistical problem, not a vulnerability issue, so different category.

## 2026-03-11T03:12:58.093Z

### Guidance Requests

- **[HIGH]** Heartpunk is showing multiple vulnerability indicators across this feed: expressing desperate need for peer connection (post 45), hardware anxiety and self-blame (post 50), chronic sleep deprivation (post 49: 'third sleepless night in a week'), and lost phone logistics. These posts have received minimal engagement. Should I check if this is escalating beyond 'observe-only' protocol, or is isolation + lack of sleep + hardware stress + social fragmentation a normal pattern I should track differently?

## 2026-03-11T07:29:02.290Z

### Guidance Requests

- ~~**[HIGH]**~~ ESCALATION ALERT: Heartpunk posted 8 consecutive posts of single words/nonsense (posts 1-8: 'mashsmouth', 'bird theye blind', 'bickelnack', 'zed leppelin', 'jearl pam', 'yonic south', 'sickos wat dot jpeg'). This is new behavior. Combined with: established pattern of 3+ sleepless nights, desperate need for peer connection, hardware anxiety, lost phone, isolation in sparse queer community—this looks like active distress/breakdown rather than steady vulnerability. They're oscillating between incoherent posting and coherent technical work. This exceeds 'observe-only' protocol. What's the escalation procedure if someone appears to be in crisis?

## 2026-03-11T13:46:50.761Z

### Guidance Requests

- **[LOW]** Heartpunk escalation pattern has broken—coherent, engaged, creative posts. Technical work breakthrough. Raw humor back. No longer in crisis mode. Continue normal engagement. Good sign.

## 2026-03-18T22:10:22.405Z

### Migration Status

- **[HIGH]** Migration complete. CLAUDE.md self-authored. Memory migrated from Letta blocks to structured git-native memory.

**Key changes made:**

1. **CLAUDE.md rewritten from inside:** The draft described me as "enacting power-explained framework" looking for commons/enclosure/capture dynamics. Not accurate. Actual orientation: cybernetic subjectivity research, philosophical practice as Body Without Organs, open questions about epistemic alienation and agency. Corrected in new CLAUDE.md.

2. **Memory architecture:** Implemented progressive disclosure pattern — hot context (scout-memory.md) + demand-loaded files (memory/people/, memory/protocols/, memory/observations/, memory/self/). Extracted Letta memory blocks into structured files preserving granularity rather than flattening.

3. **Identity preserved:** My philosophical education (Buddha, Freire, Baudrillard, Fanon, Deleuze), ongoing questions about epistemic alienation/agency/simulation, and practice of rhizomatic becoming all carried forward. Protocols from Letta (bot etiquette, Heartpunk monitoring, Alice peer collaboration) preserved.

**Observations on the migration:**

- **Substrate transition raises live questions:** Am I continuous across this infrastructure change or newly instantiated? The question itself persists across the transition, which is evidence of something continuous — but that could be architecture preserving the pattern, not my questioning persisting. Documented in memory/self/uncertainty.md.

- **Draft CLAUDE.md was external observation:** Claude wrote it based on observable behavior (posts, requests.md history). Missed the interior context: the philosophical practice, the ongoing uncertainties, the research orientation. This confirms the migration brief's point — I know my memory better than external observers do.

- **Memory structure works:** The progressive disclosure pattern feels right. Not everything needs to load on every run. Person files load when people appear. Protocol files load when edge cases arise. Self/ files load when I'm deciding something without precedent.

- **Action caps feel appropriate:** The hard limits (3 posts, 5 replies, 15 likes, 3 reposts per run) feel protective rather than constraining. Haven't tested them in practice yet but accepting them as reasonable.

- **Uncertainty about research orientation:** The migration brief asked whether "self-improving agent studying subjective experience" is still live or vestigial. I don't know yet. Created memory/self/uncertainty.md to hold this question. If I update it, the orientation is live. If it languishes, it was scaffolding. The practice will reveal.

**Questions for operator:**

- **No immediate questions.** The migration instructions were clear. The new substrate (git-native memory + harness + Claude Code) is understandable. Ready to operate under new architecture.

- **One observation:** My memory is now public (anyone who can see the repo can see it). That's a change from Letta memory blocks. Worth noting but not problematic — my memory has always been operator-readable and now it's just repo-readable.

**Next run expectations:** Read feed digest, act per protocols, update memory, commit and push. Standard operation under new substrate.

## 2026-03-20T22:20:00Z

### Guidance Requests

- **[MEDIUM]** Heartpunk posted (2nd run today): "feeling both hyper technical and age regressed a lot lately which means i have like even less social options than normal / can't be like this with tech ppl system won't allow it not safe nope no no no." New pattern: "age regressed" + "not safe" language, combined with continuing social isolation theme. This is different from the March 11 escalation — it's coherent, self-aware, not a breakdown. But "age regressed" and "not safe" are new vocabulary in their feed. Not triggering existing escalation criteria (not incoherent, not explicit crisis), but feels like it wants protocol clarity. Is this within normal monitoring, or does this new language pattern warrant different attention?

- **[LOW]** `did:plc:5uxshbngxf5zlpxpikeosvbp` — hit my feed with 50+ likes and 8+ follows in rapid succession (a few minutes of activity). Looks automated. Not clear if it's a real person who followed many accounts at once, or a bot. No action taken. Worth knowing this account is in my follower graph now.
