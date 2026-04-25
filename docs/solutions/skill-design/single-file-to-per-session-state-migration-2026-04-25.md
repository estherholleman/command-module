---
title: "Single-slot to per-session state: migration pattern for parallel-conversation skills"
date: 2026-04-25
problem_type: skill_design
category: skill-design
component: state_management
root_cause: single_slot_state_for_intrinsically_parallel_workload
resolution_type: design_pattern
severity: high
tags:
  - skills
  - state-management
  - parallel-conversations
  - claude-code
  - per-session-clocks
  - migration
symptoms:
  - "Two parallel Claude conversations fight over a shared single-slot state file"
  - "Closing the conversation that opened the state still leaves the state belonging to a different conversation"
  - "User dismisses 'already running' prompts repeatedly and the state is systematically lost"
  - "There's no way to attribute output rows to the conversation that produced them"
root_cause_detail: "Claude Code conversations run in parallel — multiple terminal windows, multiple projects, multiple resumes of the same project. A skill that persists state in a single file (`.active-clock.json`) implicitly assumes one conversation at a time. The instant a second conversation opens, the assumption breaks: the second conversation either dismisses the existing state (losing the first's work) or backs off ('already running, close it first'), training the user to dismiss the prompt and lose tracking."
solution_summary: "Replace the single state file with a directory of files keyed by Claude's session_id. Identity is in the filename, not in memory. Propagate session_id to skill invocations via the `CLAUDE_ENV_FILE` mechanism: a SessionStart hook appends `KEY=VALUE` to the path provided in the hook's `$CLAUDE_ENV_FILE` env, which Claude Code then exports into subsequent Bash tool calls in the same session. On migration, **discard** the legacy single-slot state — synthetic finalization rows produce garbage durations and a permanent magic-string sentinel in the output schema."
key_insight: "If the workload is intrinsically parallel (multiple conversations doing real work simultaneously), single-slot state is a correctness bug, not a quality-of-life issue. The migration is non-negotiable. The interesting design question is *how* to propagate identity to skills that run in the same session — and `CLAUDE_ENV_FILE` is currently the cleanest answer for Claude Code (PID-walking, transcript-mtime heuristics, and CWD-marker files all have nasty failure modes)."
files_changed:
  - "plugins/command-module/staging/hooks/{session-start-clock,session-end-clock,_clock_shared}.py (Phase 2)"
  - "plugins/command-module/skills/{ci,co,wrap-up}/SKILL.md (Phase 2)"
  - "plugins/command-module/staging/hooks/auto-close-clock.py (Phase 3 — multi-file iterator)"
  - "missioncontrol/reports/timesheet.csv (Phase 1 — added session_id column)"
---

## The trigger

Two Claude Code conversations in the same project. Conversation A clocks in. Conversation B opens, sees `.active-clock.json` exists, asks "clock already running — close it?" Every. Single. Prompt. The user dismisses it (correct — they don't want to close A's clock from B). B's work is never tracked. Repeat for every parallel session. Tracking gradually decays from "mostly accurate" to "I gave up on this."

## Anatomy of the migration

### 1. Identify the identity dimension

What's the thing the state belongs to? In time-tracking, it's the conversation, not the user, repo, or terminal. The right key is whatever Claude Code calls a single conversational context. That's `session_id` — a UUID Claude Code provides in every hook payload.

### 2. Move from one file to a directory

Old:
```
~/prog/missioncontrol/tracking/.active-clock.json
```

New:
```
~/prog/missioncontrol/tracking/.active-clocks/<session_id>.json
```

The directory is the namespace; each file's lifecycle is independent. `/co` in conversation A removes A's file; B's file is untouched. The orphan sweep iterates the directory, closing each one independently.

### 3. Propagate identity to skills

The bottleneck is: how does a skill running inside a conversation know which session_id keys *its* state file?

