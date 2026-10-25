#!/usr/bin/env python3
"""Suggest the minutes to log for this session's clock at wrap-up.

Usage: suggest-minutes.py <clock-file>

Prints one JSON object:
  clock_minutes      honest-clock minutes (accrued_seconds + open sub-span), main thread only
  transcript_minutes engaged minutes from the main transcript AND its subagent transcripts
  span_minutes       wall-clock minutes from window start to now (upper bound, includes idle)
  suggested_minutes  max(clock_minutes, transcript_minutes)
  start / end        HH:MM of the suggested window, date = clock date

The honest clock only advances on main-thread tools and turns and treats any gap over
30 minutes as idle, so long subagent or background runs are dropped. Subagent transcripts
(<session>/subagents/*.jsonl next to the main transcript) carry timestamps for that work.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

IDLE_GAP_SECONDS = 30 * 60


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
    """Sum of cluster spans, splitting on gaps longer than IDLE_GAP_SECONDS."""
    if len(times) < 2:
        return 0, None, None
    times = sorted(times)
    total, cluster_start, prev = 0.0, times[0], times[0]
    for t in times[1:]:
        if (t - prev).total_seconds() > IDLE_GAP_SECONDS:
            total += (prev - cluster_start).total_seconds()
            cluster_start = t
        prev = t
    total += (prev - cluster_start).total_seconds()
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
