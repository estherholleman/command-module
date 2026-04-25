"""
Tests for the Phase 3 auto-close-clock.py (multi-file orphan sweep).

Run from the repo root:
    python3 -m pytest plugins/command-module/tests/hooks/test_auto_close_clock.py
"""

import csv
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest


HOOK_PATH = (
    Path(__file__).resolve().parents[2]
    / "staging" / "hooks" / "auto-close-clock.py"
)
SHARED_PATH = HOOK_PATH.parent / "_clock_shared.py"


@pytest.fixture
def fakefs(tmp_path, monkeypatch):
    fs_root = tmp_path / "fakefs"
    mc = fs_root / "missioncontrol"
    (mc / "tracking").mkdir(parents=True)
    (mc / "reports").mkdir(parents=True)
    (mc / "projects.yaml").write_text(
        "clusters:\n  meta:\n    projects:\n      - repo: missioncontrol\n"
    )

    # Load _clock_shared with rewritten MISSION_CONTROL constant
    shared_text = SHARED_PATH.read_text().replace(
        'MISSION_CONTROL = Path("/Users/esther/prog/missioncontrol")',
        f'MISSION_CONTROL = Path("{mc}")',
    )
    shared_module_path = tmp_path / "_clock_shared.py"
    shared_module_path.write_text(shared_text)
    spec = importlib.util.spec_from_file_location("_clock_shared", shared_module_path)
    shared_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shared_mod)
    sys.modules["_clock_shared"] = shared_mod

    # Load the hook with its own _clock_shared dependency resolved to the patched module
    hook_spec = importlib.util.spec_from_file_location("auto_close_clock", HOOK_PATH)
    hook_mod = importlib.util.module_from_spec(hook_spec)
    # Make sure the hook's `import _clock_shared` resolves to our patched copy
    monkeypatch.syspath_prepend(str(tmp_path))
    hook_spec.loader.exec_module(hook_mod)

    return {
        "shared": shared_mod,
        "hook": hook_mod,
        "tracking": mc / "tracking",
        "clocks_dir": mc / "tracking" / ".active-clocks",
        "timesheet": mc / "reports" / "timesheet.csv",
    }


def _write_clock(fakefs, session_id, *, start_dt, repo="missioncontrol",
                 cluster="meta"):
    fakefs["clocks_dir"].mkdir(parents=True, exist_ok=True)
    path = fakefs["clocks_dir"] / f"{session_id}.json"
    path.write_text(json.dumps({
        "session_id": session_id,
        "repo": repo,
        "cluster": cluster,
        "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "date": start_dt.strftime("%Y-%m-%d"),
        "cwd": "/whatever",
        "source_at_start": "startup",
    }))
    return path


def _read_csv_rows(fakefs):
    if not fakefs["timesheet"].exists():
        return []
    with open(fakefs["timesheet"]) as f:
        return list(csv.DictReader(f))


def test_empty_directory_is_noop(fakefs, capsys):
    fakefs["hook"].main()
    out = capsys.readouterr().out
    assert "no active clocks" in out
    assert not fakefs["timesheet"].exists()


def test_missing_directory_is_noop(fakefs, capsys):
    # .active-clocks/ never created
    fakefs["hook"].main()
    out = capsys.readouterr().out
    assert "no active clocks" in out


def test_today_clock_before_2000_caps_at_2000(fakefs):
    today_morning = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
    path = _write_clock(fakefs, "sess-today", start_dt=today_morning)

    fakefs["hook"].main()

    assert not path.exists()
    rows = _read_csv_rows(fakefs)
    assert len(rows) == 1
    r = rows[0]
    assert r["source"] == "auto-close-20h"
    assert r["session_id"] == "sess-today"
    assert r["start"] == "09:15"
    # End is either 20:00 (sweep ran before 20:00) or "now" (sweep ran after).
    # Both branches produce a non-empty end string.
    assert r["end"]


def test_stale_clock_yesterday_pre_2000_ends_at_2000(fakefs):
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_15 = yesterday.replace(hour=15, minute=30, second=0, microsecond=0)
    _write_clock(fakefs, "sess-stale", start_dt=yesterday_15)

    fakefs["hook"].main()

    rows = _read_csv_rows(fakefs)
    assert len(rows) == 1
    r = rows[0]
    assert r["source"] == "auto-close-stale"
    assert r["session_id"] == "sess-stale"
    assert r["start"] == "15:30"
    assert r["end"] == "20:00"
    expected_minutes = (20 - 15) * 60 + (0 - 30)  # 4h30m = 270min
    assert int(r["minutes"]) == expected_minutes


