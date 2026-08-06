#!/usr/bin/env python3
"""
Stop hook — auto-wrap gate, arm-don't-wrap edition (2026-08-06 v2).

Fires at the end of every assistant turn. Two jobs:

1. ALWAYS: register the turn as engagement (turn-based clock start, tail
   advance, idle sub-span roll) and refresh transcript_path. Load-bearing for
   the honest clock — design/discussion turns that never touch a file still
   bill.

2. GATED: nudge the agent to SELF-ASSESS completion. The assessment is the
   same as the original 2026-07-07 gate (a shell hook can't judge done-ness),
   but the outcome changed: "done" no longer wraps on the spot — at turn-end
   idle time is zero by definition, so immediate wraps chopped live
   conversations into fragments. Instead the agent ARMS a delayed wrap:
   it launches idle-wrap-watcher.py as a background task and tells the user
   "task likely done — will wrap after ~N quiet minutes; keep going if you're
   not done." The watcher completes after IDLE_WRAP_MINUTES (default 30) of
   real silence and its output instructs the wrap; any new user prompt cancels
   the arm (idle-wrap-on-return.py clears it) and the next turn-end
   re-assesses. "Mid-task" still defers exactly as before.

Gates for the nudge (all must pass, else just record the turn):
  - stop_hook_active is False        -> the arm/defer continuation must not re-nudge
  - clock exists, non-legacy, STARTED -> real work happened this session
  - not already armed                 -> a watcher is pending; don't stack nudges
  - honest work minutes >= FLOOR      -> not a trivial 1-tool blip
  - cooldown: no nudge within COOLDOWN unless new work since the last nudge
  - artifacts: uncommitted changes in cwd OR a healthy chunk of work

Stdin JSON: {session_id, transcript_path, cwd, stop_hook_active, hook_event_name}
Never break a turn: ANY error -> exit 0.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FLOOR_MINUTES = 4          # below this, not worth arming a wrap
COOLDOWN_MINUTES = 12      # don't re-nudge sooner than this without new work
MEANINGFUL_MINUTES = 25    # a long span is worth wrapping even with nothing to commit
DEFAULT_IDLE_WRAP_MINUTES = 30

WATCHER = "/Users/esther/.claude/hooks/idle-wrap-watcher.py"


def _git_dirty(cwd: str) -> bool:
    """True if the cwd git repo has uncommitted changes. False on any error."""
    if not cwd:
        return False
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain"],
            capture_output=True, text=True, timeout=8,
        )
        return out.returncode == 0 and bool(out.stdout.strip())
    except Exception:
        return False


def _instruction(repo: str, minutes: int, dirty: bool, session_id: str, idle_min: int) -> str:
    artifacts = "uncommitted changes are present" if dirty else "tracking is likely stale"
    return (
        f"[auto-wrap gate] ~{minutes} min of tracked work in **{repo}** and {artifacts}. "
        "SELF-ASSESS — do not wrap now in either case. "
        "IF your last response completed a coherent piece of work AND the user's request is fully "
        "satisfied (you are NOT mid-task and NOT waiting on the user to answer a question): ARM a "
        "delayed wrap — run exactly this command via Bash with run_in_background set to true: "
        f"`/usr/bin/python3 {WATCHER} {session_id}` — it completes only after ~{idle_min} quiet "
        "minutes (and aborts itself if the user continues). Then reply with one short line: "
        f"\"✅ task likely done — will wrap after ~{idle_min} quiet minutes; keep going if you're "
        "not done.\" and stop. When that background task later completes, follow ITS output "
        "exactly (WRAP-NOW -> run the wrap-up skill in AUTOMATIC mode; ABORT -> output nothing). "
        "OTHERWISE (mid-task, or you just asked the user something): do NOT arm — reply with "
        "exactly \"(auto-wrap deferred — work in progress)\" and stop."
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

    if shared.is_legacy(clock):
        return  # unrecoverable pre-rewrite clock — finalizers drain it

    # A turn-end IS engaged time: count it (turn-based start, tail advance,
    # idle sub-span roll) and refresh transcript_path for reconciliation.
    now = datetime.now()
    try:
        shared.register_engagement(clock, now, is_tool=False)
        tp = data.get("transcript_path")
        if tp:
            clock["transcript_path"] = tp
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass

    if data.get("stop_hook_active"):
        return  # this turn is already a hook continuation — never re-nudge

    if clock.get("wrap_armed_at"):
        return  # a watcher is pending; its outcome decides

    span = shared.honest_span(clock, now=now)
    if span is None:
        return  # armed-only or not started -> nothing to assess
    _start_dt, _end_dt, minutes = span
    if minutes < FLOOR_MINUTES:
        return

    # Cooldown: no re-nudge within COOLDOWN unless there's new work since then.
    last_nudge = clock.get("last_nudge_at")
    if last_nudge:
        try:
            since = (now - datetime.fromisoformat(last_nudge)).total_seconds() / 60
            la = clock.get("last_activity")
            new_work = bool(la and datetime.fromisoformat(la) > datetime.fromisoformat(last_nudge))
            if since < COOLDOWN_MINUTES and not new_work:
                return
        except Exception:
            pass

    dirty = _git_dirty(clock.get("cwd") or data.get("cwd") or "")
    if not dirty and minutes < MEANINGFUL_MINUTES:
        return  # nothing to commit and only a short span -> don't nag

    try:
        idle_min = int(os.environ.get("IDLE_WRAP_MINUTES", DEFAULT_IDLE_WRAP_MINUTES))
    except Exception:
        idle_min = DEFAULT_IDLE_WRAP_MINUTES

    # Fire: record the nudge time (cooldown) and inject the assess-and-arm instruction.
    clock["last_nudge_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass

    print(json.dumps({
        "decision": "block",
        "reason": _instruction(clock.get("repo", "this repo"), minutes, dirty,
                               session_id, idle_min),
    }))


if __name__ == "__main__":
    main()
