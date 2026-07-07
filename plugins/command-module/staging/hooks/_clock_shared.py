"""
Shared helpers for the per-session clock hooks.

This module lives at ~/.claude/hooks/_clock_shared.py once installed.
It is staged in command-module (plugins/command-module/staging/hooks/) for
review; the actual deployment is performed by
`plugins/command-module/scripts/install-phase2.sh`.

Used by:
- session-start-clock.py   (SessionStart — ARM the clock)
- work-heartbeat.py        (PostToolUse — START the clock on first real action)
- auto-wrap-gate.py        (Stop — nudge the agent to auto-wrap)
- session-end-clock.py     (SessionEnd — honest finalize / drain)
- auto-close-clock.py      (launchd sweep — honest finalize / drain)

Honest-clock model (2026-07-07 rewrite — see docs/tracking-protocol.md):
A clock has three phases.
  1. ARMED   — SessionStart wrote it with `opened_at` set and `start: null`.
               No timesheet consequence yet.
  2. STARTED — the first substantive tool (Edit/Write/Bash/NotebookEdit) fired;
               work-heartbeat set `start` = that moment and bumps `last_activity`.
  3. WRAPPED — /wrap-up (auto or manual) wrote the entry for [start, last_activity]
               and RESET the clock (`start: null`, `wrapped_at` = now) so the next
               burst of work opens a fresh honest span in the same session.

Truthful duration = last_activity - start (real work span), NOT
tab-open -> tab-close. A clock that never STARTED (armed only) writes NO row —
that is what kills the ghost/phantom entries.

Legacy clocks (pre-rewrite: have `start` but no `opened_at`) can't be recovered
into an honest span, so finalizers DRAIN them without writing a row.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

MISSION_CONTROL = Path("/Users/esther/prog/missioncontrol")
TRACKING_DIR = MISSION_CONTROL / "tracking"
CLOCKS_DIR = TRACKING_DIR / ".active-clocks"
LEGACY_CLOCK_FILE = TRACKING_DIR / ".active-clock.json"
TIMESHEET = MISSION_CONTROL / "reports" / "timesheet.csv"
PROJECTS_PATH = MISSION_CONTROL / "projects.yaml"

CSV_HEADER = [
    "date", "start", "end", "repo", "cluster",
    "session_type", "minutes", "title", "details", "source",
    "session_id",
]

# Minimum honest work span (minutes) worth writing a row for. Below this a
# finalizer drains the clock silently — a 30-second accidental tool call is
# not a work session.
MIN_ROW_MINUTES = 1

# A gap between consecutive actions longer than this means the previous burst
# ended — the intervening time is idle, not work, and must not be billed.
# The heartbeat RESETS `start` to now on such a gap (a fresh honest span), and
# the Stop gate refuses to advance `last_activity` across it. This is the hard
# anti-inflation guard: no single span can contain more than IDLE_GAP of idle.
IDLE_GAP_SECONDS = 30 * 60


def clock_path_for(session_id: str) -> Path:
    return CLOCKS_DIR / f"{session_id}.json"


# ---------------------------------------------------------------------------
# Honest-clock lifecycle helpers
# ---------------------------------------------------------------------------

def is_legacy(clock: dict) -> bool:
    """True for a pre-rewrite clock (has `start` but was never armed).

    New clocks always carry `opened_at`. Its absence means the `start` field
    holds a tab-open time, not a real work-start — unrecoverable, so drain.
    """
    return "opened_at" not in clock


def has_started(clock: dict) -> bool:
    """True once real work began (first substantive tool set `start`)."""
    return bool(clock.get("start"))


def honest_span(clock: dict, now: Optional[datetime] = None):
    """Return (start_dt, end_dt, minutes) for a STARTED, non-legacy clock.

    Returns None when there is nothing honest to write (legacy, or armed but
    never started). `end` is `last_activity` when present, else `start`
    (a started-but-idle clock -> ~MIN_ROW_MINUTES).
    """
    if is_legacy(clock) or not has_started(clock):
        return None
    start_dt = datetime.fromisoformat(clock["start"])
    la = clock.get("last_activity")
    end_dt = datetime.fromisoformat(la) if la else start_dt
    if now is not None and end_dt > now:
        end_dt = now
    minutes = max(MIN_ROW_MINUTES, int((end_dt - start_dt).total_seconds() / 60))
    return start_dt, end_dt, minutes


def write_clock_atomic(clock_path: Path, clock: dict) -> None:
    """Atomically (tmp + os.replace) write a clock file."""
    clock_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = clock_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(clock, indent=2) + "\n")
    os.replace(tmp_path, clock_path)


# ---------------------------------------------------------------------------
# projects.yaml -> repo/cluster resolution (unchanged)
# ---------------------------------------------------------------------------

def load_repo_cluster_map() -> dict:
    """Build repo_name -> cluster_name mapping from projects.yaml."""
    try:
        import yaml
    except ImportError:
        return parse_projects_simple()

    with open(PROJECTS_PATH) as f:
        data = yaml.safe_load(f)

    mapping = {}
    for cluster_name, cluster in data.get("clusters", {}).items():
        for project in cluster.get("projects", []):
            mapping[project["repo"]] = cluster_name
        for client in cluster.get("clients", []):
            mapping[client["repo"]] = cluster_name
    return mapping


def parse_projects_simple() -> dict:
    """Minimal projects.yaml parser without PyYAML dependency."""
    mapping = {}
    current_cluster = None
    with open(PROJECTS_PATH) as f:
        for line in f:
            stripped = line.strip()
            if line.startswith("  ") and not line.startswith("    ") and stripped.endswith(":"):
                key = stripped.rstrip(":")
                if key not in ("description", "role", "time_allocation", "projects", "clients"):
                    current_cluster = key
            if "repo:" in stripped and current_cluster:
                repo = stripped.split("repo:")[1].strip().strip('"').strip("'")
                if repo:
                    mapping[repo] = current_cluster
    return mapping


def detect_repo_from_cwd(cwd: str, mapping: Optional[dict] = None) -> tuple[Optional[str], Optional[str]]:
    """Return (repo, cluster) from a cwd. Both None if cwd is outside ~/prog."""
    base_path = "/Users/esther/prog"
    if not cwd.startswith(base_path):
        return None, None

    relative = cwd[len(base_path):].lstrip("/")
    repo_name = relative.split("/")[0] if relative else None
    if not repo_name:
        return None, None

    if mapping is None:
        mapping = load_repo_cluster_map()
    cluster = mapping.get(repo_name)
    return repo_name, cluster


def resolve_repo_and_cluster(cwd: str) -> tuple[str, str]:
    """Like detect_repo_from_cwd but returns a never-None pair.

    Per brainstorm D5: when cwd doesn't map to a known repo, fall back to
    repo=basename(cwd), cluster='unassigned'. Never silently skip clock-in.
    """
    repo, cluster = detect_repo_from_cwd(cwd)
    if repo and cluster:
        return repo, cluster
    fallback_repo = Path(cwd).name or "unknown"
    return fallback_repo, "unassigned"


# ---------------------------------------------------------------------------
# Row / history writers (unchanged shape)
# ---------------------------------------------------------------------------

def write_csv_row(*, date, start_hm, end_hm, repo, cluster, session_type,
                  minutes, title, details, source, session_id=""):
    TIMESHEET.parent.mkdir(parents=True, exist_ok=True)
    need_header = not TIMESHEET.exists()
    with open(TIMESHEET, "a", newline="") as f:
        writer = csv.writer(f)
        if need_header:
            writer.writerow(CSV_HEADER)
        writer.writerow([
            date, start_hm, end_hm, repo, cluster,
            session_type, minutes, title, details, source,
            session_id,
        ])


def write_history_entry(*, repo, date, start_iso, session_type, title, details, minutes):
    history = TRACKING_DIR / repo / "history.jsonl"
    history.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "type": "session",
        "date": date,
        "timestamp": start_iso,
        "session_type": session_type,
        "topic": title,
        "summary": details,
        "duration_hours": round(minutes / 60, 2),
    }
    if history.exists() and history.stat().st_size > 0:
        with open(history, "rb") as rf:
            rf.seek(-1, 2)
            last_byte = rf.read(1)
        if last_byte != b"\n":
            with open(history, "a") as f:
                f.write("\n")
    with open(history, "a") as f:
        f.write(json.dumps(entry) + "\n")


def append_env_var(env_file: Path, key: str, value: str) -> bool:
    """Append KEY=VALUE to env_file if not already present.

    Returns True if appended, False if already present (or env_file is empty/missing
    and the line was newly added — still True).
    """
    line = f"{key}={value}"
    if env_file.exists():
        existing = env_file.read_text().splitlines()
        if line in existing:
            return False
    with open(env_file, "a") as f:
        f.write(line + "\n")
    return True
