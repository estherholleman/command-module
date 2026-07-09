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

# A gap between consecutive engaged moments longer than this means the previous
# burst ended — the intervening time is idle, not work, and must not be billed.
# On such a gap the engagement model SEALS the current sub-span into
# `accrued_seconds` and opens a fresh one (idle excluded, pre-gap work preserved).
# No single sub-span can contain more than IDLE_GAP of idle.
IDLE_GAP_SECONDS = 30 * 60

# The clock starts on the first of: a substantive tool (immediate) OR this many
# engaged assistant turns (design/discussion/reading that never touches a file
# still counts). A turn-based start backdates to the first turn. Threshold 2
# means a single one-shot question never bills; two+ turns is a real session.
START_TURN_THRESHOLD = 2


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
    """True once real work began (a substantive tool or turn set `start`)."""
    return bool(clock.get("start"))


def honest_span(clock: dict, now: Optional[datetime] = None):
    """Return (window_start, end_dt, minutes) for a STARTED, non-legacy clock.

    Returns None when there is nothing honest to write (legacy, or armed but
    never started). `end` is `last_activity` when present, else `start`.

    `minutes` = closed sub-spans (`accrued_seconds`) + the current open sub-span,
    so "work -> idle -> work" is billed as work only. `window_start` is the first
    sub-span start since the last wrap (`work_start`), so the CSV window brackets
    the whole engaged session; `minutes` may be < (end - window_start) because
    idle gaps between sub-spans are excluded.
    """
    if is_legacy(clock) or not has_started(clock):
        return None
    start_dt = datetime.fromisoformat(clock["start"])
    la = clock.get("last_activity")
    end_dt = datetime.fromisoformat(la) if la else start_dt
    if now is not None and end_dt > now:
        end_dt = now
    open_secs = max(0.0, (end_dt - start_dt).total_seconds())
    total_secs = int(clock.get("accrued_seconds", 0)) + open_secs
    minutes = max(MIN_ROW_MINUTES, int(total_secs / 60))
    ws = clock.get("work_start") or clock["start"]
    window_start = datetime.fromisoformat(ws)
    if window_start > end_dt:
        window_start = start_dt
    return window_start, end_dt, minutes


# ---------------------------------------------------------------------------
# Engagement model — turns AND tools drive the honest clock (2026-07-09)
# ---------------------------------------------------------------------------
# The clock STARTS on the first of: (a) a substantive tool (Edit/Write/Bash/
# NotebookEdit — immediate), or (b) the START_TURN_THRESHOLD-th engaged assistant
# turn (design/discussion/reading that never touches a file still counts, backdated
# to the first turn). Once started, both tools and turns advance `last_activity`;
# an idle gap > IDLE_GAP seals the current sub-span into `accrued_seconds` and opens
# a new one — so long collaborative sessions are neither over-billed (idle excluded)
# nor under-billed (the pre-2026-07-09 code silently DISCARDED pre-gap work on a
# start-reset; this preserves it).

def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def begin_span(clock: dict, at_iso: str, now_iso: str) -> None:
    """Open a fresh work span (null -> started). Resets accrual: a null `start`
    means no session is currently open, so any lingering accrual belongs to an
    already-wrapped session and must not bleed into the new span. This makes the
    clock self-healing regardless of how faithfully /wrap-up cleared the fields."""
    clock["start"] = at_iso
    clock["work_start"] = at_iso
    clock["last_activity"] = now_iso
    clock["accrued_seconds"] = 0


def register_engagement(clock: dict, now_dt: datetime, is_tool: bool) -> None:
    """Fold one engaged moment (a tool call or a turn-end) into the clock in place.

    Caller persists. Defensive: assumes a dict; callers wrap in try/except so a
    hook never breaks a turn. `is_tool=True` for the PostToolUse heartbeat (a real
    action -> immediate start), `is_tool=False` for the Stop turn-end (counts toward
    the turn threshold and, once started, advances the tail)."""
    now_iso = _fmt(now_dt)
    if not has_started(clock):
        if is_tool:
            begin_span(clock, now_iso, now_iso)  # a real action starts immediately
        else:
            if not clock.get("first_turn_at"):
                clock["first_turn_at"] = now_iso
            clock["turn_count"] = int(clock.get("turn_count", 0)) + 1
            if clock["turn_count"] >= START_TURN_THRESHOLD:
                at_iso = clock["first_turn_at"]
                try:
                    first_dt = datetime.fromisoformat(at_iso)
                    if (now_dt - first_dt).total_seconds() > IDLE_GAP_SECONDS:
                        at_iso = now_iso  # never backdate across an idle gap
                except Exception:
                    at_iso = now_iso
                begin_span(clock, at_iso, now_iso)
    else:
        prev = clock.get("last_activity")
        if prev:
            try:
                prev_dt = datetime.fromisoformat(prev)
                gap = (now_dt - prev_dt).total_seconds()
            except Exception:
                prev_dt, gap = None, 0
            if gap > IDLE_GAP_SECONDS and prev_dt is not None:
                # Seal the just-ended sub-span into accrual, open a fresh one.
                try:
                    span = (prev_dt - datetime.fromisoformat(clock["start"])).total_seconds()
                except Exception:
                    span = 0
                if span > 0:
                    clock["accrued_seconds"] = int(clock.get("accrued_seconds", 0)) + int(span)
                clock["start"] = now_iso
        clock["last_activity"] = now_iso
        if not is_tool:
            clock["turn_count"] = int(clock.get("turn_count", 0)) + 1
    if is_tool:
        clock["tool_count"] = int(clock.get("tool_count", 0)) + 1


