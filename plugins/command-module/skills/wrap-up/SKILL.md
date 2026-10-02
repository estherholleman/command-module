---
name: wrap-up
description: "Wrap up this session and update all tracking files. Use when the user says 'wrap up', 'end session', 'wrap this up', or wants to finalize session state and commit changes."
---

# Wrap Up

Finalize the current session by updating tracking files and committing changes.

## Context

Tracking data lives in `/Users/esther/prog/missioncontrol/tracking/{repo-name}/` -- determine the repo name from the current working directory.

This session's clock (if any) lives at `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json`. Other conversations have their own clocks in the same directory; do not touch them.

### Optional session ID

- If the user requests `--no-clock` (or says to wrap up without checking a clock), skip all clock operations even if a session ID is available.
- Otherwise resolve `clock_session_id` once: use an explicit `--session-id <id>` or the ID the user supplies for this conversation, then a nonempty `$CODEX_THREAD_ID`, then a nonempty `$CLAUDE_SESSION_ID`.
- Use the same resolved ID throughout wrap-up and pass it explicitly to `/co` if clocking out. Do not reselect an ID during the flow.
- In each shell call that uses `${clock_session_id}`, bind the resolved value with proper shell quoting; assignments from earlier tool calls may not persist.
- Before using an ID in a file path, require it to match `^[A-Za-z0-9][A-Za-z0-9._-]*$`. If it is invalid, report that clock checking was skipped and continue wrap-up.
- If no ID is available, say: "No session ID is available; skipping the clock check. Tracking updates and commits will continue." Do not ask for an ID unless the user specifically wants clock handling.

Never infer an ID from the repo name, recent transcripts, or other clock files. Without an ID, do not read, create, or delete any clock file, including `.active-clocks/.json`. Do not claim there is no running clock when the check was skipped.

## Workflow

### Step 1: Gather state

Read these in parallel:

- `/Users/esther/prog/missioncontrol/tracking/{repo}/tasks/index.json` -- current task state
- `/Users/esther/prog/missioncontrol/tracking/{repo}/status.json` -- current briefing
- `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json` -- only when clock checking is enabled and a valid ID was resolved
- Run `git status` -- check for uncommitted changes

### Step 1.5: Clock check (this session only)

Skip this step when clock checking is disabled or no valid ID was resolved.

If `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json` exists:

- Calculate elapsed minutes from the start timestamp to now
- Tell the user: "You have a clock running on **{repo}** since {start_time} ({X} minutes). Want to clock out?"
- **If yes**: run the `/co --session-id <resolved-id>` flow — derive session_type from conversation context, propose title and details, write the CSV row (with `session_id` set to the resolved ID), append to `history.jsonl`, and delete only this session's clock file
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

### Step 3.5: Repo-specific wrap-up steps

If the repo's `CLAUDE.md` or `AGENTS.md` has a section `## Bij wrap-up` or `## At wrap-up`, carry out those steps now, before the commit. They hold work that only that repo needs at the end of a session, such as keeping a project index up to date. Repos without such a section skip this step.

### Step 4: Commit

If there are uncommitted changes in the current repo, stage and commit with a clear message. Commit tracking file changes in missioncontrol separately if needed.

### Step 5: Report

Show a brief summary of what was updated. If the clock check was skipped, include that fact and the reason.

## Rules

- **Only this conversation's clock is in scope.** Sibling sessions' clock files in `.active-clocks/` are owned by their conversations.
- **Session IDs are optional for wrap-up.** A skipped clock check must be reported, but it does not block tracking updates, repo-specific steps, or commits.