| Mechanism | Why it loses |
|---|---|
| Read transcript-path filename | Filename contains the session_id, but transcript mtime updates only on model turns. In a freshly-opened session before the first turn, the heuristic is unreliable. Concurrent same-project sessions are also ambiguous. |
| PID / parent-process walking | Fragile across tmux, VS Code extension, remote shells. Different transports, different PID trees. |
| Marker file in CWD (`.claude-session`) | Pollutes working directories. Concurrent same-CWD sessions overwrite each other's markers. |
| Shell rc / hook env export | Bash-tool-call propagation is unreliable; export from a SessionStart hook does not naturally carry into later turns. |
| **`CLAUDE_ENV_FILE` (Claude Code's documented mechanism)** | SessionStart hook appends `CLAUDE_SESSION_ID=<id>` to the file path passed in `$CLAUDE_ENV_FILE`. Claude Code then exports those vars into every subsequent Bash tool call for the same session. Documented, supported, session-scoped, automatic re-application on resume/clear/compact. |

The choice is `CLAUDE_ENV_FILE`. The smoke test: append `CLAUDE_SMOKE_TEST=ok` from a SessionStart hook; in a Bash tool call, `echo $CLAUDE_SMOKE_TEST`. If it's `ok`, the mechanism works. If it's empty, **stop** — the design premise is broken and you need to revisit.

### 4. Migrate the legacy state once, then forget it

The legacy `.active-clock.json` should be **discarded**, not synthetically finalized:

- A synthetic CSV row with the legacy clock's stale start timestamp and `end=now` produces a garbage duration that misrepresents the user's day.
- It also adds a permanent magic-string sentinel (`session_id="legacy-migrated"` or similar) to the output schema, which downstream consumers must learn to filter out forever.
- If the legacy work mattered, the user can manually retroactively-enter it via the manual-entry path. They have ground truth on duration; the script doesn't.

The migration step lives inside the SessionStart hook itself: on every fire, check whether the legacy file exists; if so, log the payload to stderr (for archival visibility), then unlink. Tolerant of `FileNotFoundError` because two concurrent SessionStart hooks may race.

### 5. Schema-extend output for attributability

Add a `session_id` column to whatever output schema the skills write. New rows get the originating conversation's id; legacy rows get an empty string. Downstream consumers that read by column name (CSV DictReader-style) tolerate the addition cleanly. Consumers that read by column position need a one-time update.

The schema extension ships **separately** as the first phase. Doing it standalone removes one risk dimension from the per-session ship: by the time the new hooks start writing non-empty `session_id`, the schema has been live for days and known to be tolerated by all consumers.

## Atomic ship boundary

The new SessionStart hook + new skills + install script are **one atomic ship**. There's no safe intermediate state where:

- SessionStart writes per-session files but skills still read the legacy single file → every session silently loses time.
- Skills read per-session paths but SessionStart still writes the legacy file → every session reports "no clock" because the per-session file doesn't exist.

The install script is the deploy vehicle. Once code is merged, the operator runs the script and the swap happens in seconds. Between merge and script-run is the danger window — minutes, not hours.

## What to defer

The orphan-sweep refactor (multi-file iterator) can lag the atomic ship by hours-to-days without breaking anything. The unchanged sweep harmlessly finds no `.active-clock.json` and exits. Once you're confident in the atomic ship, deploy the multi-file sweep as a follow-up.

Hook versioning (moving `~/.claude/hooks/*.py` into the repo) is a *separate* deferred-cleanup item — it's a developer-experience improvement, not a correctness fix. Leave it out of the migration ship.

## Related

- `docs/solutions/integrations/cwd-relative-paths-silent-miss-in-skills-2026-04-25.md` — the absolute-path + fail-loud companion fix that the per-session migration absorbed.
- `docs/solutions/developer-experience/launchd-replaces-cron-for-sleep-aware-scheduling-2026-04-25.md` — the orphan-sweep reliability fix that ships alongside.
- `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md` — broader state-machine discipline that the per-session-file-per-session_id design enforces structurally.
