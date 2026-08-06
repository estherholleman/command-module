# Hook deploy notes — honest clock & auto-wrap (2026-07-07)

The clock/auto-wrap mechanism is **6 scripts + 2 settings.json hook entries**. `install-phase2.sh`
deploys the Phase-2 subset; the honest-clock rewrite adds two scripts and two settings entries on
top. When redeploying, ensure all of the following are in place.

## Scripts (copy staging → `~/.claude/hooks/`, `chmod +x`)

| Script | Hook event | Role |
|---|---|---|
| `_clock_shared.py` | (shared lib) | Honest-span helpers, repo/cluster resolution, CSV/history writers |
| `session-start-clock.py` | SessionStart | **Arm** the clock (`start: null`, `opened_at` set) |
| `work-heartbeat.py` | PostToolUse `Edit\|Write\|Bash\|NotebookEdit` | **Start** the clock on first action; bump `last_activity`; idle-gap reset |
| `auto-wrap-gate.py` | Stop | Record turn engagement; on "task likely done" self-assessment, nudge the agent to ARM a delayed wrap |
| `idle-wrap-watcher.py` | (agent-launched background task) | Stamps `wrap_armed_at`; completes with WRAP-NOW after ≥ 30 quiet min, or ABORT if cancelled/superseded |
| `idle-wrap-on-return.py` | UserPromptSubmit | Cancel the arm when the user continues in time; wrap-on-return fallback when the watcher died; never wraps unarmed clocks |
| `session-end-clock.py` | SessionEnd | Honest fallback row / drain armed+legacy |
| `auto-close-clock.py` | launchd (`com.esther.auto-close-clock`) | Honest sweep backstop / drain |

## settings.json hook entries (`~/.claude/settings.json` → `"hooks"`)

Beyond the Phase-2 SessionStart/SessionEnd entries, add:

```jsonc
"PostToolUse": [
  { /* existing sync-command-module-skills.sh */ },
  { "matcher": "Edit|Write|Bash|NotebookEdit",
    "hooks": [ { "type": "command",
                 "command": "/usr/bin/python3 /Users/esther/.claude/hooks/work-heartbeat.py" } ] }
],
"Stop": [
  { "hooks": [ { "type": "command",
                 "command": "/usr/bin/python3 /Users/esther/.claude/hooks/auto-wrap-gate.py" } ] }
],
"UserPromptSubmit": [
  { "hooks": [ { "type": "command",
                 "command": "/usr/bin/python3 /Users/esther/.claude/hooks/idle-wrap-on-return.py" } ] }
]
```

## Tunables (top of the scripts)

- `IDLE_GAP_SECONDS` (`_clock_shared.py`) = 1800 — gap that resets a span.
- `FLOOR_MINUTES` (4) in `idle-wrap-on-return.py` — minimum burst worth a wrap row.
- `IDLE_WRAP_MINUTES` (env, code default 30; **set to 60** in settings.json `env` since 2026-08-06) —
  quiet minutes before an armed wrap executes. Esther's rotation between parallel conversations
  often exceeds 30 min, so 30 wrapped sessions she still meant to come back to with questions.
  Must stay ≥ 30 (`IDLE_GAP_SECONDS`), or pauses get billed into wrapped rows.

Rollback: `missioncontrol/reports/architect/2026-07-07-honest-clock-rollback.md`.

## 2026-07-09 — engagement model (turns start the clock) + transcript reconciliation

**Problem:** the clock started only on a file mutation, so design/planning/discussion/reading
sessions billed only their sparse writing bursts (a full design morning showed ~0). The idle-gap
guard also silently discarded pre-gap work on a start-reset.

**Changes (all six hooks + `_clock_shared.py`):**
- `register_engagement()` — clock starts on the first of a substantive tool OR the 2nd engaged turn
  (backdated). Non-lossy idle model: a >30-min gap seals the sub-span into `accrued_seconds` and
  opens a fresh one (idle excluded, pre-gap work preserved). New clock fields: `work_start`,
  `accrued_seconds`, `turn_count`, `first_turn_at`, `transcript_path` (all backward-compatible).
- `reconcile_from_transcript()` / `finalize_row()` — SessionEnd + sweep reconstruct engaged minutes
  from the transcript's message timestamps (unwrapped tail, `since=wrapped_at`) and take
  max(clock, transcript). Continuous backstop; does not depend on `/evening`.
- `skills/wrap-up/SKILL.md` reset step updated to clear the new fields (clock also self-heals).

