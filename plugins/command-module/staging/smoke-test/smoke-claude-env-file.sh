#!/bin/bash
# Phase 0 smoke test: verify CLAUDE_ENV_FILE propagation.
#
# Reads $CLAUDE_ENV_FILE from the SessionStart hook's env, appends
# CLAUDE_SMOKE_TEST=ok to it, and writes a marker file so we know
# the hook fired.
#
# If $CLAUDE_ENV_FILE is unset OR a subsequent Bash tool call in the
# same session does not see CLAUDE_SMOKE_TEST=ok, the design premise
# of the per-session clocks plan (D1) is wrong.
#
# Wire-up + checklist: see staging/smoke-test/PHASE_0_CHECKLIST.md

set -u

MARKER="/tmp/claude-smoke-marker"
LOG="/tmp/claude-smoke.log"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] SessionStart smoke hook fired"
  echo "  CLAUDE_ENV_FILE=${CLAUDE_ENV_FILE:-<UNSET>}"
} >> "$LOG"

touch "$MARKER"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  printf 'CLAUDE_SMOKE_TEST=ok\n' >> "$CLAUDE_ENV_FILE"
  echo "  appended CLAUDE_SMOKE_TEST=ok to \$CLAUDE_ENV_FILE" >> "$LOG"
else
  echo "  WARN: CLAUDE_ENV_FILE is unset — design premise broken" >> "$LOG"
fi

exit 0
