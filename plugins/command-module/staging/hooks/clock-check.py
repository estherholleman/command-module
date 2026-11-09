#!/usr/bin/env python3
"""Report unresolved conversation clocks. Never close, repair or delete them."""
import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

CLOCK_CHECK_REPORT_ONLY = True
DEFAULT_ROOT = Path("/Users/esther/prog/missioncontrol")


def local_time(value):
    """Normalize offset-aware, Z and naive timestamps to the Mac's local time."""
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone().replace(tzinfo=None) if parsed.tzinfo else parsed
    except (ValueError, TypeError):
        return None


def inspect_clock(path, now):
    row = {"file": path.name, "session_id": path.stem,
           "state": "unresolved", "needs_review": True, "reasons": []}
    try:
        if path.is_symlink():
            raise ValueError("Symlink clock preserved without following it")
        clock = json.loads(path.read_text())
        if not isinstance(clock, dict):
            raise ValueError("Clock is not a JSON object")
    except (OSError, ValueError) as exc:
        row["reasons"] = [str(exc)]
        return row
    for key in ("session_id", "repo", "project", "title", "start", "last_activity"):
        if isinstance(clock.get(key), str):
            row[key] = clock[key]
    start = local_time(clock.get("start"))
    last = local_time(clock.get("last_activity"))
    opened = local_time(clock.get("opened_at"))
    if not opened:
        row["reasons"].append("Missing or invalid opened_at; preserve for format review")
    if any(value and value > now for value in (opened, start, last)):
        row["reasons"].append("Timestamp is in the future")
    if clock.get("start") is not None and start is None:
        row["reasons"].append("Invalid start timestamp")
    accrued = clock.get("accrued_seconds", 0)
    if isinstance(accrued, bool) or not isinstance(accrued, (int, float)) or accrued < 0:
        row["reasons"].append("Invalid accrued work; preserve for review")
    elif start is None and accrued:
        row["reasons"].append("Accrued work exists without an open span")
    if last and start and last < start:
        row["reasons"].append("Last activity is before the current span start")
    if start is None and clock.get("start") is None and opened and not row["reasons"]:
        row["state"] = "wrapped_idle" if clock.get("wrapped_at") else "armed_not_started"
        row["needs_review"] = False
        row["reasons"] = ["No open work span; clock preserved"]
        return row
    if start:
        if start.date() < now.date():
            row["reasons"].append("Clock began on an earlier day")
        if last is None:
            row["reasons"].append("No verified last activity; session may still be running")
        elif (now - last).total_seconds() > 3600:
            row["reasons"].append("No recorded activity in the past hour; this does not establish completion")
    if not row["reasons"]:
        row["state"] = "recent_activity"
        row["needs_review"] = False
        row["reasons"] = ["Recent activity; session completion is unknown"]
    return row


def build_report(root, now=None):
    now = now or datetime.now()
    if now.tzinfo:
        now = now.astimezone().replace(tzinfo=None)
    directory = root / "tracking" / ".active-clocks"
    errors = []
    try:
        paths = sorted(path for path in directory.iterdir() if path.name.endswith(".json"))
        clocks = [inspect_clock(path, now) for path in paths if not path.name.startswith(".")]
    except FileNotFoundError:
        clocks = []
    except OSError as exc:
        clocks = []
        errors.append(str(exc))
    return {
        "version": 1, "checked_at_local": now.isoformat(timespec="seconds"),
        "policy": "Report only. No clocks or time records are changed. Active and unknown sessions remain open.",
        "review_count": sum(c["needs_review"] for c in clocks),
        "clock_count": len(clocks), "clocks": clocks, "errors": errors,
    }


def markdown(report):
    lines = ["# Conversation clock check", "", "Checked: " + report["checked_at_local"], "",
             report["policy"], "",
             f'{report["review_count"]} clock(s) need review; {report["clock_count"]} clock(s) inspected.',
             "", "Use the conversation's /co or wrap-up only when its work has actually ended.",
             "Missing activity is not proof that a session is finished. Do not infer or duplicate time.", ""]
    for row in report["clocks"]:
        lines += [f'## {row.get("title") or row.get("repo") or row["session_id"]}',
                  f'- Conversation: {row["session_id"]}',
                  f'- State: {row["state"]}',
                  f'- Start: {row.get("start", "not started")}',
                  f'- Last recorded activity: {row.get("last_activity", "unknown")}']
        lines += ["- " + reason for reason in row["reasons"]]
        lines += [""]
    lines += ["Read error: " + error for error in report["errors"]]
    return "\n".join(lines) + "\n"


def atomic_report(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mission-control", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--stdout-only", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(args.mission_control)
    if args.stdout_only:
        print(json.dumps(report, indent=2))
    else:
        directory = args.mission_control / "reports" / "clock-check"
        atomic_report(directory / "latest.json", json.dumps(report, indent=2) + "\n")
        atomic_report(directory / "latest.md", markdown(report))
        print(f'[clock-check] {report["checked_at_local"]}: {report["review_count"]} need review, '
              f'{report["clock_count"]} preserved. Report: {directory / "latest.md"}')
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
