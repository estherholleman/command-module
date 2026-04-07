# Plan and build: /handoff skill

## What to do

Run `/implementation-plan` then `/work` for the /handoff skill — generates self-contained prompts for starting fresh conversations at transition points.

## Requirements doc

Read `docs/brainstorms/2026-04-06-handoff-skill-requirements.md` for the full requirements (R1-R7).

## Key context

- This is a small, general-purpose workflow skill — not strategy-specific, used across all repos
- Output is always both: prompt file written to `docs/prompts/` AND displayed in chat
- The skill looks at the current conversation context and generates a prompt that captures: what was decided, what to do next, which files/docs to read, and relevant context
- Creates `docs/prompts/` if it doesn't exist
- Must work standalone (user invokes it directly) and be callable by other skills at their handoff phases (future integration)
- When the user chooses "continue here" instead, the skill gets out of the way

## Quality reference

Look at the manually-written prompts already in `docs/prompts/` — these are examples of what good handoff prompts look like. The skill should produce prompts of this quality: enough context for a fresh conversation to be productive immediately, with file paths to read and clear next actions.

## Existing skills to reference

- Look at the strategy toolkit skills (`concept`, `strategy`, `whats-next`) for current conventions
- Look at `/brainstorm` for how its handoff phase currently works — /handoff will eventually replace those ad-hoc handoff patterns

## Keep it simple

This is a lightweight skill. The core logic is: read the conversation context, assess what the next conversation needs to know, write a good prompt. Don't over-engineer it.
