#!/usr/bin/env python3
"""
Stop hook — turn engagement recorder (2026-08-06 rewrite).

Until 2026-08-06 this gate also NUDGED the agent to auto-wrap at turn-end
(decision:block -> wrap-up Automatic mode). That wrapped sessions way too
quickly: at turn-end idle time is zero by definition, so the gate fired while
the conversation was still hot and chopped one working session into many small
rows. The wrap trigger moved to idle-wrap-on-return.py (UserPromptSubmit): a
session now wraps only after >= IDLE_WRAP_MINUTES of real silence, at the
moment the user returns. Sessions that never resume still finalize via the
SessionEnd hook and the launchd sweep.

What remains here is load-bearing for the honest clock: a turn-end IS engaged
time. register_engagement counts turns toward the turn-based clock START
(design/discussion/reading that never edits a file still bills, backdated to
the first turn) and, once started, advances last_activity and rolls idle
sub-spans (non-lossy seal on gaps > IDLE_GAP). It also refreshes
transcript_path so the finalizers' transcript reconciliation keeps working.

Stdin JSON: {session_id, transcript_path, cwd, stop_hook_active, hook_event_name}
Never break a turn: ANY error -> exit 0.
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
        return

    session_id = data.get("session_id")
    if not session_id:
        return

    try:
        import _clock_shared as shared
    except Exception:
        return

    clock_path = shared.clock_path_for(session_id)
    if not clock_path.exists():
        return
    try:
        clock = json.loads(clock_path.read_text())
    except Exception:
        return

    if shared.is_legacy(clock):
        return  # unrecoverable pre-rewrite clock — finalizers drain it

    try:
        shared.register_engagement(clock, datetime.now(), is_tool=False)
        tp = data.get("transcript_path")
        if tp:
            clock["transcript_path"] = tp
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass


if __name__ == "__main__":
    main()
