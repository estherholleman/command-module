#!/usr/bin/env python3
"""Suggest the minutes to log for this session's clock at wrap-up.

Usage: suggest-minutes.py <clock-file>

Prints one JSON object:
  clock_minutes      honest-clock minutes (accrued_seconds + open sub-span), main thread only
  transcript_minutes engaged minutes from the main transcript AND its subagent transcripts
  span_minutes       wall-clock minutes from window start to now (upper bound, includes idle)
  suggested_minutes  max(clock_minutes, transcript_minutes)
  start / end        HH:MM of the suggested window, date = clock date

The honest clock only advances on main-thread tools and turns, so long subagent or
background runs leave it quiet. Subagent transcripts (<session>/subagents/*.jsonl next to
the main transcript) carry timestamps for that work. Gaps between moments count by the
clock hooks' gap rule (~/.claude/hooks/_clock_shared.py: up to the wrap window in full,
longer ones minus the stretches the display was off); without the hooks, by the window alone.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

IDLE_GAP_SECONDS = 60 * 60

try:
    sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
    from _clock_shared import gap_credit
except Exception:
    def gap_credit(a, b):
        gap = (b - a).total_seconds()
        return gap if 0 < gap <= IDLE_GAP_SECONDS else 0.0


def parse(ts):
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def transcript_times(path, since, now):
    times = []
    try:
        lines = Path(path).read_text().splitlines()
    except OSError:
        return times
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("type") not in ("user", "assistant"):
            continue
        dt = parse(entry.get("timestamp"))
        if dt is None or (since and dt < since) or dt > now:
            continue
        times.append(dt)
    return times


def engaged(times):
    """Sum of the gaps between consecutive moments, each counted by gap_credit."""
    if len(times) < 2:
        return 0, None, None
    times = sorted(times)
    total = sum(gap_credit(a, b) for a, b in zip(times, times[1:]))
    return int(total / 60), times[0], times[-1]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: suggest-minutes.py <clock-file>")
    clock = json.loads(Path(sys.argv[1]).read_text())
    now = datetime.now()

    clock_minutes = 0
    window_start = None
    if clock.get("start"):
        start = parse(clock["start"])
        last = parse(clock.get("last_activity")) or start
        open_secs = max(0.0, (min(last, now) - start).total_seconds())
        clock_minutes = int((int(clock.get("accrued_seconds") or 0) + open_secs) / 60)
        window_start = parse(clock.get("work_start")) or start

    since = parse(clock.get("wrapped_at") or clock.get("opened_at"))
    times = []
    main_path = clock.get("transcript_path")
    if main_path:
        times += transcript_times(main_path, since, now)
        subagents = Path(main_path).with_suffix("") / "subagents"
        for sub in sorted(subagents.glob("*.jsonl")) if subagents.is_dir() else []:
            times += transcript_times(sub, since, now)
    transcript_minutes, first, _ = engaged(times)

    candidates = [t for t in (window_start, first) if t]
    window_start = min(candidates) if candidates else now
    print(json.dumps({
        "repo": clock.get("repo"),
        "date": clock.get("date"),
        "clock_minutes": clock_minutes,
        "transcript_minutes": transcript_minutes,
        "span_minutes": int((now - window_start).total_seconds() / 60),
        "suggested_minutes": max(1, clock_minutes, transcript_minutes),
        "start": window_start.strftime("%H:%M"),
        "end": now.strftime("%H:%M"),
    }))


if __name__ == "__main__":
    main()
