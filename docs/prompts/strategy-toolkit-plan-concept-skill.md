# Plan: /concept skill (Strategy Toolkit MVP)

Run `/implementation-plan` with this context:

## What to plan

The first skill in a three-skill strategy toolkit: `/concept` — a conceptual thinking partner that uses the reframe-react-sharpen interaction pattern.

## Requirements doc

Read `docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md` for the full requirements. Focus on R1-R14 (the /concept skill) and R27-R33 (knowledge layer and organization) for this plan.

## Research docs (read both)

- `docs/research/2026-04-06-conceptual-sparring-patterns.md` — pattern analysis from 27 real conversations, with concrete examples of the interaction pattern, anti-patterns, and Esther's thinking style
- `docs/research/2026-04-06-strategic-team-vision.md` — vision document describing four modes and design principles

## Key context for planning

- This is a skill for conceptual/strategic work, not engineering. The output is sharpened thinking + knowledge artifacts, not code or technical specs
- The skill lives in command-module (a plugin used across all repos). Project-specific domain knowledge lives in each repo under `docs/strategy/`
- The interaction pattern is fundamentally different from existing dialogue skills like /brainstorm: shorter exchanges, Claude takes positions (that may be wrong), value comes from the correction cycle, not from converging on a doc
- Look at existing skills (especially brainstorm, ideate, writing-foundations) for structural conventions, but don't force the interaction pattern into their mold
- /strategy and /whats-next will be planned separately after /concept proves the core pattern works

## Planning scope

- SKILL.md for /concept with the interaction pattern, anti-patterns, and output conventions
- Knowledge artifact template/structure
- context.md initial structure
- How the skill fits in the skills directory (naming, category)
- Any reference files needed

Do NOT plan /strategy or /whats-next yet — those come after /concept is validated.
