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
| `auto-wrap-gate.py` | Stop | Gate + nudge the agent to auto-wrap at completion |
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
]
```

## Tunables (top of the scripts)

- `IDLE_GAP_SECONDS` (`_clock_shared.py`) = 1800 — gap that resets a span.
- `FLOOR_MINUTES` (4), `COOLDOWN_MINUTES` (12), `MEANINGFUL_MINUTES` (25) in `auto-wrap-gate.py`.

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
