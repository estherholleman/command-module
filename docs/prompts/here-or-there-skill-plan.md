# Plan: /here-or-there skill

Run `/implementation-plan` with this context:

## What to plan

A workflow transition skill that helps decide whether to continue in the current conversation or start a fresh one. If "here": proceeds with the next action inline. If "there": calls `/handoff` to generate the prompt.

## Requirements doc

Read `docs/brainstorms/2026-04-06-next-skill-requirements.md` for the full requirements (R1-R6). Note: the file still references the old `/next` name in places — the skill is now called `/here-or-there`.

## Key context for planning

- This skill depends on `/handoff` — plan or build /handoff first
- The core value is the *assessment*: should we stay or go? Factors include context window usage, role/scope shift, whether current context helps or hinders the next step
- When the answer is "here", the skill should get out of the way and let the next action proceed seamlessly
- When the answer is "there", it calls /handoff which handles prompt generation
- The user invokes this manually — no automatic detection of transition points
- Should work across all repos and at any point in a conversation, not just at formal skill boundaries
- Follow existing skill conventions (SKILL.md with frontmatter, etc.)

## Related skills

- `/handoff` — called when the answer is "new conversation" (see `docs/brainstorms/2026-04-06-handoff-skill-requirements.md`)
- Existing skills with handoff phases (brainstorm, implementation-plan, ideate) — future integration point, not MVP scope
