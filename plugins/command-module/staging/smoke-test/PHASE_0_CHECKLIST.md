# Phase 0 Smoke Test — CLAUDE_ENV_FILE propagation

**Why:** The per-session clocks plan (`docs/plans/2026-04-24-001-feat-per-session-clocks-reliability-plan.md`, D1) rests on this mechanism. If a SessionStart hook can append `KEY=value` to `$CLAUDE_ENV_FILE` and subsequent Bash tool calls in the same session see `$KEY` set, the design works. If not, **stop** before shipping Phase 2 and revisit D1.

**Time:** ~5 minutes.

## 1. Wire up the throwaway hook

```bash
# Copy the smoke hook into the place Claude Code runs hooks from
cp plugins/command-module/staging/smoke-test/smoke-claude-env-file.sh ~/.claude/hooks/smoke-claude-env-file.sh
chmod +x ~/.claude/hooks/smoke-claude-env-file.sh
```

Then edit `~/.claude/settings.json` to add a SessionStart entry. The exact JSON shape that Claude Code expects (matcher `startup|resume|clear|compact`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          { "type": "command", "command": "/Users/esther/.claude/hooks/smoke-claude-env-file.sh" }
        ]
      }
    ]
  }
}
```

If `hooks.SessionStart` already exists in your settings, append the matcher block to its array — do not replace.

Back up first: `cp ~/.claude/settings.json ~/.claude/settings.json.bak.$(date +%Y%m%d%H%M%S)`.

## 2. Open a fresh Claude Code conversation

Any project. The hook fires on `startup`.

## 3. In the new conversation, ask Claude to run

```bash
ls /tmp/claude-smoke-marker && cat /tmp/claude-smoke.log && echo "---" && echo "CLAUDE_SMOKE_TEST=$CLAUDE_SMOKE_TEST"
```

### Expected (PASS)

- `/tmp/claude-smoke-marker` exists (proves SessionStart fired)
- `/tmp/claude-smoke.log` shows a recent line and prints `CLAUDE_ENV_FILE=/some/path` (NOT `<UNSET>`)
- `CLAUDE_SMOKE_TEST=ok` (env var is in the Bash tool call's environment)

### Failure modes

| Symptom | Diagnosis |
|---|---|
| Marker missing | SessionStart hook didn't fire at all. Check `settings.json` syntax, hook exec bit, Claude Code's hook-error log |
| Marker present, log shows `CLAUDE_ENV_FILE=<UNSET>` | Claude Code did not provide the env var to the hook. **Design premise broken — STOP** |
| Log shows valid env file path, but `echo $CLAUDE_SMOKE_TEST` is empty | Env file written but not propagated to Bash tool calls. **Design premise broken — STOP** |
| All three lines show expected output | **PASS — proceed with Phase 2 deployment** |

## 4. Tear down

```bash
rm ~/.claude/hooks/smoke-claude-env-file.sh
rm /tmp/claude-smoke-marker /tmp/claude-smoke.log
```

Edit `~/.claude/settings.json` to remove the matcher block you added (restore from backup if easier).

## 5. Record result

Reply pass/fail in the Phase 2 PR. PASS unblocks Phase 2 deployment; FAIL means the plan needs to revisit D1 (alternatives are worse — see plan's "Rejected alternatives" table).
