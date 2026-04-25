---
title: Manual test checklist — per-session clocks
type: test-checklist
status: active
date: 2026-04-25
plan: docs/plans/2026-04-24-001-feat-per-session-clocks-reliability-plan.md
---

# Per-session clocks — manual test checklist

Human-run checklist that exercises the success criteria the test suite cannot. Run **after Phase 2 deploys** for steps 1–9, 12, 13, and **after Phase 3 deploys** for steps 10, 11.

Treat this as the acceptance gate. If any step fails, do not proceed to the next deploy.

## Pre-flight

- [ ] **Phase 0 smoke test passed** (see `plugins/command-module/staging/smoke-test/PHASE_0_CHECKLIST.md`).
- [ ] PR #3 (Phase 1 — CSV schema) merged.
- [ ] PR #4 (Phase 2 — hooks + skills + install) merged.
- [ ] `bash plugins/command-module/scripts/install-phase2.sh` executed cleanly.
- [ ] `~/.claude/settings.json.bak.*` exists (rollback artifact).

## Phase 2 acceptance

### 1. Pre-deploy baseline (record before install)
```bash
ls -la /Users/esther/prog/missioncontrol/tracking/.active-clock* 2>/dev/null || echo "no legacy clock"
ls /Users/esther/prog/missioncontrol/tracking/.active-clocks/ 2>/dev/null || echo "no per-session dir yet"
```
Record output. Expected after install-phase2.sh: `.active-clocks/` directory exists, `.active-clock.json` may still exist (gets discarded on first SessionStart).

### 2. Fresh conversation
Open a new Claude Code conversation in any project under `~/prog`.
- [ ] `ls /Users/esther/prog/missioncontrol/tracking/.active-clocks/` shows `<this-session-uuid>.json`.
- [ ] `.active-clock.json` no longer exists (discarded by SessionStart's lazy migration).
- [ ] Stderr of the SessionStart hook (visible in Claude Code's hook-error pane on failure, or via `~/.claude/hooks/*.log` if you enable file logging) shows the discarded legacy payload.

### 3. Env var propagation
In the same conversation, ask Claude to run a Bash tool call:
```bash
echo "$CLAUDE_SESSION_ID"
```
- [ ] Returns a UUID matching the filename in `.active-clocks/`.

### 4. Parallel start
Open a second Claude Code conversation in the same repo.
- [ ] `ls .active-clocks/` shows two distinct files.
- [ ] Each conversation's `$CLAUDE_SESSION_ID` matches its own file.

### 5. Independent /co
In conversation 1, run `/co`. Confirm session_type/title/details and let it write the row.
- [ ] Conversation 1's clock file is deleted.
- [ ] Conversation 2's clock file is untouched.
- [ ] Tail of `timesheet.csv`: row's 11th field (session_id) matches conversation 1's session id; source is `clock`.

### 6. Wrap-up isolation
In conversation 2, run `/wrap-up`.
- [ ] Step 1.5 surfaces only conversation 2's clock — no cross-talk.

### 7. /clear preservation
In a third conversation, run `/clear`.
- [ ] Clock file unchanged.
- [ ] No new CSV row.
- [ ] After `/clear`, SessionStart re-fires with `source=clear` and the existing clock is treated as already-running (idempotent message).

### 8. SessionEnd finalize
In a fourth conversation, exit via `/exit` or close the terminal.
- [ ] CSV row appended with `source=auto-session-end`, session_id matching that conversation.
- [ ] Clock file deleted.

### 9. Silent-miss regression check
In any conversation, run a Bash tool call: `unset CLAUDE_SESSION_ID && /co`. (Or simulate by passing an empty env var to the relevant Bash invocation.)
- [ ] `/co` fails loud with an error naming `CLAUDE_SESSION_ID` and the expected absolute path. **No silent "no clock" response.**

## Phase 3 acceptance

### 10. Orphan sweep — stale day
Manually create a synthetic stale clock and run the sweep:
```bash
cat > /Users/esther/prog/missioncontrol/tracking/.active-clocks/test-stale.json <<'EOF'
{"session_id":"test-stale","repo":"missioncontrol","cluster":"meta","start":"$(date -v-1d +%Y-%m-%d)T14:00:00","date":"$(date -v-1d +%Y-%m-%d)","cwd":"/tmp","source_at_start":"manual"}
EOF
python3 ~/.claude/hooks/auto-close-clock.py
```
- [ ] CSV row written with `source=auto-close-stale`, session_id=`test-stale`.
- [ ] Clock file deleted.

### 11. launchd scheduling
```bash
launchctl print gui/$(id -u)/com.esther.auto-close-clock | grep -iE 'state|next firing|run on'
```
- [ ] `state = running` or `scheduled`.
- [ ] Next-firing timestamp is today's 20:00 (or tomorrow's, if it's already past 20:00).
- [ ] `crontab -l | grep auto-close-clock.py` returns nothing (or, if user declined removal, output explicitly notes the duplicate is still scheduled).

### 12. Cluster-unassigned prompt
Manually craft a clock with an unmapped cwd to trigger the unassigned cluster path:
```bash
sid=$(uuidgen)
cat > /Users/esther/prog/missioncontrol/tracking/.active-clocks/$sid.json <<EOF
{"session_id":"$sid","repo":"unmapped","cluster":"unassigned","start":"$(date +%Y-%m-%dT%H:%M:%S)","date":"$(date +%Y-%m-%d)","cwd":"/tmp/unmapped","source_at_start":"manual"}
EOF
echo "Now in a Claude conversation with CLAUDE_SESSION_ID=$sid set, run /co"
```
- [ ] `/co` prompts for cluster choice (AskUserQuestion / numbered options).
- [ ] Chosen cluster appears in the CSV row.

### 13. On-wake catch-up (optional, harder to verify)
If you want to confirm the on-wake catch-up empirically: write a stale clock, sleep the Mac before 20:00, wake after 20:00. Should fire on wake.

## Sign-off

- [ ] All Phase 2 steps pass.
- [ ] All Phase 3 steps pass.
- [ ] T015 marked `done` in missioncontrol tracking.

If any step fails, document the symptom and rollback per Phase 2's PR #4 description (restore `~/.claude/settings.json.bak.*`).
