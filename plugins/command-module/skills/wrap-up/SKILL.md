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
- `missioncontrol/tracking/.active-clock.json` -- check for active time clock
- Run `git status` -- check for uncommitted changes

### Step 1.5: Clock check

If `.active-clock.json` exists (a time clock is running):

- Calculate elapsed minutes from the start timestamp to now
- Tell the user: "You have a clock running on **{repo}** since {start_time} ({X} minutes). Want to clock out?"
- **If yes**: run the `/co` flow — derive session_type from conversation context, propose title and details, write CSV row to `missioncontrol/reports/timesheet.csv`, append to history.jsonl, and delete the state file
- **If no**: proceed with the rest of wrap-up without clocking out (the user may keep working after wrap-up)

Do NOT auto-close the clock. Always ask first.

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
