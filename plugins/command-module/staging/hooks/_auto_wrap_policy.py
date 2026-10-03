"""Guards shared by the installed Stop and UserPromptSubmit wrap hooks."""

import json
import re
from datetime import datetime
from pathlib import Path


def prompt_kind(prompt):
    if not isinstance(prompt, str):
        return "other"
    prompt = prompt.strip()
    if prompt.startswith("<task-notification"):
        return "task_notification"
    if re.match(r"^(?:/|\$)(?:command-module:)?wrap-up(?=\s|$)", prompt):
        return "manual_wrap"
    if re.search(r"<command-name>\s*/(?:command-module:)?wrap-up\s*</command-name>", prompt):
        return "manual_wrap"
    if re.fullmatch(
        r"(?:please\s+)?(?:wrap\s+up(?:\s+(?:this|the|our)\s+(?:session|conversation|chat))?"
        r"|wrap\s+this\s+up)(?:\s+(?:now|for\s+today))?[.!]?", prompt, re.I,
    ):
        return "manual_wrap"
    return "other"


def last_prompt_kind(transcript_path):
    """Read only the transcript tail; never guess completion from assistant prose."""
    if not transcript_path:
        return "other"
    try:
        with Path(transcript_path).open("rb") as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell() - 400_000))
            lines = stream.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return "other"
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(entry, dict):
            continue
        # Claude transcripts use user/message; Codex rollouts use response_item/payload.
        if entry.get("type") == "response_item":
            message = entry.get("payload") or {}
            if not isinstance(message, dict):
                continue
            if message.get("type") != "message" or message.get("role") != "user":
                continue
        elif entry.get("type") == "user":
            if entry.get("isMeta") or "toolUseResult" in entry:
                continue
            origin = entry.get("origin") or {}
            if isinstance(origin, dict) and origin.get("kind") == "task-notification":
                return "task_notification"
            message = entry.get("message") or {}
        else:
            continue
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") in ("text", "input_text")
            )
        return prompt_kind(content)
    return "other"


def cancel_manual_wrap(clock, now):
    """Cancel the auto arm and establish cooldown without closing the user's clock."""
    clock["wrap_armed_at"] = None
    clock["last_nudge_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    clock["last_nudge_tool_count"] = int(clock.get("tool_count") or 0)
    clock["last_manual_wrap_tool_count"] = int(clock.get("tool_count") or 0)
    clock["last_manual_wrap_turn_count"] = int(clock.get("turn_count") or 0)


def cooldown_active(clock, now, minutes):
    # A completed manual wrap stays quiet even after the cooldown expires.
    # One acknowledgement turn is allowed; tools or a further discussion release it.
    manual_count = clock.get("last_manual_wrap_tool_count")
    if manual_count is not None:
        try:
            new_tools = int(clock.get("tool_count") or 0) > int(manual_count)
            new_turns = int(clock.get("turn_count") or 0) > int(clock.get("last_manual_wrap_turn_count") or 0) + 1
            if not new_tools and not new_turns:
                return True
        except (ValueError, TypeError):
            pass
    last_nudge = clock.get("last_nudge_at")
    if not last_nudge:
        return False
    try:
        since = (now - datetime.fromisoformat(last_nudge)).total_seconds() / 60
        previous_count = clock.get("last_nudge_tool_count")
        # Old clocks without a snapshot receive the cooldown rather than re-nudging.
        new_work = previous_count is not None and int(clock.get("tool_count") or 0) > int(previous_count)
        return since < minutes and not new_work
    except (ValueError, TypeError):
        return False


def before_stop(clock, data, now):
    kind = last_prompt_kind(data.get("transcript_path") or clock.get("transcript_path"))
    if data.get("stop_hook_active") or kind == "task_notification":
        return True
    if clock.get("manual_wrap_requested") or kind == "manual_wrap":
        cancel_manual_wrap(clock, now)
        clock["manual_wrap_requested"] = False
        return True
    return False


def before_prompt(clock, data, now):
    kind = prompt_kind(data.get("prompt"))
    if kind == "task_notification":
        return kind
    clock["manual_wrap_requested"] = kind == "manual_wrap"
    if kind == "manual_wrap":
        cancel_manual_wrap(clock, now)
    return kind
