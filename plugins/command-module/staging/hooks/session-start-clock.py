#!/usr/bin/env python3
"""
SessionStart hook — per-session auto-clock-in.

Replaces auto-clock-in.py (UserPromptSubmit, single-slot). Fires once per
SessionStart event with stdin JSON: {session_id, transcript_path, cwd,
hook_event_name, source, model}.

Behavior:
1. Append CLAUDE_SESSION_ID=<id> to $CLAUDE_ENV_FILE (deduped) so subsequent
   Bash tool calls in this session see the env var.
2. Lazy-migrate legacy ~/prog/missioncontrol/tracking/.active-clock.json:
   log payload to stderr, then unlink. No CSV row written (D4).
3. If a per-session clock file already exists for this session_id, no-op
   (covers source=resume|clear|compact — D7 deferred-impl: preserve start).
4. Otherwise resolve repo/cluster from cwd (fall back to basename + "unassigned"
   when cwd is outside ~/prog) and write the clock file.
5. Emit hookSpecificOutput.additionalContext UX message.

See plan: docs/plans/2026-04-24-001-feat-per-session-clocks-reliability-plan.md
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
        # Idempotent re-fire (resume / clear / compact). Preserve start timestamp.
        try:
            existing = json.loads(clock_path.read_text())
            repo = existing.get("repo", "?")
            cluster = existing.get("cluster", "?")
            start = existing.get("start", "?")
        except Exception:
            repo = cluster = start = "?"
        _emit(
            f"Clock already running for this session: {repo} ({cluster}) since {start}. "
            f"Run /co when done."
        )
        return

    repo, cluster = shared.resolve_repo_and_cluster(cwd)
    now = datetime.now()
    clock = {
        "session_id": session_id,
        "repo": repo,
        "cluster": cluster,
        "start": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "cwd": cwd,
        "source_at_start": source,
    }
    tmp_path = clock_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(clock, indent=2) + "\n")
    os.replace(tmp_path, clock_path)

    _emit(
        f"Auto clocked in: {repo} ({cluster}) at {now.strftime('%H:%M')}. "
        f"Run /co when done."
    )


if __name__ == "__main__":
    main()
