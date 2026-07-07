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