def test_stale_clock_yesterday_post_2000_uses_30min_fallback(fakefs):
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_2230 = yesterday.replace(hour=22, minute=30, second=0, microsecond=0)
    _write_clock(fakefs, "sess-late", start_dt=yesterday_2230)

    fakefs["hook"].main()

    rows = _read_csv_rows(fakefs)
    assert len(rows) == 1
    r = rows[0]
    assert r["source"] == "auto-close-stale"
    assert r["start"] == "22:30"
    assert r["end"] == "23:00"
    assert int(r["minutes"]) == 30


def test_multiple_clocks_handled_independently(fakefs):
    today_morning = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_14 = yesterday.replace(hour=14, minute=0, second=0, microsecond=0)

    _write_clock(fakefs, "sess-A", start_dt=today_morning, repo="missioncontrol")
    _write_clock(fakefs, "sess-B", start_dt=yesterday_14, repo="missioncontrol")

    fakefs["hook"].main()

    rows = _read_csv_rows(fakefs)
    assert len(rows) == 2
    sids = {r["session_id"] for r in rows}
    assert sids == {"sess-A", "sess-B"}
    sources = {r["session_id"]: r["source"] for r in rows}
    assert sources["sess-A"] == "auto-close-20h"
    assert sources["sess-B"] == "auto-close-stale"
    assert not list(fakefs["clocks_dir"].glob("*.json"))


def test_failure_on_one_clock_does_not_block_others(fakefs):
    today_morning = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    good = _write_clock(fakefs, "sess-good", start_dt=today_morning)
    bad = fakefs["clocks_dir"] / "sess-bad.json"
    bad.write_text("not valid json")

    fakefs["hook"].main()

    # Good clock finalized
    rows = _read_csv_rows(fakefs)
    assert any(r["session_id"] == "sess-good" for r in rows)
    # Bad clock left in place for next run
    assert bad.exists()
    assert not good.exists()


def test_csv_row_has_11_columns_with_session_id(fakefs):
    today_morning = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    _write_clock(fakefs, "sess-Z", start_dt=today_morning)

    fakefs["hook"].main()

    with open(fakefs["timesheet"]) as f:
        reader = csv.reader(f)
        header = next(reader)
        row = next(reader)
    assert header[-1] == "session_id"
    assert len(header) == 11
    assert len(row) == 11
    assert row[-1] == "sess-Z"


def test_history_entry_written(fakefs):
    today_morning = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    _write_clock(fakefs, "sess-H", start_dt=today_morning, repo="missioncontrol")

    fakefs["hook"].main()

    history = fakefs["tracking"] / "missioncontrol" / "history.jsonl"
    assert history.exists()
    entries = [json.loads(line) for line in history.read_text().splitlines() if line.strip()]
    assert len(entries) == 1
    assert entries[0]["session_type"] == "execution"


def test_clock_file_only_deleted_on_successful_writes(fakefs, monkeypatch):
    """If write_csv_row raises, clock file must remain so the next run can retry."""
    today_morning = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    path = _write_clock(fakefs, "sess-fail", start_dt=today_morning)

    def boom(*args, **kwargs):
        raise IOError("disk full")

    # The hook's _clock_shared was loaded from sys.modules during fixture setup
    monkeypatch.setattr(fakefs["shared"], "write_csv_row", boom)

    # All-failures path exits with status 1 — caught here.
    with pytest.raises(SystemExit) as exc_info:
        fakefs["hook"].main()
    assert exc_info.value.code == 1

    assert path.exists()  # not deleted on failure


def test_sweep_function_returns_lists(fakefs):
    today_morning = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    _write_clock(fakefs, "sess-1", start_dt=today_morning)
    _write_clock(fakefs, "sess-2", start_dt=today_morning)

    closed, failed = fakefs["hook"].sweep()

    assert len(closed) == 2
    assert len(failed) == 0
    assert {c["session_id"] for c in closed} == {"sess-1", "sess-2"}
