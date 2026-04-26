#!/usr/bin/env python3
"""
SessionEnd hook — opportunistic clock finalize.

Best-effort finalize-on-end. The launchd orphan sweep (Phase 3) is the
actual reliability mechanism — SessionEnd misses on API 500, OS reboot,
process kill, and some /exit paths.

Stdin JSON: {session_id, hook_event_name, reason}
  reason ∈ {clear, resume, logout, prompt_input_exit,
            bypass_permissions_disabled, other}

Behavior:
- reason ∈ {clear, resume} → exit 0 (lifecycle event, not termination).
  Log diagnostic to stderr; do not finalize.
- reason ∈ {logout, prompt_input_exit, bypass_permissions_disabled, other}
  → finalize: read clock, write CSV row + history entry, delete clock file.
- Missing clock for session_id → exit 0 (already finalized by /co or /wrap-up).
- Malformed stdin → exit 1 with stderr error.

See plan: docs/plans/2026-04-24-001-feat-per-session-clocks-reliability-plan.md (D2)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _clock_shared as shared

LIFECYCLE_REASONS = {"clear", "resume"}
TERMINAL_REASONS = {"logout", "prompt_input_exit", "bypass_permissions_disabled", "other"}
DEFAULT_SESSION_TYPE = "execution"


def _finalize(session_id: str, reason: str) -> None:
    clock_path = shared.clock_path_for(session_id)
    if not clock_path.exists():
        # Already finalized by /co or /wrap-up — nothing to do.
        return

    clock = json.loads(clock_path.read_text())
    start_dt = datetime.fromisoformat(clock["start"])
    now = datetime.now()
    minutes = max(1, int((now - start_dt).total_seconds() / 60))

    repo = clock.get("repo", "unknown")
    cluster = clock.get("cluster", "unassigned")
    title = f"Auto-closed at SessionEnd ({reason})"
    details = (
        f"Clock opened {start_dt.strftime('%Y-%m-%d %H:%M')}, "
        f"auto-closed by SessionEnd at {now.strftime('%Y-%m-%d %H:%M')} "
        f"with reason={reason}. Correct manually if session_type/title are wrong."
    )

    shared.write_csv_row(
        date=start_dt.date().isoformat(),
        start_hm=start_dt.strftime("%H:%M"),
        end_hm=now.strftime("%H:%M"),
        repo=repo,
        cluster=cluster,
        session_type=DEFAULT_SESSION_TYPE,
        minutes=minutes,
        title=title,
        details=details,
        source="auto-session-end",
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

    # Anything else (including unknown values) treated as terminal —
    # better an over-finalized row the user corrects than a lost session.
    try:
        _finalize(session_id, reason)
    except Exception as exc:
        print(f"[session-end-clock] ERROR finalizing session={session_id}: {exc}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
