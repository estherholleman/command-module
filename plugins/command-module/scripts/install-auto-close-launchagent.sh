#!/usr/bin/env bash
# Install report-only clock checks, retiring the fixed-time closing job.
# Compatibility name retained. Never edits clocks, time records, or crontab.
# Usage: bash install-auto-close-launchagent.sh [--hook-source DIR] [--no-cron-prompt]
# Existing files are backed up. The old label is disabled; a separate report-only
# label runs at 20:00. Unknown and active sessions are preserved at every hour.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SOURCE="$SCRIPT_DIR/../staging/hooks"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hook-source) HOOK_SOURCE="$2"; shift 2 ;;
    --no-cron-prompt) shift ;; # compatibility: cron is now always read-only
    -h|--help) head -7 "$0"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
SOURCE="$HOOK_SOURCE/clock-check.py"
# Fail before touching any installed state if given the old destructive source.
test -f "$SOURCE" || { echo "Missing report-only clock-check.py" >&2; exit 1; }
grep -q '^CLOCK_CHECK_REPORT_ONLY = True$' "$SOURCE" || {
  echo "Refusing a source that is not explicitly report-only" >&2; exit 1;
}
/usr/bin/python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$SOURCE"
DOMAIN="gui/$(id -u)"
OLD="com.esther.auto-close-clock"
NEW="com.esther.clock-check"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
BACKUP="$HOME/Library/Application Support/ClockCheck/backups/$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$BACKUP" "$LAUNCH_DIR"
# Retire the known job first, while retaining its plist as a reversible backup.
launchctl disable "$DOMAIN/$OLD"
if launchctl print "$DOMAIN/$OLD" >/dev/null 2>&1; then
  launchctl bootout "$DOMAIN/$OLD"
fi
for host in .claude .codex; do
  DEST="$HOME/$host/hooks"
  mkdir -p "$DEST" "$BACKUP/$host"
  for name in auto-close-clock.py clock-check.py; do
    if [[ -f "$DEST/$name" ]]; then cp -p "$DEST/$name" "$BACKUP/$host/$name"; fi
  done
  cp "$SOURCE" "$DEST/clock-check.py"
  # Do not copy an override's auto-close script: generate the safe shim ourselves.
  cat >"$DEST/auto-close-clock.py" <<'PY'
#!/usr/bin/env python3
"""Compatibility entry point: automatic clock closure is retired."""
# CLOCK_CHECK_REPORT_ONLY: legacy callers also report without closing clocks.
import runpy
from pathlib import Path
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("clock-check.py")), run_name="__main__")
PY
done
OLD_PLIST="$LAUNCH_DIR/$OLD.plist"
if [[ -f "$OLD_PLIST" ]]; then cp -p "$OLD_PLIST" "$BACKUP/$OLD.plist"; fi
NEW_PLIST="$LAUNCH_DIR/$NEW.plist"
if [[ -f "$NEW_PLIST" ]]; then cp -p "$NEW_PLIST" "$BACKUP/$NEW.plist"; fi
# Rewrite the old plist to the safe shim too, so manually enabling it cannot
# restore the destructive program. It remains disabled and unloaded.
HOME_DIR="$HOME" NEW_PLIST="$NEW_PLIST" OLD_PLIST="$OLD_PLIST" /usr/bin/python3 - <<'PY'
import os, plistlib
from pathlib import Path
home = Path(os.environ["HOME_DIR"])
for label, key in (("com.esther.clock-check", "NEW_PLIST"), ("com.esther.auto-close-clock", "OLD_PLIST")):
    data = {"Label": label,
            "ProgramArguments": ["/usr/bin/python3", str(home / ".claude/hooks/clock-check.py")],
            "StartCalendarInterval": {"Hour": 20, "Minute": 0},
            "RunAtLoad": False,
            "EnvironmentVariables": {"PYTHONDONTWRITEBYTECODE": "1"},
            "StandardOutPath": str(home / ".claude/hooks/clock-check.log"),
            "StandardErrorPath": str(home / ".claude/hooks/clock-check.log")}
    Path(os.environ[key]).write_bytes(plistlib.dumps(data))
PY
if launchctl print "$DOMAIN/$NEW" >/dev/null 2>&1; then
  launchctl bootout "$DOMAIN/$NEW"
fi
launchctl enable "$DOMAIN/$NEW"
launchctl bootstrap "$DOMAIN" "$NEW_PLIST"
cat >"$BACKUP/README.txt" <<'TXT'
Clock-check deployment backup. Existing clocks and time records were not edited.
The previous destructive job is disabled and unloaded.
Normal /ci, /co, wrap-up and session hooks remain independent.
To stop the report schedule: launchctl disable gui/$(id -u)/com.esther.clock-check
and launchctl bootout gui/$(id -u)/com.esther.clock-check.
Restoring the old scripts/plist would restore clock deletion: review before
doing that. This backup is not an instruction to re-enable the old behavior.
TXT
echo "Installed report-only com.esther.clock-check at 20:00; old closure disabled."
echo "Backups: $BACKUP"
echo "Report: $HOME/prog/missioncontrol/reports/clock-check/latest.md"
echo "No clocks, timesheet rows, history, other launch jobs or cron entries changed."