**Tests:** `tests/hooks/test_engagement.py` (standalone, runs under `/usr/bin/python3`, 16/16).
**Deploy:** staging → live via `cp` to `~/.claude/hooks/` (6 files) + cleared `__pycache__`;
verified `py_compile` under `/usr/bin/python3` (3.9). Live hooks run under 3.9 — kept 3.9-safe
(normalize transcript 'Z' before `fromisoformat`).

## 2026-08-06 — idle wrap-on-return (sessions wrapped way too quickly)

**Problem:** the Stop-hook gate nudged an auto-wrap at *turn-end* — the one moment idle time is
zero by definition — so it fired while a conversation was still hot and chopped one working
session into many small wrapped rows.

**Changes:**
- New `idle-wrap-on-return.py` (UserPromptSubmit): fires only when the user RETURNS after
  ≥ `IDLE_WRAP_MINUTES` (env, default 30) of silence on a STARTED clock with ≥ 4 honest minutes.
  Injects `additionalContext` (never a block): wrap the ENDED burst first (wrap-up Automatic mode,
  read the clock before any Bash/Edit so `last_activity` still marks the burst end), then answer
  the new message in the same turn. Skips `/wrap-up` and `/co` prompts.
- `auto-wrap-gate.py` (Stop) stripped to its load-bearing core: `register_engagement` (turn-based
  clock start + tail advance + idle sub-span roll) and `transcript_path` refresh. No more nudge,
  no `decision:block`.
- `skills/wrap-up/SKILL.md` Automatic mode rewritten: trigger is the idle-return gate; wrap-first-
  then-answer replaces the self-assess/defer step (a wrap records a time segment, not task
  completion). Confirm line now continues into the user's message instead of stopping.
- Sessions that never get another prompt still finalize via SessionEnd / launchd sweep
  (`*-unwrapped`, `/evening` refines) — unchanged.

**Default 30 min, not 15:** below `IDLE_GAP_SECONDS` (30 min) a pause stays inside the open
sub-span, so a 15-min threshold would bill the pause into the wrapped row. 30 keeps the wrap
boundary aligned with the clock's own sub-span seal. Override via `IDLE_WRAP_MINUTES` env.

**Tests:** ad-hoc stdin harness (8/8: fire on 45-min gap, silent on hot/armed/tiny/wrap-prompts,
env override, Stop hook records turns silently); `test_engagement.py` still 16/16 (shared lib
untouched). **Deploy:** both scripts live in `~/.claude/hooks/` + `UserPromptSubmit` entry added
to settings.json.

### Same-day v2 — arm-don't-wrap (Esther's refinement)

Pure wrap-on-return lost two things: the turn-end *done-assessment* (which was good), and it
wrapped ANY long-gap return — but a conversation left mid-task for an hour and then continued must
never wrap. v2 splits the mechanism:

- `auto-wrap-gate.py` (Stop) got its gates + nudge back, but the "done" outcome now ARMS instead
  of wrapping: the agent launches `idle-wrap-watcher.py <sid>` (Bash, `run_in_background: true`),
  says *"✅ task likely done — will wrap after ~30 quiet minutes; keep going if you're not done."*,
  and stops. New gate: skip when `wrap_armed_at` is already set. Mid-task defer line unchanged.
- NEW `idle-wrap-watcher.py`: stamps `wrap_armed_at` (the arm IS the watcher — failed launch = no
  arm), polls the clock (≤ 5-min sleeps), completes with **WRAP-NOW** (full Automatic-mode
  instruction on stdout — the harness re-invokes the agent with it) after `IDLE_WRAP_MINUTES` of
  no engagement, or **ABORT** (output nothing) when the stamp is cleared/superseded or the burst
  already wrapped. Cancellation is detected on the next poll — it only needs to beat the wrap.
- `idle-wrap-on-return.py` (UserPromptSubmit) is now the arm's guardian: every prompt on an armed
  clock consumes the arm — early return (< threshold) cancels silently; late return injects the
  wrap (watcher-died fallback, e.g. laptop sleep froze the timer). **Unarmed clocks are never
  wrapped on return.**
- settings.json: allowlist entry `Bash(/usr/bin/python3 …/idle-wrap-watcher.py *)` so arming never
  prompts. New clock field: `wrap_armed_at` (cleared by every wrap reset).
- `skills/wrap-up/SKILL.md` Automatic mode rewritten around the two-stage flow (WRAP-NOW → confirm
  and stop; return fallback → wrap first, then answer).

**Tests:** 11/11 (gate arms/skips-when-armed/defers-on-continuation/respects floor+artifacts;
watcher stamps+WRAP-NOW, aborts on cancel/wrapped; return hook: unarmed long gap silent, early
return cancels, late return wraps, /wrap-up skip). `test_engagement.py` still 16/16.
