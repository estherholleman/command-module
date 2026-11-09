#!/usr/bin/env python3
"""Create a compatible manual conversation clock, preserving existing clocks."""
import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_ROOT = Path("/Users/esther/prog/missioncontrol")
SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def local_naive(value):
    return value.astimezone().replace(tzinfo=None) if value.tzinfo else value


def new_clock(session_id, cwd, attribution, now=None):
    if not SESSION_ID.fullmatch(session_id or ""):
        raise ValueError("Supply a valid conversation session ID")
    now = local_naive(now or datetime.now())
    stamp = now.isoformat(timespec="seconds")
    return {
        "session_id": session_id,
        **{key: attribution.get(key, "") for key in ("repo", "cluster", "project", "group")},
        "attribution": attribution.get("source", attribution.get("attribution", "")),
        "cwd": str(cwd), "date": now.date().isoformat(),
        "source_at_start": "manual-ci", "opened_at": stamp,
        "start": stamp, "work_start": stamp, "last_activity": stamp,
        "accrued_seconds": 0, "tool_count": 0, "turn_count": 0,
        "first_turn_at": None, "wrapped_at": None, "last_nudge_at": None,
        "wrap_armed_at": None, "watcher_pid": None,
    }


def create_clock(directory, clock):
    """Publish atomically without replacing a concurrent or existing clock."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (clock["session_id"] + ".json")
    if path.exists():
        return False, json.loads(path.read_text())
    fd, tmp = tempfile.mkstemp(prefix="." + path.name, suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(clock, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            return False, json.loads(path.read_text())
    finally:
        os.unlink(tmp)
    return True, json.loads(path.read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--repo")
    parser.add_argument("--project")
    parser.add_argument("--tasks")
    parser.add_argument("--mission-control", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    if not SESSION_ID.fullmatch(args.session_id):
        parser.error("Invalid session ID; no clock was read or changed")
    directory = args.mission_control / "tracking" / ".active-clocks"
    path = directory / (args.session_id + ".json")
    if path.exists():
        print(json.dumps({"created": False, "clock": json.loads(path.read_text())}))
        return 0
    command = ["/usr/bin/python3", str(args.mission_control / "scripts" / "attribution.py"), "resolve"]
    command += ["--repo", args.repo] if args.repo else ["--cwd", str(args.cwd)]
    for name in ("project", "tasks"):
        if getattr(args, name):
            command += ["--" + name, getattr(args, name)]
    attribution = json.loads(subprocess.check_output(command, text=True))
    clock = new_clock(args.session_id, args.cwd, attribution)
    created, saved = create_clock(directory, clock)
    print(json.dumps({"created": created, "clock": saved}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
