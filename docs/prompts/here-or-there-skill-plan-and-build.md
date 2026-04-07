# Plan and build: /here-or-there skill

## What to do

Run `/implementation-plan` then `/work` for the /here-or-there skill — the transition decision point that helps decide whether to continue in the current conversation or start a fresh one.

## Requirements doc

Read `docs/brainstorms/2026-04-06-next-skill-requirements.md` for the full requirements (R1-R6). Note: the file still uses the old `/next` name in some places — the skill is called `/here-or-there`.

## Key context

- This skill depends on `/handoff` — it calls /handoff when the answer is "new conversation"
- The core value is the assessment: should we stay or go? Factors: context window usage, whether the next step requires a different role/mode, whether current conversation context helps or hinders
- When the answer is "here": proceed with the next action inline, seamlessly
- When the answer is "there": call /handoff to generate the prompt
- Works at any point in any conversation, not just at formal skill transition points

## Existing skills to reference

- `/handoff` skill (just built) — this is what /here-or-there calls for the "there" path. Check its interface
- Look at how other skills handle their transition points (brainstorm's Phase 4, implementation-plan's Phase 5.4) — /here-or-there formalizes what those do ad-hoc

## Design considerations

- The recommendation should be genuinely useful, not just always saying "new conversation." Sometimes continuing is clearly better (small follow-up, context is an asset)
- Keep the interaction minimal — one question with a recommendation, then act on the answer
- The skill should feel lightweight and helpful, not bureaucratic
