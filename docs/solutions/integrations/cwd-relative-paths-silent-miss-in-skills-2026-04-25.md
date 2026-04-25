---
title: "CWD-relative paths in skills cause silent misses across project boundaries"
date: 2026-04-25
problem_type: integrations
category: integrations
component: skills
root_cause: relative_path_resolves_against_conversation_cwd
resolution_type: design_pattern
severity: high
tags:
  - skills
  - claude-code
  - file-paths
  - silent-miss
  - per-session-clocks
symptoms:
  - "Skill responds 'no active clock' even though the state file exists at the absolute path"
  - "Skill works in one repo but silently fails in another"
  - "Action that depends on a shared state file silently no-ops when the conversation's CWD is not the expected one"
root_cause_detail: "Relative paths in SKILL.md prose (e.g., `missioncontrol/tracking/.active-clock.json`) are interpreted by the agent as paths relative to the conversation's current working directory, not the location the skill was authored against. When a user invokes the skill from a different repo, the read resolves to a path that doesn't exist — and most skills treat 'file not found' as 'state not present', responding with a benign-looking 'nothing to do' message. The user sees no error, the state file remains, and the work the skill should have done is lost."
solution_summary: "Use absolute paths in skill prose for any cross-repo state. Pair with fail-loud assertions: when the absolute path doesn't exist, name the path and the variables that should have set it, and stop. Never treat a missing file at a CWD-relative path as 'no state' — that's the silent-miss bug."
key_insight: "A skill is not a script run from a fixed directory. It is text the agent interprets each turn from whatever CWD the user happens to be in. Any relative path in the prose is a CWD bug waiting to happen. The fix is structural: bake the absolute path into the skill, and surface every missing-file case as an explicit error."
files_changed:
  - "plugins/command-module/skills/{ci,co,wrap-up}/SKILL.md (Phase 2 rewrite — absolute paths + preamble assertions)"
---

## The bug

`/co` reports "no active clock" when called from `~/prog/portfoliostrategyframework`, even though `~/prog/missioncontrol/tracking/.active-clock.json` clearly exists. The `co` skill's Step 1 instructed the agent to read `missioncontrol/tracking/.active-clock.json` — a relative path. The agent dutifully reads `~/prog/portfoliostrategyframework/missioncontrol/tracking/.active-clock.json`, which doesn't exist, and falls into the "no clock" branch.

The user observes: nothing. No error. The clock keeps running. Work is unrecorded. The next 20:00 cron sweep finds the still-running clock and either auto-closes it (correct) or — if the Mac is asleep — silently skips and stale-clock-cascades into tomorrow.

## Why it's hard to spot

- The skill works in `~/prog/missioncontrol`. So it's "tested" — just not in every CWD.
- The fail mode looks like normal "nothing to do." Skills that handle empty state gracefully are good practice; the trap is when *missing* state and *empty* state are the same response.
- Logs don't help. The agent reads the relative path through its normal Read tool. There's no syscall warning, no stderr line.
- Reproducing requires switching projects mid-session, which doesn't happen in unit tests.

## The fix is structural

**1. Absolute paths in skill prose.**

Wrong:
```
Read `missioncontrol/tracking/.active-clock.json`.
```

Right:
```
Read `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json`.
```

Hardcoding the user's home isn't ideal portability — but for personal-tracking skills with one user, the absolute path is the simplest correctness guarantee. For multi-user skills, derive `$HOME` and parameterize.

**2. Fail loud on missing state.**

Wrong (silent-miss-prone):
```
If the file doesn't exist: tell the user "no active clock" and stop.
```

Right:
```
If the file at /Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json
doesn't exist: tell the user *verbatim* "No clock file at <that absolute path> for this
session. Either it was already closed by /co, finalized by SessionEnd, or the SessionStart
hook never wrote one." Then stop.
```

The verbatim error names the path the user can `ls` themselves, making the disambiguation between "no work to do" and "lookup misfire" trivial.

**3. Preamble assertions on prerequisite vars.**

If the skill depends on an env var that another component sets (like `$CLAUDE_SESSION_ID` from a SessionStart hook), assert it before the work:

```bash
test -n "$CLAUDE_SESSION_ID" || { echo "ERROR: CLAUDE_SESSION_ID empty. SessionStart hook did not set it. Aborting."; exit 1; }
```

This separates "the hook didn't fire" from "no state to act on" — two completely different operational situations the user needs to debug differently.

## Counter-pattern: when relative paths are fine

- The skill is conceptually scoped to a single repo (e.g., a `git-commit` skill operates on the current repo, and "relative to the current repo root" is the *correct* semantic).
- The skill never crosses repo boundaries.
- The skill doesn't read shared cross-project state.

If any of those don't hold, the path should be absolute or derived from a fixed anchor.

## Detection

Quick grep for skills at risk:

```bash
grep -rE '`(missioncontrol|tracking|reports)/' plugins/command-module/skills/ | grep -v '^Binary'
```

Any backtick path that starts with a non-absolute segment naming a shared resource is a candidate for review.

## Related

- `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md` — the broader principle: skills are state machines that re-read live state at every decision boundary.
- The 2026-04-23 → 2026-04-24 stale-clock cascade in `portfoliostrategyframework` is the canonical incident reproduction.
