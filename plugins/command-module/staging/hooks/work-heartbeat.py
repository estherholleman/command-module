#!/usr/bin/env python3
"""
PostToolUse hook — the honest clock-in / work heartbeat (2026-07-07).

Registered for the substantive-tool matcher (Edit|Write|Bash|NotebookEdit).
Read/Grep/Glob are deliberately excluded: opening a tab and skimming a file is
not a work session; the clock should start when the conversation DOES something.
The Stop hook also bumps `last_activity`, so a session whose last action was a
read still gets an accurate tail.

On each qualifying tool call:
  1. Ensure this session has a clock (create an ARMED one if SessionStart missed).
  2. If the clock has not STARTED yet, stamp `start` = now — this is the honest
     clock-in (first real action), NOT tab-open time.
  3. Always bump `last_activity` = now and increment `tool_count`.

Truthful duration later = last_activity - start.

Defensive by construction: PostToolUse cannot undo the tool, and must never break
a session. ANY error -> exit 0 silently. Fast path only (one small JSON read+write).

Stdin JSON: {session_id, cwd, tool_name, tool_input, tool_response, ...}
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return  # malformed stdin -> never disrupt the tool

    session_id = data.get("session_id")
    if not session_id:
        return

    try:
        import _clock_shared as shared
    except Exception:
        return

    now = datetime.now()
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
    clock_path = shared.clock_path_for(session_id)

    try:
        if clock_path.exists():
            clock = json.loads(clock_path.read_text())
        else:
            # SessionStart didn't run (or clock was cleared). Arm one now from cwd.
            cwd = data.get("cwd") or ""
            repo, cluster = shared.resolve_repo_and_cluster(cwd) if cwd else ("unknown", "unassigned")
            clock = {
                "session_id": session_id,
                "repo": repo,
                "cluster": cluster,
                "opened_at": now_iso,
                "start": None,
                "last_activity": None,
                "date": now.strftime("%Y-%m-%d"),
                "cwd": cwd,
                "source_at_start": "heartbeat-created",
                "tool_count": 0,
                "wrapped_at": None,
                "last_nudge_at": None,
            }

        was_started = shared.has_started(clock)
        # A real action is an immediate, unambiguous clock-in; the engagement
        # model also handles the idle-gap sub-span roll (non-lossy).
        shared.register_engagement(clock, now, is_tool=True)
        if not was_started:
            clock["date"] = now.strftime("%Y-%m-%d")
        tp = data.get("transcript_path")
        if tp:
            clock["transcript_path"] = tp  # enables the finalizer transcript backstop

        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        # Corrupt clock, race, permissions — never disrupt the session.
        return


if __name__ == "__main__":
    main()
