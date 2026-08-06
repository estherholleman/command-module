#!/usr/bin/env python3
"""
Idle-wrap watcher — the 30-quiet-minutes grace timer (2026-08-06).

Launched BY THE AGENT as a background Bash task when the Stop-hook gate's
self-assessment says "task likely done" (see auto-wrap-gate.py). Design:
a wrap should record a completed piece of work, but only after the user has
had a real chance to continue the conversation — so "done" arms a delayed
wrap instead of wrapping on the spot.

On launch it stamps `wrap_armed_at` on the session's clock (the arm IS this
process — if the launch fails, nothing is armed). Then it waits until the
clock shows IDLE_WRAP_MINUTES (env, default 30) of no engagement and exits.
The harness re-invokes the agent with this script's stdout, which is the
complete instruction for what to do:

  WRAP-NOW  — 30 quiet minutes passed, arm still current -> wrap-up Automatic
  ABORT     — the user continued (UserPromptSubmit clears the arm), a newer
              arm superseded this one, the burst was already wrapped, or the
              clock vanished -> do nothing, end the turn silently

The user continuing does NOT slide this timer — it cancels it (arm cleared by
idle-wrap-on-return.py on every prompt); the next turn-end re-assesses and
re-arms if the work still looks done. Fallback: if this process dies (laptop
sleep, tab closed), the armed clock is still honored by idle-wrap-on-return.py
when the user returns, and by the SessionEnd/sweep finalizers if they never do.

Usage: /usr/bin/python3 idle-wrap-watcher.py <session_id>
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

DEFAULT_IDLE_WRAP_MINUTES = 30
POLL_CAP_SECONDS = 300


def abort(reason: str) -> None:
    print(
        f"ABORT — {reason}. The armed wrap is cancelled (the user continued, a newer arm "
        "superseded this one, or the burst is already wrapped). Do NOT wrap and do NOT "
        "reply to this notification — output nothing and end the turn."
    )
    sys.exit(0)


def wrap_now_instruction(sid: str, idle_min: int, last_activity: str) -> str:
    clock_file = f"/Users/esther/prog/missioncontrol/tracking/.active-clocks/{sid}.json"
    return (
        f"WRAP-NOW — the wrap armed at task completion has matured: {idle_min} quiet minutes "
        f"since last activity ({last_activity}), and the user did not continue. Run the `wrap-up` "
        f"skill in AUTOMATIC mode for this ended burst now. Read {clock_file} FIRST, before any "
        "Bash/Edit call this turn (Read does not advance the heartbeat), so `last_activity` still "
        "marks the true burst end. Honest minutes = accrued_seconds/60 + (last_activity - start); "
        "row start = work_start (fall back to start), end = last_activity as read — never extend "
        "the row into the pause. Write the timesheet.csv row + history.jsonl session entry with a "
        "SPECIFIC title, correct session_type, and a real one-line summary (source = `auto-wrap`); "
        "update any changed tracking (index.json, task T0NN.md files, status.json); commit + push "
        "per the wrap-up skill's git step; then RESET the clock (start=null, work_start=null, "
        "last_activity=null, accrued_seconds=0, first_turn_at=null, turn_count=0, "
        "wrap_armed_at=null, wrapped_at=now — keep the file). Finish with ONLY the one-line wrap "
        "confirmation, then stop."
    )


def main() -> None:
    if len(sys.argv) < 2:
        abort("no session id given")
    sid = sys.argv[1]

    try:
        import _clock_shared as shared
    except Exception:
        abort("clock library unavailable")

    clock_path = shared.clock_path_for(sid)
    try:
        idle_min = int(os.environ.get("IDLE_WRAP_MINUTES", DEFAULT_IDLE_WRAP_MINUTES))
    except Exception:
        idle_min = DEFAULT_IDLE_WRAP_MINUTES
    idle = timedelta(minutes=idle_min)

    if not clock_path.exists():
        abort("no clock file")
    try:
        clock = json.loads(clock_path.read_text())
    except Exception:
        abort("unreadable clock")
    if shared.is_legacy(clock) or not shared.has_started(clock):
        abort("clock not started — nothing to wrap")

    # Arm: this process IS the arm. A newer watcher overwrites the stamp and
    # this one aborts on the mismatch (dedup).
    token = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    clock["wrap_armed_at"] = token
    try:
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        abort("could not stamp wrap_armed_at")

    while True:
        if not clock_path.exists():
            abort("clock file gone (session ended and was finalized)")
        try:
            clock = json.loads(clock_path.read_text())
        except Exception:
            abort("clock became unreadable")
        if clock.get("wrap_armed_at") != token:
            abort("arm cleared or superseded")
        if not shared.has_started(clock):
            abort("burst already wrapped")
        la = clock.get("last_activity") or clock.get("start")
        try:
            la_dt = datetime.fromisoformat(la)
        except Exception:
            abort("unreadable last_activity")
        now = datetime.now()
        target = la_dt + idle
        if now >= target:
            print(wrap_now_instruction(sid, idle_min, la))
            return
        time.sleep(min((target - now).total_seconds() + 1, POLL_CAP_SECONDS))


if __name__ == "__main__":
    main()
