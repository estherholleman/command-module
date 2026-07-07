#!/usr/bin/env python3
"""
Stop hook — auto-wrap gate (2026-07-07).

Fires at the end of every assistant turn. Its job is NOT to wrap — a shell hook
can't reason about session_type/title/summary or which tasks changed, which is
exactly why the old dumb-hook finalizers produced generic "Auto-closed...
execution... correct manually" rows. Instead this gate decides *whether the
moment looks like a completed piece of work* and, if so, injects an instruction
(decision:block) that makes THE AGENT run /wrap-up non-interactively — producing
an agent-quality entry plus the commit/push, then resetting the clock.

Gates (all must pass, else exit 0 = let the turn stop normally):
  - stop_hook_active is False        -> avoid the continuation loop (only nudge once)
  - clock exists, non-legacy, STARTED -> real work happened this session
  - honest work minutes >= FLOOR      -> not a trivial 1-tool blip
  - cooldown: no nudge within COOLDOWN unless new work since the last nudge
  - artifacts: uncommitted changes in cwd OR a healthy chunk of work
                                       -> there is something worth wrapping/committing

When it fires it records last_nudge_at (cooldown) and returns:
  {"decision":"block","reason": <the auto-wrap instruction>}

The instruction tells the agent to SELF-ASSESS: wrap only if it just completed a
coherent unit and the user's request is satisfied; if mid-task, reply one line and
stop. On that continuation the next Stop has stop_hook_active=True, so we never loop.

Stdin JSON: {session_id, transcript_path, cwd, stop_hook_active, hook_event_name}
Never break a turn: ANY error -> exit 0.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FLOOR_MINUTES = 4          # below this, not worth an auto-wrap
COOLDOWN_MINUTES = 12      # don't re-nudge sooner than this without new work
MEANINGFUL_MINUTES = 25    # a long span is worth wrapping even with nothing to commit


def _load(name, obj, default=None):
    v = obj.get(name)
    return v if v is not None else default


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


def _instruction(repo: str, minutes: int, dirty: bool) -> str:
    artifacts = "uncommitted changes are present" if dirty else "tracking is likely stale"
    return (
        f"[auto-wrap trigger] ~{minutes} min of tracked work in **{repo}** and {artifacts}. "
        "IF your last response completed a coherent piece of work AND the user's request is fully "
        "satisfied (you are NOT mid-task and NOT waiting on the user to answer a question): invoke "
        "the `wrap-up` skill in AUTOMATIC mode now, without asking for confirmation. Automatic mode: "
        "finalize this session's honest clock (duration = start -> last_activity from "
        "tracking/.active-clocks/<session_id>.json, NOT tab-open->now), write the timesheet.csv row "
        "+ history.jsonl session entry with a SPECIFIC title, correct session_type, and a real "
        "one-line summary (source column = `auto-wrap`); update any changed tracking (index.json, "
        "task T0NN.md files, status.json); commit + push per the wrap-up skill's git step; then RESET "
        "the clock for continued work (set start=null, last_activity=null, wrapped_at=now, keep the "
        "file). Finish with a one-line confirmation, then stop. "
        "OTHERWISE (mid-task, or you just asked the user something): do NOT wrap — reply with exactly "
        "\"(auto-wrap deferred — work in progress)\" and stop."
    )


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return

    if data.get("stop_hook_active"):
        return  # we already injected on this continuation; let it stop -> no loop

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

    now = datetime.now()

    # Keep the tail honest even when the last action was a read (unmatched by
    # the heartbeat): a STARTED clock's last_activity advances to turn-end —
    # but only across a SMALL gap. A large gap since the last action is idle
    # (e.g. a deferred wrap then a long-open tab); never advance into it.
    if shared.has_started(clock) and not shared.is_legacy(clock):
        prev_la = _load("last_activity", clock)
        advance = True
        if prev_la:
            try:
                gap = (now - datetime.fromisoformat(prev_la)).total_seconds()
                advance = gap <= shared.IDLE_GAP_SECONDS
            except Exception:
                advance = True
        if advance:
            clock["last_activity"] = now.strftime("%Y-%m-%dT%H:%M:%S")
            try:
                shared.write_clock_atomic(clock_path, clock)
            except Exception:
                pass

    span = shared.honest_span(clock, now=now)
    if span is None:
        return  # armed-only, legacy, or not started -> nothing to wrap
    _start_dt, _end_dt, minutes = span
    if minutes < FLOOR_MINUTES:
        return

    # Cooldown: no re-nudge within COOLDOWN unless there's new work since then.
    last_nudge = _load("last_nudge_at", clock)
    if last_nudge:
        try:
            since = (now - datetime.fromisoformat(last_nudge)).total_seconds() / 60
            la = _load("last_activity", clock)
            new_work = bool(la and datetime.fromisoformat(la) > datetime.fromisoformat(last_nudge))
            if since < COOLDOWN_MINUTES and not new_work:
                return
        except Exception:
            pass

    dirty = _git_dirty(clock.get("cwd") or data.get("cwd") or "")
    if not dirty and minutes < MEANINGFUL_MINUTES:
        return  # nothing to commit and only a short span -> don't nag

    # Fire: record the nudge time (cooldown) and inject the wrap instruction.
    clock["last_nudge_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        shared.write_clock_atomic(clock_path, clock)
    except Exception:
        pass

    print(json.dumps({
        "decision": "block",
        "reason": _instruction(clock.get("repo", "this repo"), minutes, dirty),
    }))


if __name__ == "__main__":
    main()
