"""
Shared helpers for the per-session clock hooks.

This module lives at ~/.claude/hooks/_clock_shared.py once installed.
It is staged in this repo for review; the actual deployment is performed
by `plugins/command-module/scripts/install-phase2.sh`.

Used by:
- session-start-clock.py (Phase 2)
- session-end-clock.py (Phase 2)
- auto-close-clock.py (Phase 3 — once refactored to share)
"""

import csv
import json
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


def clock_path_for(session_id: str) -> Path:
    return CLOCKS_DIR / f"{session_id}.json"


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
