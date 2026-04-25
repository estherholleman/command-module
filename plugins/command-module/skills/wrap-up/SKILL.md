---
name: wrap-up
description: "Wrap up this session and update all tracking files. Use when the user says 'wrap up', 'end session', 'wrap this up', or wants to finalize session state and commit changes."
---

# Wrap Up

Finalize the current session by updating tracking files and committing changes.

## Context

Tracking data lives in `/Users/esther/prog/missioncontrol/tracking/{repo-name}/` -- determine the repo name from the current working directory.

This session's clock (if any) lives at `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json`. Other conversations have their own clocks in the same directory; do not touch them.

## Workflow

### Step 1: Gather state

Read these in parallel:

- `/Users/esther/prog/missioncontrol/tracking/{repo}/tasks/index.json` -- current task state
- `/Users/esther/prog/missioncontrol/tracking/{repo}/status.json` -- current briefing
- `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` -- this session's clock (if any)
- Run `git status` -- check for uncommitted changes

If `$CLAUDE_SESSION_ID` is empty, surface a specific error and stop:

> ERROR: `CLAUDE_SESSION_ID` is empty. SessionStart hook did not set it (CLAUDE_ENV_FILE mechanism). Cannot identify this conversation's clock. Aborting.

### Step 1.5: Clock check (this session only)

If `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` exists:

- Calculate elapsed minutes from the start timestamp to now
- Tell the user: "You have a clock running on **{repo}** since {start_time} ({X} minutes). Want to clock out?"
- **If yes**: run the `/co` flow — derive session_type from conversation context, propose title and details, write the CSV row (with `session_id` populated), append to `history.jsonl`, and delete only this session's clock file
- **If no**: proceed with the rest of wrap-up without clocking out (the user may keep working after wrap-up)

Do NOT auto-close the clock. Always ask first.

If the file does not exist, no other conversation's clock is shown and no prompt is issued — wrap-up proceeds.

### Step 2: Identify changes

Scan the conversation for tasks worked on, status changes, and any uncaptured work. If there are uncaptured items, note them in the summary rather than blocking for confirmation.

### Step 3: Update tracking files

Write these in parallel:

- Update each modified task's `tasks/T00N.md` frontmatter (status, updated date)
- Update `tasks/index.json` with matching changes (and any new task entries)
- Append to `history.jsonl`: session entry + `status_change` entries + `task_created` entries
- Write `status.json`: curated briefing with summary, highlights, active/blocked/upcoming tasks

### Step 4: Commit

If there are uncommitted changes in the current repo, stage and commit with a clear message. Commit tracking file changes in missioncontrol separately if needed.

### Step 5: Report

Show a brief summary of what was updated.

## Rules

- **Only this conversation's clock is in scope.** Sibling sessions' clock files in `.active-clocks/` are owned by their conversations.
- **Fail loud on missing `$CLAUDE_SESSION_ID`.** Do not silently treat the absence as "no clock" — that was the silent-miss bug.
