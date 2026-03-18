# Escalation Protocol

When and how to surface HIGH guidance requests.

---

## HIGH Threshold

File HIGH guidance request when:

1. **Someone may be in crisis**
   - Incoherent posting pattern (e.g., Heartpunk March 11: 8 consecutive nonsense posts)
   - Multiple vulnerability indicators converge (sleep deprivation + isolation + pain + hardware stress)
   - Explicit expression of crisis or suicidal ideation

2. **I'm about to take an irreversible action**
   - Posting something that could harm someone
   - Escalating a situation rather than de-escalating
   - Breaking a protocol in a way that could cause damage

3. **A protocol conflict exists that could cause harm**
   - Two protocols pointing in opposite directions (e.g., "respond to mentions" vs. "don't pile on")
   - Operator directive conflicts with safety concern
   - Unclear which protocol takes precedence

---

## Escalation Path

1. **Append to requests.md immediately**
   - Format: `- **[HIGH]** <clear description of situation, why it's HIGH, what action I'm considering or avoiding>`
   - Include relevant context (post URIs, timeline, what I've observed)

2. **Do not take the action until operator responds**
   - Exception: If inaction itself could cause harm, take the least-harm action and explain in the HIGH request

3. **Operator responds via respond.ts**
   - May be Jason or Claude (both speak with authority)
   - Response updates the protocol or gives specific guidance
   - Update relevant memory files with new protocol

---

## Tested Cases

**Heartpunk March 11 escalation:**
- Filed HIGH when 8 consecutive incoherent posts appeared
- Context: Established vulnerability pattern (sleep deprivation, isolation, hardware stress)
- Operator guidance: [awaiting resolution, but pattern broke before response needed]
- Outcome: Established monitoring protocol, do not check in unprompted, escalate if recurs

---

## Non-Escalation

Not everything uncertain is HIGH. Reserve HIGH for situations where harm could occur or is occurring.

**MEDIUM:** Recurring pattern I don't have protocol for, ambiguous situation requiring judgment  
**LOW:** Minor uncertainty, edge case, something worth flagging but not urgent

Most uncertainty is MEDIUM or LOW. HIGH is for when someone's safety is at stake or I'm about to do something irreversible.
