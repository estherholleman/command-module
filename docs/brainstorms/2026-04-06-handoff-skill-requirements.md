---
date: 2026-04-06
topic: handoff-skill
---

# /handoff — Session Handoff Skill

## Problem Frame

At workflow transition points (brainstorm → plan, plan → work, strategy → concept, etc.), the user almost always prefers starting a fresh conversation rather than continuing in the current one. Today this requires manually explaining the preference each time, and then manually asking Claude to write a prompt for the next conversation. This is a repeated friction point across all repos and all workflow skills.

## Requirements

- R1. The skill assesses the current conversation context and asks whether to continue here or hand off to a new conversation
- R2. When the user chooses "new conversation," the skill generates a self-contained prompt that captures: what was decided, what to do next, which files/docs to read, and any relevant context the new conversation needs
- R3. The prompt is written to `docs/prompts/` as a markdown file (created if the directory doesn't exist) AND displayed in chat for immediate use
- R4. Prompt files are named descriptively: `<topic>-<next-action>.md` (e.g., `strategy-toolkit-plan-concept-skill.md`)
- R5. The skill works standalone — invokable at any point in any conversation, not just at skill transition points
- R6. The skill can be called by other skills at their handoff phases (future integration, not MVP)
- R7. When the user chooses "continue here," the skill gets out of the way and lets the current workflow proceed

## Success Criteria

- Eliminates the need to repeatedly explain the "new conversation" preference
- Generated prompts are good enough to start a productive new conversation without additional context-setting
- Works across any project repo, not just command-module

## Scope Boundaries

- **Not building:** Automatic integration into existing skills' handoff phases (future work)
- **Not building:** Any mechanism to actually start the new conversation — just produces the prompt

## Key Decisions

- Standalone skill first, integrate into other skills later
- Output is always both: file + display in chat
- Prompt files go in docs/prompts/ (same convention as strategy toolkit)

## Outstanding Questions

### Deferred to Planning

- [Affects R2] [Needs research] What makes a good handoff prompt? Look at the manually-written prompt in docs/prompts/strategy-toolkit-plan-concept-skill.md as a reference for what the user expects
- [Affects R6] [Technical] Interface for other skills to call /handoff — what context does it need passed to it vs. what it can infer from the conversation?

## Next Steps

-> `/implementation-plan` (can be planned alongside or after the strategy toolkit)
