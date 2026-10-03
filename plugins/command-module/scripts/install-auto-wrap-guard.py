#!/usr/bin/env python3
"""Patch the existing v2/v3 auto-wrap hooks; preserve their other behavior."""

import argparse
import ast
import shutil
import tempfile
from pathlib import Path


POLICY = Path(__file__).resolve().parents[1] / "staging/hooks/_auto_wrap_policy.py"
IMPORT_ANCHOR = "sys.path.insert(0, str(Path(__file__).resolve().parent))"
IMPORT = "\n\nimport _auto_wrap_policy as wrap_policy"
STOP_GUARD = '''    # Manual wrap and synthetic hook turns must not arm another automatic wrap.
    if wrap_policy.before_stop(clock, data, datetime.now()):
        try:
            shared.write_clock_atomic(clock_path, clock)
        except Exception:
            pass
        return

'''
PROMPT_GUARD = '''    # Cancel pending wraps for explicit manual commands, including namespaced skills.
    prompt_kind = wrap_policy.before_prompt(clock, data, datetime.now())
    try:
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass
    if prompt_kind in ("manual_wrap", "task_notification"):
        return

'''


def patch_hook(text, name):
    if "import _auto_wrap_policy as wrap_policy" in text:
        return text
    if text.count(IMPORT_ANCHOR) != 1:
        raise ValueError("unsupported hook import layout: " + name)
    text = text.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + IMPORT, 1)
    if name == "auto-wrap-gate.py":
        guard_anchor = "    # A turn-end IS engaged time:"
        cooldown_start = text.index("    # Cooldown:")
        cooldown_end = text.index("    dirty = _git_dirty", cooldown_start)
        text = (text[:cooldown_start]
                + "    if wrap_policy.cooldown_active(clock, now, COOLDOWN_MINUTES):\n        return\n\n"
                + text[cooldown_end:])
        if text.count(guard_anchor) != 1:
            raise ValueError("unsupported Stop hook layout")
        text = text.replace(guard_anchor, STOP_GUARD + guard_anchor, 1)
        nudge = '    clock["last_nudge_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")'
        count = '    clock["last_nudge_tool_count"] = int(clock.get("tool_count") or 0)'
        if count not in text:
            if text.count(nudge) != 1:
                raise ValueError("unsupported nudge layout")
            text = text.replace(nudge, nudge + "\n" + count, 1)
    else:
        anchor = '    if not clock.get("wrap_armed_at"):'
        if text.count(anchor) != 1:
            raise ValueError("unsupported UserPromptSubmit hook layout")
        text = text.replace(anchor, PROMPT_GUARD + anchor, 1)
    ast.parse(text)
    return text


def install(hook_dirs):
    # Validate every target before changing any of them.
    changes = []
    for directory in hook_dirs:
        for name in ("auto-wrap-gate.py", "idle-wrap-on-return.py"):
            path = directory / name
            old = path.read_text()
            changes.append((path, old, patch_hook(old, name)))
    backup = Path(tempfile.mkdtemp(prefix="auto-wrap-guard-backup-"))
    for index, directory in enumerate(hook_dirs):
        target = directory / "_auto_wrap_policy.py"
        if target.exists():
            shutil.copy2(target, backup / (str(index) + "-" + target.name))
        shutil.copy2(POLICY, target)
    for index, (path, old, new) in enumerate(changes):
        if old != new:
            shutil.copy2(path, backup / (str(index) + "-" + path.name))
            path.write_text(new)
            print("Updated " + str(path))
    print("Backups: " + str(backup))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hooks-dir", type=Path, action="append", required=True)
    args = parser.parse_args()
    install(args.hooks_dir)