# ---------------------------------------------------------------------------
# Transcript reconciliation — ground-truth engaged time (2026-07-09)
# ---------------------------------------------------------------------------
# The live clock can still under-count if hooks partially fail or a burst stays
# below the turn threshold. A session's transcript carries a timestamp on every
# user/assistant message — the true "when was I engaged" signal, independent of
# which tools fired. Finalizers take max(clock, transcript) so nothing is lost;
# this is the continuous backstop that does NOT depend on running /evening.

def _to_local_naive(ts: Optional[str]) -> Optional[datetime]:
    """ISO ts (may be 'Z'/offset-aware or naive) -> naive LOCAL datetime.

    Transcript timestamps are UTC with a 'Z' suffix; py3.9 fromisoformat can't
    parse 'Z', so normalize it, then convert an aware value to local wall time to
    match the clock's naive-local convention."""
    if not ts:
        return None
    s = ts.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def reconcile_from_transcript(transcript_path, since: Optional[datetime] = None,
                              now: Optional[datetime] = None):
    """Reconstruct honest engaged-minutes from a transcript's message timestamps.

    Clusters user/assistant message times, splits on gaps > IDLE_GAP, and sums each
    cluster's span. `since` (pass the clock's `wrapped_at`) excludes already-wrapped
    bursts so a finalizer never double-counts. Returns {minutes, first, last, spans}
    or None when the transcript is unreadable or holds no countable engagement."""
    if not transcript_path:
        return None
    try:
        text = Path(transcript_path).read_text()
    except Exception:
        return None
    times = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") not in ("user", "assistant"):
            continue
        if obj.get("isSidechain"):
            continue
        dt = _to_local_naive(obj.get("timestamp"))
        if dt is None:
            continue
        if since is not None and dt < since:
            continue
        if now is not None and dt > now:
            continue
        times.append(dt)
    if len(times) < 2:
        return None
    times.sort()
    total = 0.0
    cluster_start = times[0]
    prev = times[0]
    spans = 1
    for t in times[1:]:
        if (t - prev).total_seconds() > IDLE_GAP_SECONDS:
            total += (prev - cluster_start).total_seconds()
            spans += 1
            cluster_start = t
        prev = t
    total += (prev - cluster_start).total_seconds()
    minutes = int(total / 60)
    if minutes < MIN_ROW_MINUTES:
        return None
    return {"minutes": minutes, "first": times[0], "last": times[-1], "spans": spans}


def finalize_row(clock: dict, now: Optional[datetime] = None):
    """Blend the live honest span with a transcript reconstruction of the UNWRAPPED
    tail for the SessionEnd / sweep finalizers. Returns
    (window_start, end_dt, minutes, method) or None to drain (no honest time).

    method in {"clock", "reconciled", "reconstructed"} — recorded in the row
    details so /evening (or a human) can see how the minutes were derived."""
    if now is None:
        now = datetime.now()
    span = honest_span(clock, now=now)
    since = None
    wa = clock.get("wrapped_at")
    if wa:
        try:
            since = datetime.fromisoformat(wa)
        except Exception:
            since = None
    recon = None
    if not is_legacy(clock):
        recon = reconcile_from_transcript(clock.get("transcript_path"), since=since, now=now)

    if span is None:
        # Armed-only / legacy: only a transcript can rescue it (rare — a real
        # session would have crossed the turn threshold and started).
        if recon is not None:
            return recon["first"], recon["last"], recon["minutes"], "reconstructed"
        return None
    window_start, end_dt, minutes = span
    if recon is not None and recon["minutes"] > minutes:
        return recon["first"], recon["last"], recon["minutes"], "reconciled"
    return window_start, end_dt, minutes, "clock"


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
