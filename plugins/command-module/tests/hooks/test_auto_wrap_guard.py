"""Regression checks for manual wrap-up and repeated auto-wrap nudges."""

import importlib.util
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = load_module("auto_wrap_policy", ROOT / "staging/hooks/_auto_wrap_policy.py")
installer = load_module("auto_wrap_installer", ROOT / "scripts/install-auto-wrap-guard.py")
NOW = datetime(2026, 10, 3, 12, 0, 0)


@pytest.mark.parametrize("prompt", [
    "/wrap-up", "/wrap-up --no-clock", "/command-module:wrap-up",
    "$wrap-up --session-id my-chat", "$command-module:wrap-up",
    "<command-name>/command-module:wrap-up</command-name>\n<command-args></command-args>",
    "wrap up", "Please wrap this up.", "Wrap up this session for today",
])
def test_manual_commands_cancel_pending_wrap_without_clocking_out(prompt):
    clock = {"wrap_armed_at": "pending", "start": "2026-10-03T10:00:00",
             "last_activity": "2026-10-03T11:59:00", "tool_count": 17}
    assert policy.before_prompt(clock, {"prompt": prompt}, NOW) == "manual_wrap"
    assert clock["wrap_armed_at"] is None
    assert clock["start"] == "2026-10-03T10:00:00"
    assert clock["last_activity"] == "2026-10-03T11:59:00"
    # Wrap-up's own tools must not make its final response re-arm the hook.
    clock["tool_count"] = 22
    assert policy.before_stop(clock, {}, NOW)
    assert clock["last_nudge_tool_count"] == 22
    assert policy.cooldown_active(clock, NOW + timedelta(minutes=1), 12)


@pytest.mark.parametrize("prompt", [
    "I noticed the wrap up hook fires a lot", "Explain /wrap-up", "/wrap-updated",
    "$wrap-updated", "Implement a feature", "Wrap up skill needs updating", "",
])
def test_ordinary_requests_do_not_suppress_new_work(prompt):
    clock = {"manual_wrap_requested": True}
    assert policy.before_prompt(clock, {"prompt": prompt}, NOW) == "other"
    assert not policy.before_stop(clock, {}, NOW)


def test_turn_timestamp_cannot_bypass_cooldown_but_new_tool_work_can():
    clock = {"last_nudge_at": "2026-10-03T11:58:00", "last_nudge_tool_count": 9,
             "last_activity": "2026-10-03T12:00:00", "tool_count": 9}
    assert policy.cooldown_active(clock, NOW, 12)
    clock["tool_count"] = 10
    assert not policy.cooldown_active(clock, NOW, 12)
    clock["tool_count"] = 9
    assert not policy.cooldown_active(clock, NOW + timedelta(minutes=12), 12)


def test_old_clock_without_tool_snapshot_gets_cooldown():
    clock = {"last_nudge_at": "2026-10-03T11:58:00", "tool_count": 19}
    assert policy.cooldown_active(clock, NOW, 12)


def test_manual_wrap_stays_quiet_after_idle_and_a_thank_you_but_releases_for_new_work():
    clock = {"tool_count": 12, "turn_count": 5}
    policy.cancel_manual_wrap(clock, NOW)
    clock["turn_count"] = 6  # One acknowledgement is not a new work session.
    later = NOW + timedelta(hours=2)
    assert policy.cooldown_active(clock, later, 12)
    clock["tool_count"] = 13
    assert not policy.cooldown_active(clock, later, 12)
    clock["tool_count"] = 12
    clock["turn_count"] = 7  # A continuing discussion also counts as new work.
    assert not policy.cooldown_active(clock, later, 12)


@pytest.mark.parametrize("entry", [
    {"type": "user", "message": {"content": "/command-module:wrap-up"}},
    {"type": "user", "message": {"content": [{"type": "text", "text": "$wrap-up"}]}},
    {"type": "response_item", "payload": {"type": "message", "role": "user",
        "content": [{"type": "input_text", "text": "$wrap-up --no-clock"}]}},
])
def test_manual_request_detected_from_claude_and_codex_transcripts(tmp_path, entry):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("\n".join(json.dumps(row) for row in [
        entry, {"type": "user", "isMeta": True, "message": {"content": "hook feedback"}},
        {"type": "user", "toolUseResult": {}, "message": {"content": "tool result"}},
        {"type": "assistant", "message": {"content": "Wrapped up"}},
    ]))
    clock = {"wrap_armed_at": "pending", "tool_count": 4}
    assert policy.before_stop(clock, {"transcript_path": str(transcript)}, NOW)
    assert clock["wrap_armed_at"] is None


@pytest.mark.parametrize("notification", [
    {"type": "user", "message": {"content": "<task-notification>ABORT</task-notification>"}},
    {"type": "user", "origin": {"kind": "task-notification"},
     "message": {"content": "watcher finished"}},
])
def test_background_completions_never_rearm_or_consume_pending_wrap(tmp_path, notification):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(json.dumps(notification))
    clock = {"wrap_armed_at": "pending", "tool_count": 5}
    assert policy.before_stop(clock, {"transcript_path": str(transcript)}, NOW)
    assert clock == {"wrap_armed_at": "pending", "tool_count": 5}
    assert policy.before_prompt(clock, {"prompt": "<task-notification>ABORT"}, NOW) == "task_notification"
    assert clock["wrap_armed_at"] == "pending"


def test_latest_real_request_releases_manual_wrap_suppression(tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("\n".join(json.dumps({"type": "user", "message": {"content": prompt}})
                                     for prompt in ["/wrap-up", "Now implement another feature"]))
    assert not policy.before_stop({}, {"transcript_path": str(transcript)}, NOW)


def test_missing_or_malformed_transcript_does_not_break_hook(tmp_path):
    assert policy.last_prompt_kind(tmp_path / "missing") == "other"
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("broken json\n[]\nnull\n")
    assert policy.last_prompt_kind(transcript) == "other"


def test_unknown_hook_layout_is_rejected():
    with pytest.raises(ValueError):
        installer.patch_hook("print('unrelated hook')", "auto-wrap-gate.py")
