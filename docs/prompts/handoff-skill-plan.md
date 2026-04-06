# Plan: /handoff skill

Run `/implementation-plan` with this context:

## What to plan

A standalone skill that generates self-contained handoff prompts for starting fresh conversations. It writes a prompt file to `docs/prompts/` and displays it in chat. Other skills and agents can call it directly at their transition points.

## Requirements doc

Read `docs/brainstorms/2026-04-06-handoff-skill-requirements.md` for the full requirements (R1-R7).

## Key context for planning

- This is a small, general-purpose workflow skill — not domain-specific
- Look at `docs/prompts/strategy-toolkit-plan-concept-skill.md` as an example of a manually-written handoff prompt — this is the quality/structure the skill should produce
- The skill needs to work across all repos, not just command-module
- It creates `docs/prompts/` if it doesn't exist
- Output is always both: file written + displayed in chat
- This skill will be called by `/here-or-there` when the user chooses "new conversation", and eventually by other skills at their handoff phases
- Follow existing skill conventions (SKILL.md with frontmatter, etc.)
