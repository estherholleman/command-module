#!/usr/bin/env bash
# install-phase2.sh — atomic deploy of per-session clocks (Phase 2).
#
# Per the plan (D5), there is no safe intermediate state where the new
# SessionStart hook writes per-session clock files but skills still read
# the legacy single-file path. This script is the deploy surface that
# closes that window in seconds:
#
#   1. Copy session-start-clock.py, session-end-clock.py, _clock_shared.py
#      into ~/.claude/hooks/ from the staged source.
#   2. Patch ~/.claude/settings.json (Python, atomic): add SessionStart and
#      SessionEnd hook entries, remove the UserPromptSubmit auto-clock-in
#      entry. settings.json is backed up first.
#   3. Delete obsolete hooks: auto-clock-in.py, clock-reminder.sh, and the
#      /tmp/claude-clock-reminded marker.
#
# Idempotent: re-running re-copies, re-patches, and re-deletes — no harm.
#
# Usage:
#   bash install-phase2.sh [--hook-source <dir>]
#
# Default --hook-source is the repo's plugins/command-module/staging/hooks/.

set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DEFAULT_SOURCE="$( cd "$SCRIPT_DIR/../staging/hooks" && pwd )"

HOOK_SOURCE="$DEFAULT_SOURCE"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hook-source)
      HOOK_SOURCE="$2"
      shift 2
      ;;
    -h|--help)
      sed -n 's/^# \{0,1\}//p' "$0" | head -25
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

HOOKS_DIR="$HOME/.claude/hooks"
SETTINGS="$HOME/.claude/settings.json"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
BACKUP="$SETTINGS.bak.$TIMESTAMP"

REQUIRED_FILES=(session-start-clock.py session-end-clock.py _clock_shared.py)

echo "==> Phase 2 install"
echo "    hook source : $HOOK_SOURCE"
echo "    hooks target: $HOOKS_DIR"
echo "    settings    : $SETTINGS"
echo

for f in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$HOOK_SOURCE/$f" ]]; then
    echo "ERROR: required hook file missing: $HOOK_SOURCE/$f" >&2
    exit 1
  fi
done

if [[ ! -f "$SETTINGS" ]]; then
  echo "ERROR: $SETTINGS does not exist. Refusing to create one." >&2
  exit 1
fi

mkdir -p "$HOOKS_DIR"
mkdir -p "$HOME/prog/missioncontrol/tracking/.active-clocks"

echo "==> Copying hook files"
for f in "${REQUIRED_FILES[@]}"; do
  cp "$HOOK_SOURCE/$f" "$HOOKS_DIR/$f"
  chmod +x "$HOOKS_DIR/$f"
  echo "    installed $HOOKS_DIR/$f"
done
echo

echo "==> Backing up settings to $BACKUP"
cp "$SETTINGS" "$BACKUP"

echo "==> Patching settings.json"
python3 - "$SETTINGS" <<'PY'
import json
import sys

settings_path = sys.argv[1]
with open(settings_path) as f:
    settings = json.load(f)

hooks = settings.setdefault("hooks", {})

# 1. Remove UserPromptSubmit entries that point at the old auto-clock-in.py
#    or clock-reminder.sh. Preserve other UserPromptSubmit entries.
ups_entries = hooks.get("UserPromptSubmit", [])
new_ups = []
removed_legacy = 0
for entry in ups_entries:
    kept_hooks = []
    for h in entry.get("hooks", []):
        cmd = h.get("command", "")
        if "auto-clock-in.py" in cmd or "clock-reminder.sh" in cmd:
            removed_legacy += 1
            continue
        kept_hooks.append(h)
    if kept_hooks:
        new_entry = dict(entry)
        new_entry["hooks"] = kept_hooks
        new_ups.append(new_entry)
if new_ups:
    hooks["UserPromptSubmit"] = new_ups
elif "UserPromptSubmit" in hooks:
    del hooks["UserPromptSubmit"]

# 2. Add SessionStart entry (idempotent — skip if already present pointing at new hook)
session_start_cmd = "/usr/bin/python3 /Users/esther/.claude/hooks/session-start-clock.py"
session_end_cmd = "/usr/bin/python3 /Users/esther/.claude/hooks/session-end-clock.py"

def has_command(event_entries, target_cmd):
    for entry in event_entries:
        for h in entry.get("hooks", []):
            if h.get("command") == target_cmd:
                return True
    return False

ss_entries = hooks.setdefault("SessionStart", [])
if not has_command(ss_entries, session_start_cmd):
    ss_entries.append({
        "matcher": "startup|resume|clear|compact",
        "hooks": [{"type": "command", "command": session_start_cmd}],
    })
    print("  added SessionStart hook")
else:
    print("  SessionStart hook already registered")

se_entries = hooks.setdefault("SessionEnd", [])
if not has_command(se_entries, session_end_cmd):
    se_entries.append({
        "hooks": [{"type": "command", "command": session_end_cmd}],
    })
    print("  added SessionEnd hook")
else:
    print("  SessionEnd hook already registered")

print(f"  removed {removed_legacy} legacy UserPromptSubmit clock-related hook(s)")

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
PY
echo

echo "==> Deleting obsolete files (idempotent)"
for f in auto-clock-in.py clock-reminder.sh; do
  if [[ -f "$HOOKS_DIR/$f" ]]; then
    rm "$HOOKS_DIR/$f"
    echo "    removed $HOOKS_DIR/$f"
  fi
done
if [[ -f /tmp/claude-clock-reminded ]]; then
  rm /tmp/claude-clock-reminded
  echo "    removed /tmp/claude-clock-reminded"
fi
echo

echo "==> Done."
cat <<EOF
Next steps (manual):
  1. Open a fresh Claude Code conversation in any project.
  2. In that conversation, run a Bash tool call:
       echo "\$CLAUDE_SESSION_ID"
     Expect a UUID. If empty, the SessionStart hook did not propagate
     CLAUDE_ENV_FILE — see staging/smoke-test/PHASE_0_CHECKLIST.md.
  3. Run:
       ls /Users/esther/prog/missioncontrol/tracking/.active-clocks/
     Expect a file named "<that-uuid>.json".
  4. If anything looks off, restore: cp "$BACKUP" "$SETTINGS"
EOF
