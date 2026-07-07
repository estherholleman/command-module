---
name: dispatch
description: "Run the Flight Director: produce today's dispatch (brief, Launch Pad GO cards grouped into runs, court, momentum flags) from missioncontrol tracking data. Use when the user says 'dispatch', 'run the flight director', 'today's dispatch', 'stage my day', or the day needs re-aiming."
---

# /dispatch — The Flight Director

Produce today's dispatch for Esther's project portfolio and write it to `reports/dispatch/` (markdown for humans, JSON sidecar for the Launch Pad view).

## Source of truth

The full role prompt lives at `/Users/esther/prog/missioncontrol/docs/prompts/dispatch-prompt.md`. **Read it first and execute it exactly.** This skill is glue around that prompt, not a restatement -- if this file and the prompt ever disagree, the prompt wins. Design and rules: `/Users/esther/prog/missioncontrol/docs/plans/2026-07-07-dispatch-layer-design.md`.

## What the skill adds around the prompt

- **Absolute paths.** The skill may be invoked from any repo. Every read and write in the prompt resolves under `/Users/esther/prog/missioncontrol/`: `tracking/*/`, `docs/constitution.md`, `friction.md`, `reports/dispatch/`.
- **Interactive mode.** The prompt's headless note (Read/Write/Glob/Grep only, no Bash) applies to scheduled runs. Invoked as a skill, Bash is fine -- `date +%F` for today's date, `grep`/`tail` for history.jsonl filtering (never read history.jsonl whole).
- **Same-day re-run = re-aiming.** If `reports/dispatch/<today>.md` already exists, this is a re-aim, not a fresh day: read **today's** state file `reports/dispatch/<today>.state.json` (not just the previous day's), keep the ids of still-running cards stable so the dashboard's per-card state stays attached, and overwrite today's `.md` + `.json`.

## Do-not-skip checkpoints

All of these are specified in the prompt; they are the newest (v2 flight-plan) parts and the easiest to miss:

1. **The state-file read.** `reports/dispatch/<date>.state.json` -- written by the dashboard, never by you. Its maps: `fired` (card-id -> timestamp), `court` (checked court-item slugs), `done` (card-id -> `"manual"|"auto"`), `moves` (card-id -> run-id). Fired cards count against the WIP cap; done cards and checked court items are not re-listed; moves are honored when planning today's runs.
2. **The JSON sidecar with the flight-plan `runs` array.** `reports/dispatch/YYYY-MM-DD.json` per the schema in the prompt, including `runs` -- the run-of-day grouping (currently max 3 runs x 8 cards per run, max 3 court; the prompt's schema and caps win). The JSON is authoritative for the Launch Pad view; markdown and JSON must agree; `repo` and `flags[].project` must be real registry repo slugs.
3. **Card hygiene.** Every card prompt ends with the standard Finish-with line; the Translation Rule and the Both-Paths Rule apply to every card and every court item.

## Output

Write `reports/dispatch/YYYY-MM-DD.md` and `reports/dispatch/YYYY-MM-DD.json`, then show the markdown in chat. Keep the whole dispatch under a page, plain language throughout.
