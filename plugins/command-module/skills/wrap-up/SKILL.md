---
name: wrap-up
description: "Wrap up this session and update all tracking files. Use when the user says 'wrap up', 'end session', 'wrap this up', or wants to finalize session state and commit changes."
---

# Wrap Up

Finalize the current session by updating tracking files and committing changes.

## Context

Tracking data lives in `missioncontrol/tracking/{repo-name}/` -- determine the repo name from the current working directory.

## Workflow

### Step 1: Gather state

Read these in parallel:

- `missioncontrol/tracking/{repo}/tasks/index.json` -- current task state
- `missioncontrol/tracking/{repo}/status.json` -- current briefing
- Run `git status` -- check for uncommitted changes

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
