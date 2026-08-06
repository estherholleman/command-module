#!/usr/bin/env python3
"""
UserPromptSubmit hook — idle wrap-on-return gate (2026-08-06).

Replaces the turn-end auto-wrap nudge that wrapped sessions way too quickly.
A Stop hook fires at the end of every turn — the one moment idle time is zero
by definition — so it could never know whether the user was about to continue,
and it chopped one working session into many small wrapped rows.

A session is over only after real silence. This gate fires when the user
RETURNS to a conversation whose previous work burst ended >= IDLE_WRAP_MINUTES
ago. At that moment the burst boundary is a fact, not a guess. It injects
additionalContext (never a block) telling the agent: run the wrap-up skill in
AUTOMATIC mode for the ENDED burst first, then answer the new message in the
same turn.

Gates (all must pass, else exit 0 = stay silent):
  - clock exists, non-legacy, STARTED   -> real work happened in the prior burst
  - gap since last_activity >= IDLE_WRAP_MINUTES -> the burst is actually over
  - honest minutes >= FLOOR_MINUTES     -> not a trivial blip (short bursts
                                           merge into the next span or the
                                           SessionEnd/sweep fallback row)
  - the prompt is not itself /wrap-up or /co (redundant nudge)

Sessions that never get another prompt still finalize honestly via the
SessionEnd hook or the launchd sweep (source=*-unwrapped; /evening refines).

Threshold: env IDLE_WRAP_MINUTES, default 30. Below 30 the wrapped row can
include the pause itself as billed time (gaps <= IDLE_GAP_SECONDS stay inside
a sub-span by design); 30 keeps wrap boundaries aligned with the clock's own
sub-span seal.

Stdin JSON: {session_id, transcript_path, cwd, prompt, hook_event_name}
Never break a turn: ANY error -> exit 0.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FLOOR_MINUTES = 4                # below this, not worth a wrap row
DEFAULT_IDLE_WRAP_MINUTES = 30   # silence that ends a session (env-overridable)

SKIP_PROMPT_PREFIXES = ("/wrap-up", "/co")


def _instruction(repo: str, minutes: int, gap_minutes: int) -> str:
    return (
        f"[idle-wrap trigger] The previous work burst in **{repo}** (~{minutes} min) ended "
        f"{gap_minutes} min ago — that session segment is over. BEFORE addressing the user's new "
        "message: invoke the `wrap-up` skill in AUTOMATIC mode for the ENDED burst. Read "
        "tracking/.active-clocks/<session_id>.json FIRST, before any Bash/Edit call this turn "
        "(Read does not advance the heartbeat), so `last_activity` still marks the true burst end. "
        "Automatic mode: honest minutes = accrued_seconds/60 + (last_activity - start); row start = "
        "work_start (fall back to start), end = last_activity as read — do NOT extend the row into "
        "the pause or into this new turn. Write the timesheet.csv row + history.jsonl session entry "
        "with a SPECIFIC title, correct session_type, and a real one-line summary (source = "
        "`auto-wrap`); update any changed tracking (index.json, task T0NN.md files, status.json); "
        "commit + push per the wrap-up skill's git step; then RESET the clock (start=null, "
        "work_start=null, last_activity=null, accrued_seconds=0, first_turn_at=null, turn_count=0, "
        "wrapped_at=now — keep the file). A wrap records a TIME SEGMENT, not task completion — wrap "
        "even if the task is unfinished (statuses just stay in_progress). Then answer the user's "
        "message normally in this same turn, leading with a one-line wrap confirmation."
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

    prompt = (data.get("prompt") or "").lstrip()
    if prompt.startswith(SKIP_PROMPT_PREFIXES):
        return  # the user is already wrapping/clocking out

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
    if gap_minutes < idle_min:
        return  # the conversation is still hot — no wrap

    span = shared.honest_span(clock, now=now)
    if span is None:
        return
    _window_start, _end_dt, minutes = span
    if minutes < FLOOR_MINUTES:
        return

    # Record the nudge (observability; the wrap itself resets the clock).
    clock["last_nudge_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": _instruction(
                clock.get("repo", "this repo"), minutes, int(gap_minutes)),
        }
    }))


if __name__ == "__main__":
    main()
