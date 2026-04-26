"""
Tests for session-start-clock.py.

Run from the repo root:
    python3 -m pytest plugins/command-module/tests/hooks/test_session_start_clock.py
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


HOOK_PATH = (
    Path(__file__).resolve().parents[2]
    / "staging" / "hooks" / "session-start-clock.py"
)
SHARED_PATH = HOOK_PATH.parent / "_clock_shared.py"


def _load_shared():
    spec = importlib.util.spec_from_file_location("_clock_shared", SHARED_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fakefs(tmp_path, monkeypatch):
    """Redirect all filesystem constants in _clock_shared at import time so the
    hook subprocess sees them too. We do this by writing a tiny override file
    that the subprocess can pick up via env vars.

    Simpler approach: pass paths via env vars consumed by a thin shim. But the
    plan calls for absolute paths baked in. We monkeypatch by editing the
    shared module on disk... too invasive.

    Pragmatic approach: write a fixtures-style shared module in tmp_path and
    invoke session-start-clock.py with PYTHONPATH overridden. But the hook
    does `from _clock_shared import ...` after `sys.path.insert(0, parent)`.

    Cleanest: copy hook + shared into tmp_path with paths rewritten, then run.
    """
    fs_root = tmp_path / "fakefs"
    fs_root.mkdir()
    mc = fs_root / "missioncontrol"
    (mc / "tracking").mkdir(parents=True)
    (mc / "reports").mkdir(parents=True)
    projects_yaml = mc / "projects.yaml"
    projects_yaml.write_text(
        "clusters:\n"
        "  meta:\n"
        "    description: meta cluster\n"
        "    projects:\n"
        "      - repo: missioncontrol\n"
        "  portbase:\n"
        "    description: portbase cluster\n"
        "    projects:\n"
        "      - repo: portbase\n"
        "      - repo: portfoliostrategyframework\n"
    )

    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()

    shared_text = SHARED_PATH.read_text()
    shared_text = shared_text.replace(
        'MISSION_CONTROL = Path("/Users/esther/prog/missioncontrol")',
        f'MISSION_CONTROL = Path("{mc}")',
    )
    # Rewrite the prog base for repo detection
    shared_text = shared_text.replace(
        'base_path = "/Users/esther/prog"',
        f'base_path = "{fs_root}"',
    )
    (hook_dir / "_clock_shared.py").write_text(shared_text)

    hook_text = HOOK_PATH.read_text()
    (hook_dir / "session-start-clock.py").write_text(hook_text)

    return {
        "root": fs_root,
        "mc": mc,
        "tracking": mc / "tracking",
        "clocks_dir": mc / "tracking" / ".active-clocks",
        "legacy_clock": mc / "tracking" / ".active-clock.json",
        "hook": hook_dir / "session-start-clock.py",
        "hook_dir": hook_dir,
    }


def _run_hook(fakefs, stdin_payload, env_file=None, extra_env=None):
    env = os.environ.copy()
    if env_file is not None:
        env["CLAUDE_ENV_FILE"] = str(env_file)
    else:
        env.pop("CLAUDE_ENV_FILE", None)
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, str(fakefs["hook"])],
        input=json.dumps(stdin_payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def _make_session_dir(fakefs, repo_name="missioncontrol"):
    repo_dir = fakefs["root"] / repo_name
    repo_dir.mkdir(exist_ok=True)
    return repo_dir


def test_fresh_startup_creates_clock_and_writes_env(fakefs, tmp_path):
    repo_dir = _make_session_dir(fakefs, "missioncontrol")
    env_file = tmp_path / "env-file"

    result = _run_hook(
        fakefs,
        {"session_id": "sess-A", "cwd": str(repo_dir), "source": "startup"},
        env_file=env_file,
    )

    assert result.returncode == 0, result.stderr
    clock = json.loads((fakefs["clocks_dir"] / "sess-A.json").read_text())
    assert clock["session_id"] == "sess-A"
    assert clock["repo"] == "missioncontrol"
    assert clock["cluster"] == "meta"
    assert clock["cwd"] == str(repo_dir)
    assert clock["source_at_start"] == "startup"
    assert "CLAUDE_SESSION_ID=sess-A" in env_file.read_text()
    out = json.loads(result.stdout)
    assert "Auto clocked in: missioncontrol (meta)" in out["hookSpecificOutput"]["additionalContext"]


def test_legacy_active_clock_is_discarded(fakefs, tmp_path):
    repo_dir = _make_session_dir(fakefs, "missioncontrol")
    env_file = tmp_path / "env-file"
    fakefs["legacy_clock"].write_text(json.dumps(
        {"repo": "old-repo", "cluster": "old", "start": "2026-04-01T09:00:00", "date": "2026-04-01"}
    ))

    result = _run_hook(
        fakefs,
        {"session_id": "sess-B", "cwd": str(repo_dir), "source": "startup"},
        env_file=env_file,
    )

    assert result.returncode == 0, result.stderr
    assert not fakefs["legacy_clock"].exists()
    assert "discarded legacy clock" in result.stderr
    assert "old-repo" in result.stderr  # payload logged
    # New per-session clock written
    assert (fakefs["clocks_dir"] / "sess-B.json").exists()


def test_resume_with_existing_clock_is_idempotent(fakefs, tmp_path):
    repo_dir = _make_session_dir(fakefs, "missioncontrol")
    env_file = tmp_path / "env-file"
    fakefs["clocks_dir"].mkdir(parents=True, exist_ok=True)
    existing = {
        "session_id": "sess-C",
        "repo": "missioncontrol",
        "cluster": "meta",
        "start": "2026-04-25T08:00:00",
        "date": "2026-04-25",
        "cwd": str(repo_dir),
        "source_at_start": "startup",
    }
    clock_path = fakefs["clocks_dir"] / "sess-C.json"
    clock_path.write_text(json.dumps(existing))
    original_bytes = clock_path.read_bytes()

    result = _run_hook(
        fakefs,
        {"session_id": "sess-C", "cwd": str(repo_dir), "source": "clear"},
        env_file=env_file,
    )

    assert result.returncode == 0, result.stderr
    # Clock unchanged
    assert clock_path.read_bytes() == original_bytes
    out = json.loads(result.stdout)
    assert "already running" in out["hookSpecificOutput"]["additionalContext"]


def test_env_file_dedupes_on_re_invocation(fakefs, tmp_path):
    repo_dir = _make_session_dir(fakefs, "missioncontrol")
    env_file = tmp_path / "env-file"

    _run_hook(fakefs, {"session_id": "sess-D", "cwd": str(repo_dir), "source": "startup"}, env_file=env_file)
    _run_hook(fakefs, {"session_id": "sess-D", "cwd": str(repo_dir), "source": "clear"}, env_file=env_file)

    occurrences = env_file.read_text().count("CLAUDE_SESSION_ID=sess-D")
    assert occurrences == 1


def test_unmapped_cwd_falls_back_to_unassigned(fakefs, tmp_path):
    # Outside the fake "/Users/esther/prog" base
    out_of_tree = tmp_path / "elsewhere"
    out_of_tree.mkdir()
    env_file = tmp_path / "env-file"

    result = _run_hook(
        fakefs,
        {"session_id": "sess-E", "cwd": str(out_of_tree), "source": "startup"},
        env_file=env_file,
    )

    assert result.returncode == 0, result.stderr
    clock = json.loads((fakefs["clocks_dir"] / "sess-E.json").read_text())
    assert clock["cluster"] == "unassigned"
    assert clock["repo"] == out_of_tree.name


def test_missing_claude_env_file_warns_but_succeeds(fakefs):
    repo_dir = _make_session_dir(fakefs, "missioncontrol")

    result = _run_hook(
        fakefs,
        {"session_id": "sess-F", "cwd": str(repo_dir), "source": "startup"},
        env_file=None,
    )

    assert result.returncode == 0, result.stderr
    assert "CLAUDE_ENV_FILE unset" in result.stderr
    assert (fakefs["clocks_dir"] / "sess-F.json").exists()


def test_malformed_stdin_fails_loud(fakefs, tmp_path):
    env = os.environ.copy()
    env["CLAUDE_ENV_FILE"] = str(tmp_path / "env-file")
    result = subprocess.run(
        [sys.executable, str(fakefs["hook"])],
        input="not json {{{",
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 1
    assert "stdin is not valid JSON" in result.stderr


def test_missing_session_id_fails_loud(fakefs, tmp_path):
    repo_dir = _make_session_dir(fakefs, "missioncontrol")
    env_file = tmp_path / "env-file"

    result = _run_hook(
        fakefs,
        {"cwd": str(repo_dir), "source": "startup"},  # no session_id
        env_file=env_file,
    )

    assert result.returncode == 1
    assert "missing session_id" in result.stderr


def test_concurrent_legacy_migration_tolerant(fakefs, tmp_path):
    """If two SessionStart hooks run nearly-simultaneously, both should tolerate
    a missing legacy file."""
    repo_dir = _make_session_dir(fakefs, "missioncontrol")
    env_file = tmp_path / "env-file"
    fakefs["legacy_clock"].write_text("{}")

    # First migration
    r1 = _run_hook(
        fakefs,
        {"session_id": "sess-G1", "cwd": str(repo_dir), "source": "startup"},
        env_file=env_file,
    )
    # Legacy already gone — second hook tolerates
    r2 = _run_hook(
        fakefs,
        {"session_id": "sess-G2", "cwd": str(repo_dir), "source": "startup"},
        env_file=env_file,
    )

    assert r1.returncode == 0
    assert r2.returncode == 0
    assert (fakefs["clocks_dir"] / "sess-G1.json").exists()
    assert (fakefs["clocks_dir"] / "sess-G2.json").exists()
    assert not fakefs["legacy_clock"].exists()
