"""
Tests for migrate-timesheet-schema.py.

Run from the repo root:
    python3 -m pytest plugins/command-module/tests/hooks/

The script under test is invoked by importing its module via importlib (its
filename contains hyphens, so it cannot be imported with normal `import`).
"""

import csv
import importlib.util
import sys
import threading
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "migrate-timesheet-schema.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("migrate_timesheet_schema", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


migrate_module = _load_module()
migrate = migrate_module.migrate
EXPECTED_HEADER = migrate_module.EXPECTED_HEADER
NEW_COLUMN = migrate_module.NEW_COLUMN


def _write_csv(path: Path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def _read_csv(path: Path):
    with open(path, newline="") as f:
        return list(csv.reader(f))


def test_no_file_returns_no_file(tmp_path):
    missing = tmp_path / "does-not-exist.csv"
    assert migrate(missing) == "no-file"


def test_header_only_csv(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    _write_csv(csv_path, [EXPECTED_HEADER])

    assert migrate(csv_path) == "migrated"

    rows = _read_csv(csv_path)
    assert rows[0] == EXPECTED_HEADER + [NEW_COLUMN]
    assert len(rows) == 1


def test_csv_with_data_rows_gets_empty_session_id(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    sample_row_a = [
        "2026-04-20", "09:00", "10:30", "portbase", "portbase",
        "execution", "90", "Implement feature", "Some details", "clock",
    ]
    sample_row_b = [
        "2026-04-21", "14:00", "15:00", "missioncontrol", "meta",
        "planning", "60", "Review", "", "manual",
    ]
    _write_csv(csv_path, [EXPECTED_HEADER, sample_row_a, sample_row_b])

    assert migrate(csv_path) == "migrated"

    rows = _read_csv(csv_path)
    assert rows[0] == EXPECTED_HEADER + [NEW_COLUMN]
    assert rows[1] == sample_row_a + [""]
    assert rows[2] == sample_row_b + [""]


def test_already_migrated_is_noop(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    migrated_header = EXPECTED_HEADER + [NEW_COLUMN]
    sample_row = [
        "2026-04-20", "09:00", "10:30", "portbase", "portbase",
        "execution", "90", "Implement feature", "Some details", "clock", "abc-123",
    ]
    _write_csv(csv_path, [migrated_header, sample_row])
    original_bytes = csv_path.read_bytes()

    assert migrate(csv_path) == "already-migrated"
    assert csv_path.read_bytes() == original_bytes


def test_unexpected_header_fails_loud(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    bad_header = ["date", "start", "end", "extra_col"]
    _write_csv(csv_path, [bad_header, ["2026-04-20", "09:00", "10:30", "x"]])
    original_bytes = csv_path.read_bytes()

    with pytest.raises(ValueError, match="Unexpected header"):
        migrate(csv_path)

    assert csv_path.read_bytes() == original_bytes


def test_short_row_fails_loud_without_clobbering(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    short_row = ["2026-04-20", "09:00", "10:30"]
    _write_csv(csv_path, [EXPECTED_HEADER, short_row])
    original_bytes = csv_path.read_bytes()

    with pytest.raises(ValueError, match="line 2"):
        migrate(csv_path)

    assert csv_path.read_bytes() == original_bytes


def test_empty_file_fails_loud(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    csv_path.write_text("")

    with pytest.raises(ValueError, match="empty"):
        migrate(csv_path)


def test_atomic_rename_does_not_leave_temp(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    _write_csv(csv_path, [EXPECTED_HEADER, [
        "2026-04-20", "09:00", "10:30", "portbase", "portbase",
        "execution", "90", "Title", "Details", "clock",
    ]])

    migrate(csv_path)

    leftover = list(tmp_path.glob(".timesheet-migrate-*.csv"))
    assert leftover == []


def test_concurrent_invocations_are_safe(tmp_path):
    """Two concurrent migrators race; one wins, the other becomes a no-op
    on the next run. Final state must be a valid migrated CSV."""
    csv_path = tmp_path / "timesheet.csv"
    rows = [EXPECTED_HEADER] + [
        ["2026-04-20", "09:00", "10:00", "portbase", "portbase",
         "execution", "60", f"row {i}", "", "clock"]
        for i in range(5)
    ]
    _write_csv(csv_path, rows)

    results = []
    errors = []

    def runner():
        try:
            results.append(migrate(csv_path))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=runner) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final_rows = _read_csv(csv_path)
    assert final_rows[0] == EXPECTED_HEADER + [NEW_COLUMN]
    assert len(final_rows) == 6
    for row in final_rows[1:]:
        assert len(row) == 11
        assert row[-1] == ""


def test_blank_line_between_rows_is_dropped(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    sample_row = [
        "2026-04-20", "09:00", "10:00", "portbase", "portbase",
        "execution", "60", "Title", "", "clock",
    ]
    # Manually write CSV with a blank line in the middle (real-world cruft)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(EXPECTED_HEADER)
        writer.writerow(sample_row)
        f.write("\n")
        writer.writerow(sample_row)

    assert migrate(csv_path) == "migrated"

    rows = _read_csv(csv_path)
    assert rows[0] == EXPECTED_HEADER + [NEW_COLUMN]
    # Blank line dropped; two real data rows kept.
    assert len(rows) == 3
    assert rows[1] == sample_row + [""]
    assert rows[2] == sample_row + [""]


def test_quoted_fields_with_commas_preserved(tmp_path):
    csv_path = tmp_path / "timesheet.csv"
    row_with_comma = [
        "2026-04-20", "09:00", "10:00", "portbase", "portbase",
        "execution", "60", "Comma, in title", "Detail; with; semis", "clock",
    ]
    _write_csv(csv_path, [EXPECTED_HEADER, row_with_comma])

    assert migrate(csv_path) == "migrated"

    rows = _read_csv(csv_path)
    assert rows[1] == row_with_comma + [""]
