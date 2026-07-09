#!/usr/bin/env python3
"""
Auto close-clock — launchd sweep, reliability backstop (honest-clock rewrite 2026-07-07).

Runs daily via the com.esther.auto-close-clock LaunchAgent. Iterates every file
in /Users/esther/prog/missioncontrol/tracking/.active-clocks/ and finalizes each
independently, using the HONEST span rather than the old 20:00 wall-clock cap.

Per clock:
  - legacy (no `opened_at`)      -> DRAIN, write no row (unrecoverable ghost —
                                    this is what cleanly retires the pre-rewrite
                                    orphan backlog to zero ghost rows).
  - armed but never STARTED      -> DRAIN, write no row (tab opened, no work).
  - STARTED, not yet wrapped     -> write an HONEST row [start, last_activity],
                                    source=auto-close-unwrapped, then unlink.

No more 20:00 cap and no more "407 min" inflation: last_activity is the real end.
A clock still armed (start=null) from a live session is harmless to leave — it
carries no time — but the sweep drains it too, and the live session re-arms on its
next SessionStart / first tool. Failures on one clock never abort the others.

Empty or missing .active-clocks/ -> no-op, clean exit.

See docs/tracking-protocol.md ("The honest clock" + "Reconciliation").
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _clock_shared as shared

DEFAULT_SESSION_TYPE = "execution"


def close_one(clock_path: Path) -> dict:
    """Finalize a single clock file. Returns a result dict (drained or written)."""
    clock = json.loads(clock_path.read_text())
    now = datetime.now()

    result = shared.finalize_row(clock, now=now)
    if result is None:
        drain_reason = "legacy" if shared.is_legacy(clock) else "armed-only"
        clock_path.unlink()
        return {"drained": True, "reason": drain_reason,
                "session_id": clock.get("session_id", ""),
                "repo": clock.get("repo", "unknown")}

    start_dt, end_dt, minutes, method = result
    method_note = {
        "clock": "honest span",
        "reconciled": "reconciled from transcript",
        "reconstructed": "reconstructed from transcript",
    }.get(method, "honest span")
    repo = clock.get("repo", "unknown")
    cluster = clock.get("cluster", "unassigned")
    session_id = clock.get("session_id", "")
    title = "Unwrapped session (auto-finalized by sweep)"
    details = (
        f"Work {start_dt.strftime('%Y-%m-%d %H:%M')}-{end_dt.strftime('%H:%M')} "
        f"({minutes} min, {method_note}). Never auto-wrapped; finalized by the launchd "
        f"sweep at {now.strftime('%Y-%m-%d %H:%M')}. Refine title/type in /evening reconcile."
    )

    shared.write_csv_row(
        date=start_dt.date().isoformat(),
        start_hm=start_dt.strftime("%H:%M"),
        end_hm=end_dt.strftime("%H:%M"),
        repo=repo,
        cluster=cluster,
        session_type=DEFAULT_SESSION_TYPE,
        minutes=minutes,
        title=title,
        details=details,
        source="auto-close-unwrapped",
        session_id=session_id,
    )
    shared.write_history_entry(
        repo=repo,
        date=start_dt.date().isoformat(),
        start_iso=start_dt.isoformat(timespec="seconds"),
        session_type=DEFAULT_SESSION_TYPE,
        title=title,
        details=details,
        minutes=minutes,
    )
    # Delete only after successful writes — a re-run resumes on partial failure.
    clock_path.unlink()

    return {
        "drained": False,
        "session_id": session_id,
        "repo": repo,
        "minutes": minutes,
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
        sid_short = r["session_id"][:8] if r.get("session_id") else "<none>"
        if r.get("drained"):
            print(f"[auto-close-clock] {stamp} — drained {r['repo']} "
                  f"({r['reason']}, no row, session={sid_short}).")
        else:
            print(
                f"[auto-close-clock] {stamp} — closed {r['repo']} "
                f"({r['minutes']} min, auto-close-unwrapped, session={sid_short}). "
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
