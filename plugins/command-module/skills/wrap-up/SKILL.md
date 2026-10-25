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

The time entry is the only thing wrap-up asks about. Everything else (clocking out, session type, title, details, tracking updates, commit) runs without confirmation.

### Step 1: Suggest the time (first action)

Skip this step when clock checking is disabled or no valid ID was resolved.

Before reading anything else, run the estimator on this session's clock file:

```bash
python3 scripts/suggest-minutes.py "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json"
```

If the clock file does not exist, skip to Step 2 and mention the skipped clock-out in the report. If the clock never started (`clock_minutes` and `transcript_minutes` are both 0), skip the time entry the same way.

The script prints `suggested_minutes`, which is the larger of the honest clock (main-thread activity, idle gaps over 30 minutes excluded) and the engaged time in the main transcript plus its subagent transcripts. It also prints `span_minutes`, the whole window from `start` to now including pauses.

Ask one question with the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini):

- Question: "Log **{suggested_minutes} min** on **{repo}** ({start}–{end})?"
- Options: "{suggested_minutes} min (suggested)", and "{span_minutes} min (whole window, incl. pauses)" when `span_minutes` is more than 15 minutes higher. The user types any other number through the free-text option.

Without a question tool, print the same line and wait for a reply; a bare number is the corrected minutes, and anything affirmative accepts the suggestion. Accept answers like "90", "1h30" or "2 hours" and convert them to minutes.

### Step 2: Gather state

Read these in parallel:

- `/Users/esther/prog/missioncontrol/tracking/{repo}/tasks/index.json` -- current task state
- `/Users/esther/prog/missioncontrol/tracking/{repo}/status.json` -- current briefing
- Run `git status` -- check for uncommitted changes

### Step 2.5: Clock out (this session only)

Skip this step when Step 1 was skipped.

Run the `co` skill flow with `--session-id <resolved-id> --minutes <confirmed-minutes>`. With `--minutes`, `co` derives session type, title and details from the conversation and writes them without asking, writes the CSV row (with `session_id` set to the resolved ID) and the `history.jsonl` entry, and deletes only this session's clock file. Treat this as the session entry for Step 4, so `history.jsonl` gets one session entry, not two.

### Step 3: Identify changes

Scan the conversation for tasks worked on, status changes, and any uncaptured work. If there are uncaptured items, note them in the summary rather than blocking for confirmation.

### Step 4: Update tracking files

Write these in parallel:

- Update each modified task's `tasks/T00N.md` frontmatter (status, updated date)
- Update `tasks/index.json` with matching changes (and any new task entries)
- Append to `history.jsonl`: `status_change` entries + `task_created` entries, plus a session entry only when Step 2.5 did not write one
- Write `status.json`: curated briefing with summary, highlights, active/blocked/upcoming tasks

### Step 4.5: Repo-specific wrap-up steps

If the repo's `CLAUDE.md` or `AGENTS.md` has a section `## Bij wrap-up` or `## At wrap-up`, carry out those steps now, before the commit. They hold work that only that repo needs at the end of a session, such as keeping a project index up to date. Repos without such a section skip this step.

### Step 5: Commit

If there are uncommitted changes in the current repo, stage and commit with a clear message. Commit tracking file changes in missioncontrol separately if needed.

### Step 6: Report

Show a brief summary of what was updated, starting with the logged time entry (minutes, session type, title). If the clock check was skipped, include that fact and the reason.

## Rules

- **Only this conversation's clock is in scope.** Sibling sessions' clock files in `.active-clocks/` are owned by their conversations.
- **Ask only about time.** Session type, title and details are derived, not confirmed; the user can correct them afterwards or in the evening reconcile.
- **Session IDs are optional for wrap-up.** A skipped clock check must be reported, but it does not block tracking updates, repo-specific steps, or commits.
