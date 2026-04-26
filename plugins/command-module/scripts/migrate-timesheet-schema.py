#!/usr/bin/env python3
"""
One-shot migration: extend timesheet.csv with a session_id column.

Reads the existing CSV, appends `session_id` to the header (empty value for all
existing rows), and writes the result back via temp file + atomic rename.

Idempotent: if the header already contains `session_id`, exits with no changes.

Usage:
    python3 migrate-timesheet-schema.py [path/to/timesheet.csv]

Default path: /Users/esther/prog/missioncontrol/reports/timesheet.csv
"""

import csv
import os
import sys
import tempfile
from pathlib import Path

DEFAULT_CSV = Path("/Users/esther/prog/missioncontrol/reports/timesheet.csv")
EXPECTED_HEADER = [
    "date", "start", "end", "repo", "cluster",
    "session_type", "minutes", "title", "details", "source",
]
NEW_COLUMN = "session_id"


def migrate(csv_path: Path) -> str:
    """Return one of: 'migrated', 'already-migrated', 'no-file'."""
    if not csv_path.exists():
        return "no-file"

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"{csv_path} is empty (no header row)")

    header = rows[0]

    if NEW_COLUMN in header:
        return "already-migrated"

    if header != EXPECTED_HEADER:
        raise ValueError(
            f"Unexpected header in {csv_path}.\n"
            f"  expected: {EXPECTED_HEADER}\n"
            f"  found:    {header}"
        )

    expected_cols = len(EXPECTED_HEADER)
    new_data_rows = []
    for i, row in enumerate(rows[1:], start=2):
        if not row:
            # Stray blank line — skip silently, do not preserve in output.
            continue
        if len(row) != expected_cols:
            raise ValueError(
                f"{csv_path} line {i}: expected {expected_cols} columns, "
                f"got {len(row)}: {row!r}"
            )
        new_data_rows.append(row + [""])

    new_rows = [header + [NEW_COLUMN]] + new_data_rows

    fd, tmp_path_str = tempfile.mkstemp(
        prefix=".timesheet-migrate-", suffix=".csv", dir=str(csv_path.parent)
    )
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(new_rows)
        os.replace(tmp_path, csv_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    return "migrated"


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV

    try:
        result = migrate(csv_path)
    except Exception as exc:
        print(f"[migrate-timesheet-schema] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if result == "no-file":
        print(f"[migrate-timesheet-schema] {csv_path} does not exist; nothing to do.")
    elif result == "already-migrated":
        print(f"[migrate-timesheet-schema] Already migrated; no changes to {csv_path}.")
    else:
        print(f"[migrate-timesheet-schema] Migrated {csv_path}: appended '{NEW_COLUMN}' column.")


if __name__ == "__main__":
    main()
