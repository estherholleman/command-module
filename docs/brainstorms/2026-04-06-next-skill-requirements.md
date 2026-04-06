---
date: 2026-04-06
topic: here-or-there-skill
---

# /here-or-there — Workflow Transition Decision Point

## Problem Frame

At transition points between workflow phases, the user has to manually assess whether the next step fits in the current conversation or needs a fresh one, then explain that decision and act on it. This happens frequently across all repos and workflow skills. The assessment itself is predictable — it depends on context window usage, how much the role/scope changes, and whether the current conversation's context helps or hinders the next step.

## Requirements

- R1. Assesses the current state: what just finished (or is in progress), what the natural next step is, and whether continuing in this conversation or starting fresh makes more sense
- R2. Factors in: how much context window has been used, whether the next step requires a different role/mode, whether the current conversation context is an asset or liability for the next step
- R3. Presents the assessment to the user with a recommendation and asks: continue here or new conversation?
- R4. If "continue here": proceeds with the next skill/action inline in the current conversation
- R5. If "new conversation": invokes `/handoff` to generate the prompt file and display it
- R6. Works at any point in a conversation, not just at formal skill transition points — the user might invoke it mid-conversation when they sense a natural break

## Success Criteria

- The user never has to manually explain the "should I continue or start fresh?" question — just types `/here-or-there`
- Recommendations are sensible: correctly identifies when a fresh conversation would be more productive
- The inline-continue path works seamlessly (next skill starts without ceremony)

## Scope Boundaries

- **Not building:** The prompt generation — that's /handoff's job
- **Not building:** Automatic detection of transition points — the user invokes /here-or-there when they're ready

## Key Decisions

- Two skills: /here-or-there (decision + routing) and /handoff (prompt generation). /handoff is reusable by other skills and agents directly
- /here-or-there calls /handoff when the answer is "new conversation"

## Outstanding Questions

### Deferred to Planning

- [Affects R2] [Needs research] What heuristics work best for the continue-vs-fresh recommendation? Context window percentage, role shift magnitude, scope overlap — what signals matter most?
- [Affects R4] [Technical] How does /here-or-there invoke the "next skill" inline? It needs to know what skill to call — inferred from context, or explicitly passed?

## Next Steps

-> `/implementation-plan` (plan alongside /handoff)
