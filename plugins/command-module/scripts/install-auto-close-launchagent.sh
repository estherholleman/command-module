#!/usr/bin/env bash
# install-auto-close-launchagent.sh — Phase 3 deploy.
#
# Replaces the cron-scheduled 20:00 sweep with a launchd LaunchAgent that
# catches up on wake (per Apple launchd.plist(5) man page). Also installs the
# new multi-file auto-close-clock.py.
#
# Steps:
#   1. Copy plugins/command-module/staging/hooks/auto-close-clock.py
#      into ~/.claude/hooks/auto-close-clock.py.
#   2. Write ~/Library/LaunchAgents/com.esther.auto-close-clock.plist with
#      StartCalendarInterval { Hour=20, Minute=0 }, ProgramArguments pointing
#      at the python3 + the hook.
#   3. bootout the existing label (tolerant of missing), bootstrap, enable,
#      kickstart (test-fire), and print the agent state.
#   4. Prompt the user to remove the legacy cron entry (`auto-close-clock.py`).
#      Refuses to edit crontab without explicit confirmation. Leaves all other
#      cron entries (including claude-configs/sync.sh) intact.
#
# Idempotent: re-running re-installs cleanly.
#
# Usage:
#   bash install-auto-close-launchagent.sh [--hook-source <dir>] [--no-cron-prompt]
#
# Default --hook-source is the repo's plugins/command-module/staging/hooks/.
# --no-cron-prompt skips the crontab edit prompt (the legacy entry will keep
# running alongside launchd until manually removed).

set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DEFAULT_SOURCE="$( cd "$SCRIPT_DIR/../staging/hooks" && pwd )"

HOOK_SOURCE="$DEFAULT_SOURCE"
SKIP_CRON_PROMPT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hook-source) HOOK_SOURCE="$2"; shift 2 ;;
    --no-cron-prompt) SKIP_CRON_PROMPT=1; shift ;;
    -h|--help)
      sed -n 's/^# \{0,1\}//p' "$0" | head -30
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

HOOKS_DIR="$HOME/.claude/hooks"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
LABEL="com.esther.auto-close-clock"
PLIST="$LAUNCH_DIR/$LABEL.plist"
LOG="$HOOKS_DIR/auto-close.log"
HOOK_TARGET="$HOOKS_DIR/auto-close-clock.py"
PYTHON_BIN="/usr/bin/python3"
UID_NUM="$(id -u)"
DOMAIN="gui/$UID_NUM"

echo "==> Phase 3 launchd install"
echo "    hook source : $HOOK_SOURCE"
echo "    hook target : $HOOK_TARGET"
echo "    plist       : $PLIST"
echo "    label       : $LABEL"
echo

if [[ ! -f "$HOOK_SOURCE/auto-close-clock.py" ]]; then
  echo "ERROR: $HOOK_SOURCE/auto-close-clock.py not found" >&2
  exit 1
fi
if [[ ! -f "$HOOKS_DIR/_clock_shared.py" ]]; then
  echo "ERROR: $HOOKS_DIR/_clock_shared.py not deployed."
  echo "       Run plugins/command-module/scripts/install-phase2.sh first."
  echo "       Phase 3 sweep depends on Phase 2's shared module." >&2
  exit 1
fi

mkdir -p "$HOOKS_DIR" "$LAUNCH_DIR"

echo "==> Copying auto-close-clock.py"
cp "$HOOK_SOURCE/auto-close-clock.py" "$HOOK_TARGET"
chmod +x "$HOOK_TARGET"
echo "    installed $HOOK_TARGET"
echo

echo "==> Writing $PLIST"
cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON_BIN</string>
    <string>$HOOK_TARGET</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>20</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>$LOG</string>
  <key>StandardErrorPath</key>
  <string>$LOG</string>
</dict>
</plist>
PLIST
chmod 644 "$PLIST"
echo

echo "==> Loading LaunchAgent"
# bootout is tolerant of missing — discard error output but keep the line for visibility.
if launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null; then
  echo "    booted out previous instance"
else
  echo "    no previous instance to bootout (fine)"
fi
launchctl bootstrap "$DOMAIN" "$PLIST"
launchctl enable "$DOMAIN/$LABEL"
echo "    bootstrapped + enabled"
echo

echo "==> Test-firing once to verify"
launchctl kickstart "$DOMAIN/$LABEL" || true
sleep 2
echo

echo "==> Agent status"
launchctl print "$DOMAIN/$LABEL" 2>/dev/null | grep -iE "state|next firing|run on|program|stdoutpath|stderrpath" || true
echo

if [[ $SKIP_CRON_PROMPT -eq 0 ]]; then
  if crontab -l 2>/dev/null | grep -q "auto-close-clock.py"; then
    echo "==> Legacy cron entry detected:"
    crontab -l 2>/dev/null | grep "auto-close-clock.py" | sed 's/^/    /'
    echo
    echo "    Remove it now? (launchd already handles 20:00 with on-wake catch-up.)"
    echo "    Other cron entries (e.g. claude-configs/sync.sh) will be preserved."
    read -r -p "    Remove legacy auto-close-clock cron entry? [y/N] " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
      crontab -l 2>/dev/null | grep -v "auto-close-clock.py" | crontab -
      echo "    removed."
    else
      echo "    skipped — the legacy cron will continue running alongside launchd"
      echo "    (harmless but redundant; remove via 'crontab -e' when ready)."
    fi
  else
    echo "==> No legacy cron entry for auto-close-clock.py — nothing to remove."
  fi
else
  echo "==> --no-cron-prompt: skipping crontab edit step."
fi
echo

echo "==> Done."
cat <<EOF
Next steps (manual):
  1. Confirm the agent is scheduled:
       launchctl print $DOMAIN/$LABEL | grep -iE 'state|next firing'
  2. Tail the log on next 20:00 firing:
       tail -f $LOG
  3. To uninstall:
       launchctl bootout $DOMAIN/$LABEL
       rm $PLIST

System Settings note (macOS Sonoma+):
  General → Login Items & Extensions → Allow in the Background
  may silently disable LaunchAgents. If the next-firing is not honored,
  check that toggle is on for your shell / Terminal / iTerm.
EOF
