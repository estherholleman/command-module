# Plan: /whats-next skill

Run `/implementation-plan` with this context:

## What to plan

The /whats-next skill — a strategic execution advisor that maps sharpened concepts to actionable tasks and prompts. This is the bridge between thinking and doing in the strategy toolkit.

## Requirements doc

Read `docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md` — focus on R20-R26 (/whats-next requirements) and R27-R30 (knowledge layer).

## Research docs

- `docs/research/2026-04-06-strategic-team-vision.md` — the Translator mode (section 2.3) is what /whats-next implements

## Key context for planning

- /whats-next takes the output of /strategy and /concept sessions and analyzes what needs to happen across deliverables
- It's opinionated: recommends what to do AND what not to do, considers multiple paths, suggests which one best serves the strategic context
- It presents a task overview for user review/approval, then delegates to the existing `/capture` skill for mechanical task creation
- It writes prompt files to `docs/prompts/` — self-contained briefs for execution conversations
- It works both as an end-phase of /strategy (invoked from within a strategy session) and standalone
- It reads `docs/strategy/context.md` for strategic context, same as /concept and /strategy

## Existing skills to reference

- `/concept` and `/strategy` skills — just built, look at them for conventions (flat naming, frontmatter, context.md loading)
- `/capture` skill — /whats-next delegates to this for task creation. Check its interface
- `/brainstorm` skill — for handoff phase and option presentation patterns

## What makes this skill different from a task list

The core value is strategic judgment, not task capture. It should:
- Explain *why* each task matters in strategic terms
- Recommend what NOT to do (some implications shouldn't be acted on yet)
- When multiple paths exist, present them with trade-offs in strategic terms
- Only after user approval does it call /capture and write prompt files
