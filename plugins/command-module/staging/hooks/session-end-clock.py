#!/usr/bin/env python3
"""
SessionEnd hook — honest finalize / drain (honest-clock rewrite 2026-07-07).

Best-effort finalize-on-end. The launchd sweep (auto-close-clock.py) is the
reliability backstop — SessionEnd misses on API 500, OS reboot, process kill,
and some /exit paths.

Stdin JSON: {session_id, hook_event_name, reason}
  reason in {clear, resume, logout, prompt_input_exit,
             bypass_permissions_disabled, other}

Behavior:
- reason in {clear, resume} -> lifecycle event, do NOT finalize (exit 0).
- Otherwise, load this session's clock and:
    * legacy (no `opened_at`)      -> DRAIN, write no row (unrecoverable ghost).
    * armed but never STARTED      -> DRAIN, write no row (no work happened).
    * STARTED, not yet wrapped     -> write an HONEST row [start, last_activity],
                                      source=auto-session-end-unwrapped, flagged for
                                      reconciliation, then delete the clock.
    * missing clock file           -> exit 0 (already wrapped by /co or /wrap-up).

The honest span (last_activity - start) means these fallback rows carry a real
work duration, not tab-open->tab-close. session_type stays a guess (a hook can't
reason) — the title says so, and /evening's reconcile can refine it.

See docs/tracking-protocol.md ("The honest clock" + "Reconciliation").
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _clock_shared as shared

LIFECYCLE_REASONS = {"clear", "resume"}
DEFAULT_SESSION_TYPE = "execution"


def _finalize(session_id: str, reason: str) -> None:
    clock_path = shared.clock_path_for(session_id)
    if not clock_path.exists():
        return  # already finalized by /co or /wrap-up

    clock = json.loads(clock_path.read_text())

    # Legacy or armed-but-never-started -> DRAIN without a row (kills ghosts).
    span = shared.honest_span(clock, now=datetime.now())
    if span is None:
        reason_txt = "legacy" if shared.is_legacy(clock) else "no work (armed only)"
        print(f"[session-end-clock] drained {clock_path.name} without a row ({reason_txt}).",
              file=sys.stderr)
        clock_path.unlink()
        return

    start_dt, end_dt, minutes = span
    repo = clock.get("repo", "unknown")
    cluster = clock.get("cluster", "unassigned")
    title = "Unwrapped session (auto-finalized at SessionEnd)"
    details = (
        f"Work {start_dt.strftime('%Y-%m-%d %H:%M')}-{end_dt.strftime('%H:%M')} "
        f"({minutes} min, honest span). Session ended (reason={reason}) before an "
        f"auto-wrap ran. session_type is a guess; refine title/type in /evening reconcile."
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
        source="auto-session-end-unwrapped",
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
    clock_path.unlink()


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        print(f"[session-end-clock] ERROR: stdin is not valid JSON: {exc}",
              file=sys.stderr)
        sys.exit(1)

    session_id = data.get("session_id")
    reason = data.get("reason", "other")

    if not session_id:
        print("[session-end-clock] ERROR: stdin missing session_id; cannot continue.",
              file=sys.stderr)
        sys.exit(1)

    if reason in LIFECYCLE_REASONS:
        print(
            f"[session-end-clock] reason={reason} for session={session_id}: "
            f"lifecycle event, not finalizing.",
            file=sys.stderr,
        )
        return

    try:
        _finalize(session_id, reason)
    except Exception as exc:
        print(f"[session-end-clock] ERROR finalizing session={session_id}: {exc}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
