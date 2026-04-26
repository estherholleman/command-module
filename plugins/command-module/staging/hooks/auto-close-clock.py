#!/usr/bin/env python3
"""
Auto close-clock — runs daily at 20:00 via launchd LaunchAgent (Phase 3).

Iterates every file in /Users/esther/prog/missioncontrol/tracking/.active-clocks/
and closes each one independently with the same time-cap policy as the legacy
single-file sweep:

- start_date == today and now < 20:00 → end at 20:00 (cap), source=auto-close-20h.
- start_date == today and now >= 20:00 → end at now, source=auto-close-20h.
- start_date < today and start_dt < 20:00 of start_date → end at 20:00 of start_date,
  source=auto-close-stale.
- start_date < today and start_dt >= 20:00 of start_date → end at start + 30min
  (LATE_START_FALLBACK_MIN), source=auto-close-stale.

Each clock is finalized to a CSV row + history.jsonl entry, then the clock file
is unlinked. Failures on one clock do not abort the others.

CSV row's session_id is taken from the clock payload.

Empty or missing .active-clocks/ directory → no-op, clean exit.

Replaces the legacy ~/.claude/hooks/auto-close-clock.py wholesale. The Phase 3
install script copies this file in and switches the trigger from cron to a
launchd LaunchAgent so missed 20:00 firings catch up on wake.

See plan: docs/plans/2026-04-24-001-feat-per-session-clocks-reliability-plan.md
(D3, Unit 6).
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _clock_shared as shared

LATE_START_FALLBACK_MIN = 30
DEFAULT_SESSION_TYPE = "execution"
CAP_HOUR = 20


def close_one(clock_path: Path) -> dict:
    """Finalize a single clock file. Returns a result dict, or raises on error."""
    clock = json.loads(clock_path.read_text())

    start_iso = clock["start"]
    start_dt = datetime.fromisoformat(start_iso)
    start_date = start_dt.date()
    repo = clock.get("repo", "unknown")
    cluster = clock.get("cluster", "unassigned")
    session_id = clock.get("session_id", "")
    now = datetime.now()
    today = now.date()

    cap_same_day = datetime.combine(start_date, datetime.min.time()).replace(hour=CAP_HOUR)

    if start_date == today:
        end_dt = cap_same_day if now >= cap_same_day else now
        source = "auto-close-20h"
    else:
        if start_dt < cap_same_day:
            end_dt = cap_same_day
        else:
            end_dt = start_dt + timedelta(minutes=LATE_START_FALLBACK_MIN)
        source = "auto-close-stale"

    minutes = max(1, int((end_dt - start_dt).total_seconds() / 60))
    title = f"Auto-closed at {end_dt.strftime('%H:%M')}"
    details = (
        f"Clock opened {start_dt.strftime('%Y-%m-%d %H:%M')}, "
        f"auto-closed by launchd at {now.strftime('%Y-%m-%d %H:%M')}. "
        f"Correct manually if session_type/title are wrong."
    )

    shared.write_csv_row(
        date=start_date.isoformat(),
        start_hm=start_dt.strftime("%H:%M"),
        end_hm=end_dt.strftime("%H:%M"),
        repo=repo,
        cluster=cluster,
        session_type=DEFAULT_SESSION_TYPE,
        minutes=minutes,
        title=title,
        details=details,
        source=source,
        session_id=session_id,
    )
    shared.write_history_entry(
        repo=repo,
        date=start_date.isoformat(),
        start_iso=start_dt.isoformat(timespec="seconds"),
        session_type=DEFAULT_SESSION_TYPE,
        title=title,
        details=details,
        minutes=minutes,
    )
    # Delete only after successful writes — re-run resumes on partial failure.
    clock_path.unlink()

    return {
        "session_id": session_id,
        "repo": repo,
        "minutes": minutes,
        "source": source,
        "start": start_dt.isoformat(timespec="seconds"),
        "end": end_dt.isoformat(timespec="seconds"),
    }


def sweep() -> tuple[list[dict], list[tuple[Path, Exception]]]:
    """Iterate all clock files; return (closed, failed) lists."""
    closed: list[dict] = []
    failed: list[tuple[Path, Exception]] = []
    if not shared.CLOCKS_DIR.exists():
        return closed, failed
    try:
        clock_paths = sorted(shared.CLOCKS_DIR.glob("*.json"))
    except FileNotFoundError:
        return closed, failed
    for path in clock_paths:
        try:
            closed.append(close_one(path))
        except Exception as exc:  # noqa: BLE001 — keep going across siblings
            failed.append((path, exc))
    return closed, failed


def main() -> None:
    closed, failed = sweep()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not closed and not failed:
        print(f"[auto-close-clock] {stamp} — no active clocks, nothing to do.")
        return

    for r in closed:
        sid_short = r['session_id'][:8] if r['session_id'] else "<none>"
        print(
            f"[auto-close-clock] {stamp} — closed {r['repo']} "
            f"({r['minutes']} min, {r['source']}, session={sid_short}). "
            f"start={r['start']} end={r['end']}"
        )
    for path, exc in failed:
        print(
            f"[auto-close-clock] {stamp} — ERROR closing {path.name}: {exc!r}",
            file=sys.stderr,
        )

    if failed and not closed:
        sys.exit(1)


if __name__ == "__main__":
    main()
