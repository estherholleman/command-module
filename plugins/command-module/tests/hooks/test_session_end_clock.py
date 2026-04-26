"""
Tests for session-end-clock.py.

Run from the repo root:
    python3 -m pytest plugins/command-module/tests/hooks/test_session_end_clock.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest


HOOK_PATH = (
    Path(__file__).resolve().parents[2]
    / "staging" / "hooks" / "session-end-clock.py"
)
SHARED_PATH = HOOK_PATH.parent / "_clock_shared.py"


@pytest.fixture
def fakefs(tmp_path):
    fs_root = tmp_path / "fakefs"
    fs_root.mkdir()
    mc = fs_root / "missioncontrol"
    (mc / "tracking").mkdir(parents=True)
    (mc / "reports").mkdir(parents=True)
    (mc / "projects.yaml").write_text(
        "clusters:\n  meta:\n    projects:\n      - repo: missioncontrol\n"
    )

    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    shared_text = SHARED_PATH.read_text().replace(
        'MISSION_CONTROL = Path("/Users/esther/prog/missioncontrol")',
        f'MISSION_CONTROL = Path("{mc}")',
    )
    (hook_dir / "_clock_shared.py").write_text(shared_text)
    (hook_dir / "session-end-clock.py").write_text(HOOK_PATH.read_text())

    return {
        "root": fs_root,
        "mc": mc,
        "tracking": mc / "tracking",
        "clocks_dir": mc / "tracking" / ".active-clocks",
        "timesheet": mc / "reports" / "timesheet.csv",
        "hook": hook_dir / "session-end-clock.py",
    }


def _run_hook(fakefs, payload):
    return subprocess.run(
        [sys.executable, str(fakefs["hook"])],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def _seed_clock(fakefs, session_id, repo="missioncontrol", cluster="meta",
                start_offset_minutes=120):
    fakefs["clocks_dir"].mkdir(parents=True, exist_ok=True)
    start = datetime.now() - timedelta(minutes=start_offset_minutes)
    clock = {
        "session_id": session_id,
        "repo": repo,
        "cluster": cluster,
        "start": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "date": start.strftime("%Y-%m-%d"),
        "cwd": "/whatever",
        "source_at_start": "startup",
    }
    path = fakefs["clocks_dir"] / f"{session_id}.json"
    path.write_text(json.dumps(clock))
    return path


def test_reason_clear_does_not_finalize(fakefs):
    clock_path = _seed_clock(fakefs, "sess-A")
    result = _run_hook(fakefs, {"session_id": "sess-A", "reason": "clear"})

    assert result.returncode == 0
    assert clock_path.exists()
    assert not fakefs["timesheet"].exists()
    assert "lifecycle event" in result.stderr


def test_reason_resume_does_not_finalize(fakefs):
    clock_path = _seed_clock(fakefs, "sess-B")
    result = _run_hook(fakefs, {"session_id": "sess-B", "reason": "resume"})

    assert result.returncode == 0
    assert clock_path.exists()
    assert not fakefs["timesheet"].exists()


def test_reason_logout_finalizes(fakefs):
    clock_path = _seed_clock(fakefs, "sess-C", start_offset_minutes=90)
    result = _run_hook(fakefs, {"session_id": "sess-C", "reason": "logout"})

    assert result.returncode == 0, result.stderr
    assert not clock_path.exists()
    rows = fakefs["timesheet"].read_text().splitlines()
    assert rows[0].startswith("date,start,end,")
    assert rows[0].endswith(",session_id")
    assert ",auto-session-end,sess-C" in rows[1]
    assert "missioncontrol" in rows[1]


def test_no_clock_file_is_noop(fakefs):
    """Already finalized by /co — no row written, no error."""
    result = _run_hook(fakefs, {"session_id": "missing", "reason": "logout"})

    assert result.returncode == 0
    assert not fakefs["timesheet"].exists()


def test_reason_other_treated_as_terminal(fakefs):
    clock_path = _seed_clock(fakefs, "sess-D")
    result = _run_hook(fakefs, {"session_id": "sess-D", "reason": "other"})

    assert result.returncode == 0, result.stderr
    assert not clock_path.exists()
    assert "auto-session-end,sess-D" in fakefs["timesheet"].read_text()


def test_unknown_reason_finalizes_safe_default(fakefs):
    """Unexpected reason shouldn't lose data — finalize."""
    clock_path = _seed_clock(fakefs, "sess-E")
    result = _run_hook(fakefs, {"session_id": "sess-E", "reason": "unknown_new_value"})

    assert result.returncode == 0, result.stderr
    assert not clock_path.exists()


def test_malformed_stdin_fails_loud(fakefs):
    result = subprocess.run(
        [sys.executable, str(fakefs["hook"])],
        input="not json {{{",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "stdin is not valid JSON" in result.stderr


def test_missing_session_id_fails_loud(fakefs):
    result = _run_hook(fakefs, {"reason": "logout"})
    assert result.returncode == 1
    assert "missing session_id" in result.stderr


def test_finalize_writes_history_entry(fakefs):
    _seed_clock(fakefs, "sess-F", repo="missioncontrol", start_offset_minutes=60)
    _run_hook(fakefs, {"session_id": "sess-F", "reason": "logout"})

    history_path = fakefs["tracking"] / "missioncontrol" / "history.jsonl"
    assert history_path.exists()
    entries = [json.loads(line) for line in history_path.read_text().splitlines() if line.strip()]
    assert len(entries) == 1
    e = entries[0]
    assert e["type"] == "session"
    assert e["session_type"] == "execution"
    assert "Auto-closed at SessionEnd (logout)" in e["topic"]


def test_only_one_session_finalized_at_a_time(fakefs):
    """Multiple clock files present — finalize only the requested one."""
    _seed_clock(fakefs, "sess-keep")
    target = _seed_clock(fakefs, "sess-target")

    result = _run_hook(fakefs, {"session_id": "sess-target", "reason": "logout"})
    assert result.returncode == 0
    assert not target.exists()
    assert (fakefs["clocks_dir"] / "sess-keep.json").exists()
