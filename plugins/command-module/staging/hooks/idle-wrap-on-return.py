#!/usr/bin/env python3
"""
UserPromptSubmit hook — armed-wrap guardian (2026-08-06 v2).

Runs on every user prompt. Only ARMED clocks are in scope: `wrap_armed_at` is
stamped by idle-wrap-watcher.py when the turn-end self-assessment said "task
likely done" (see auto-wrap-gate.py). An unarmed clock is a conversation whose
work was NOT assessed complete — the user stepping away for two hours mid-task
and then continuing must never trigger a wrap, so this hook stays silent there.

For an armed clock, the user's return decides the arm's fate:
  - returned within IDLE_WRAP_MINUTES  -> the user continued: CLEAR the arm
    (the running watcher sees the cleared stamp and aborts); the next turn-end
    re-assesses and re-arms if the work still looks done.
  - returned after >= IDLE_WRAP_MINUTES -> the grace window passed but the
    watcher evidently never fired (laptop slept, process died): CLEAR the arm
    (kills any zombie watcher) and inject the wrap instruction — wrap the
    ended burst first, then answer the new message in the same turn.

Sessions that never get another prompt AND lose their watcher still finalize
honestly via the SessionEnd hook or the launchd sweep (source=*-unwrapped).

Threshold: env IDLE_WRAP_MINUTES, default 30 — keep aligned with
IDLE_GAP_SECONDS (below it, the pause itself is billed into the row).

Stdin JSON: {session_id, transcript_path, cwd, prompt, hook_event_name}
Never break a turn: ANY error -> exit 0.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

DEFAULT_IDLE_WRAP_MINUTES = 30
SKIP_PROMPT_PREFIXES = ("/wrap-up", "/co")


def _instruction(repo: str, minutes: int, gap_minutes: int, session_id: str) -> str:
    clock_file = f"/Users/esther/prog/missioncontrol/tracking/.active-clocks/{session_id}.json"
    return (
        f"[idle-wrap trigger] The previous burst in **{repo}** (~{minutes} min) was assessed "
        f"complete and its grace window passed ({gap_minutes} min of silence) without the "
        "background watcher firing. BEFORE addressing the user's new message: run the `wrap-up` "
        f"skill in AUTOMATIC mode for the ENDED burst. Read {clock_file} FIRST, before any "
        "Bash/Edit call this turn (Read does not advance the heartbeat), so `last_activity` still "
        "marks the true burst end. Honest minutes = accrued_seconds/60 + (last_activity - start); "
        "row start = work_start (fall back to start), end = last_activity as read — do NOT extend "
        "the row into the pause or into this new turn. Write the timesheet.csv row + "
        "history.jsonl session entry with a SPECIFIC title, correct session_type, and a real "
        "one-line summary (source = `auto-wrap`); update any changed tracking (index.json, task "
        "T0NN.md files, status.json); commit + push per the wrap-up skill's git step; then RESET "
        "the clock (start=null, work_start=null, last_activity=null, accrued_seconds=0, "
        "first_turn_at=null, turn_count=0, wrap_armed_at=null, wrapped_at=now — keep the file). "
        "Then answer the user's message normally in this same turn, leading with a one-line wrap "
        "confirmation."
    )


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

    if not clock.get("wrap_armed_at"):
        return  # not assessed done -> never wrap, however long the gap

    if shared.is_legacy(clock) or not shared.has_started(clock):
        return

    la = clock.get("last_activity") or clock.get("start")
    try:
        la_dt = datetime.fromisoformat(la)
    except Exception:
        return

    now = datetime.now()
    try:
        idle_min = int(os.environ.get("IDLE_WRAP_MINUTES", DEFAULT_IDLE_WRAP_MINUTES))
    except Exception:
        idle_min = DEFAULT_IDLE_WRAP_MINUTES
    gap_minutes = (now - la_dt).total_seconds() / 60

    prompt = (data.get("prompt") or "").lstrip()
    wrap_here = (gap_minutes >= idle_min
                 and not prompt.startswith(SKIP_PROMPT_PREFIXES))

    # In every branch the arm is consumed: cleared stamp = any live watcher aborts.
    clock["wrap_armed_at"] = None
    if wrap_here:
        clock["last_nudge_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass

    if not wrap_here:
        return  # user continued in time (or is wrapping manually) — arm cancelled

    span = shared.honest_span(clock, now=now)
    if span is None:
        return
    _window_start, _end_dt, minutes = span

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": _instruction(
                clock.get("repo", "this repo"), minutes, int(gap_minutes), session_id),
        }
    }))


if __name__ == "__main__":
    main()
