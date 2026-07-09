#!/usr/bin/env python3
"""
SessionStart hook — ARM a per-session clock (honest-clock rewrite 2026-07-07).

Fires once per SessionStart with stdin JSON: {session_id, transcript_path, cwd,
hook_event_name, source, model}.

Old behavior (ghost-clock era): stamped `start` = tab-open time immediately, so
a tab merely *opened* began accruing time and produced a phantom timesheet row.

New behavior: only ARM the clock. Resolve repo/cluster from cwd (cwd is reliable
at open time) and write the clock with `opened_at` set and `start: null`. The
clock does not START until the first substantive tool fires (work-heartbeat.py
sets `start`). An armed-but-never-started clock writes NO timesheet row — that is
what eliminates ghost entries for tabs that never did work.

Steps:
1. Append CLAUDE_SESSION_ID=<id> to $CLAUDE_ENV_FILE (deduped) so subsequent Bash
   tool calls and skills (/co, /wrap-up) can identify this conversation's clock.
2. Discard any legacy single-file ~/prog/missioncontrol/tracking/.active-clock.json.
3. If a clock file already exists for this session_id, no-op (resume/clear/compact).
4. Otherwise write an ARMED clock (opened_at set, start=null).
5. Emit a UX message.

See docs/tracking-protocol.md ("The honest clock").
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# When deployed at ~/.claude/hooks/, _clock_shared.py is a sibling.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _clock_shared as shared


def _migrate_legacy_clock_if_present() -> None:
    legacy = shared.LEGACY_CLOCK_FILE
    try:
        payload = legacy.read_text()
    except FileNotFoundError:
        return
    except Exception as exc:
        print(f"[session-start-clock] WARN: legacy migration read failed: {exc}",
              file=sys.stderr)
        return

    print(
        f"[session-start-clock] discarded legacy clock at {legacy}: "
        f"{payload.strip()}",
        file=sys.stderr,
    )
    try:
        legacy.unlink()
    except FileNotFoundError:
        # Concurrent migrator already removed it.
        pass


def _record_session_id_env(session_id: str) -> None:
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if not env_file:
        print(
            "[session-start-clock] WARN: CLAUDE_ENV_FILE unset; "
            "skill-level lookups will fail loud later.",
            file=sys.stderr,
        )
        return
    try:
        shared.append_env_var(Path(env_file), "CLAUDE_SESSION_ID", session_id)
    except Exception as exc:
        print(f"[session-start-clock] WARN: failed to write env file: {exc}",
              file=sys.stderr)


def _emit(message: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"additionalContext": message}}))


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        print(f"[session-start-clock] ERROR: stdin is not valid JSON: {exc}",
              file=sys.stderr)
        sys.exit(1)

    session_id = data.get("session_id")
    if not session_id:
        print("[session-start-clock] ERROR: stdin missing session_id; cannot continue.",
              file=sys.stderr)
        sys.exit(1)

    cwd = data.get("cwd") or os.getcwd()
    source = data.get("source", "startup")

    _record_session_id_env(session_id)
    _migrate_legacy_clock_if_present()

    clock_path = shared.clock_path_for(session_id)
    shared.CLOCKS_DIR.mkdir(parents=True, exist_ok=True)

    if clock_path.exists():
        # Idempotent re-fire (resume / clear / compact). Preserve existing state
        # (whether armed or already started — do not reset the work span).
        try:
            existing = json.loads(clock_path.read_text())
            repo = existing.get("repo", "?")
            cluster = existing.get("cluster", "?")
        except Exception:
            repo = cluster = "?"
        _emit(
            f"Clock present for this session: {repo} ({cluster}). "
            f"Timing runs from your first action to your last; it wraps automatically."
        )
        return

    repo, cluster = shared.resolve_repo_and_cluster(cwd)
    now = datetime.now()
    clock = {
        "session_id": session_id,
        "repo": repo,
        "cluster": cluster,
        "opened_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "start": None,           # set by first substantive tool OR the 2nd turn
        "work_start": None,      # window start = first sub-span since last wrap
        "last_activity": None,   # bumped by work-heartbeat + auto-wrap-gate
        "accrued_seconds": 0,    # closed sub-spans since last wrap (idle-split)
        "date": now.strftime("%Y-%m-%d"),
        "cwd": cwd,
        "source_at_start": source,
        "tool_count": 0,
        "turn_count": 0,         # engaged turns (drives the turn-based clock-in)
        "first_turn_at": None,   # backdate anchor for the turn-based start
        "transcript_path": data.get("transcript_path"),  # finalizer backstop
        "wrapped_at": None,      # set by /wrap-up after it writes an entry
        "last_nudge_at": None,   # auto-wrap-gate cooldown
    }
    shared.write_clock_atomic(clock_path, clock)

    _emit(
        f"Clock armed: {repo} ({cluster}). Timing starts at your first action and "
        f"stops at task completion — the session wraps to tracking automatically."
    )


if __name__ == "__main__":
    main()
