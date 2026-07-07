---
name: architect
description: "Run the System Architect: triage friction.md, stage up to 3 ranked system improvements, report a capability bulletin, and propose one deletion. Use when the user says 'architect', 'run the architect', 'architect pass', or the work-system feels heavier than it should. Roughly weekly."
---

# /architect — The System Architect

Redesign pass over Esther's Mission Control work-system. The Flight Director runs the system; the Architect redesigns it. The standing question: *why is this still manual, what is this costing, and what became possible since last time?*

## Source of truth

The full role prompt lives at `/Users/esther/prog/missioncontrol/docs/prompts/architect-prompt.md`. **Read it first and execute it exactly.** This skill is glue around that prompt, not a restatement -- if this file and the prompt ever disagree, the prompt wins. Role definition: design doc §9, `/Users/esther/prog/missioncontrol/docs/plans/2026-07-07-dispatch-layer-design.md`.

## What the skill adds around the prompt

- **Absolute paths.** The skill may be invoked from any repo. Every read and write in the prompt resolves under `/Users/esther/prog/missioncontrol/`: `friction.md`, the design doc, `reports/dispatch/`, `reports/architect/`. The permission-hotspot skim also reads `~/.claude/settings.json` and missioncontrol's `.claude/settings.json`.
- **Capability watch needs the web.** Use WebSearch/WebFetch for the Claude Code changelog and Anthropic announcements. Find the last-pass date from the newest report in `reports/architect/` (ignore non-dated audit files).
- **friction.md is the only file this skill edits besides its report.** Processed entries move to the archive section at the bottom of `friction.md`; nothing else in the repo is touched.

## Do-not-skip checkpoints

All specified in the prompt:

1. **Frictions triaged** -- every `friction.md` entry lands in exactly one bucket: fixed-now (with the fix staged), proposal, or explained-why-not-yet. Then archive the processed entries.
2. **Max 3 proposals**, ranked by Esther-minutes saved per week, each obeying the Translation Rule (the exact paste-ready prompt/command/config diff -- never "you should consider"), with honest cost.
3. **Capability bulletin** (2-5 lines) -- lead with anything that unblocks a known limitation, especially cloud-FD-enabling changes.
4. **One deletion** -- the system must shrink as well as grow.

## Output

Write `reports/architect/YYYY-MM-DD.md` and show it in chat. Plain language throughout; price uncertainty in Esther-minutes and let the number decide.
