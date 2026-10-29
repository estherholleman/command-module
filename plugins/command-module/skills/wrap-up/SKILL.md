---
name: wrap-up
description: "Wrap up this session and update all tracking files. Use when the user says 'wrap up', 'end session', 'wrap this up', or wants to finalize session state and commit changes."
---

# Wrap Up

Finalize the current session by updating tracking files and committing changes.

## Context

Tracking data lives in `/Users/esther/prog/missioncontrol/tracking/{repo-name}/`. Determine the repo with the shared resolver, not from the folder name:

```bash
python3 /Users/esther/prog/missioncontrol/scripts/attribution.py resolve --cwd "$PWD"
```

It routes code repos such as `/Users/esther/prog/music` to their tracking repo (`musical-ideas`), worktrees (`.claude/worktrees/*` and sibling worktree folders) to their main repo, and the home folder and chat folders to `unassigned`. When it says `unassigned`, ask which repo the work belongs to (or, in automatic mode, write no tracking files and report it); never create a new `tracking/{name}/` directory for a folder the resolver does not know. If the command fails, fall back to the first folder under `/Users/esther/prog`.

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

The script prints `suggested_minutes`, which is the larger of the honest clock (main-thread activity, with pauses counted by the clock's gap rule: up to 60 minutes in full, longer ones minus the stretches the display was off) and the engaged time in the main transcript plus its subagent transcripts. It also prints `span_minutes`, the whole window from `start` to now including pauses.

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

Run the `co` skill flow with `--session-id <resolved-id> --minutes <confirmed-minutes>`, plus `--project <ref>` when the session touched tasks: get the ref from `python3 /Users/esther/prog/missioncontrol/scripts/attribution.py resolve --repo <repo> --tasks T0NN,T0MM` (its `project` field, the project folder most of those tasks sit under; omit the flag when it is empty). That explicit project is the high-trust path for hours per project and group. With `--minutes`, `co` derives session type, title and details from the conversation and writes them without asking, writes the CSV row (with `session_id` set to the resolved ID) and the `history.jsonl` entry, and deletes only this session's clock file. Treat this as the session entry for Step 4, so `history.jsonl` gets one session entry, not two.

### Step 3: Identify changes

Scan the conversation for tasks worked on, status changes, and any uncaptured work. If there are uncaptured items, note them in the summary rather than blocking for confirmation.

### Step 3.5: Check for an existing task before creating one

Before creating any task, look through the repo's open tasks and its tasks updated in the last 30 days (from the index read in Step 2), and the tasks in the folder where the new task would go (`python3 /Users/esther/prog/missioncontrol/scripts/tree_outline.py --project "<title>"` lists them). When the new item is an update of an existing task, update that task instead of creating a duplicate: change its title, description or status where needed and append a dated note to its file, then say in the report which task was updated and why. Never ask about this. When it is unclear whether the item duplicates an existing task, create the new task and name the possible duplicate in the report. The rule is "Check for an existing task first" in `/Users/esther/prog/missioncontrol/docs/tracking-protocol.md`.

### Step 4: Update tracking files

Two rules come first, because other sessions write the same files while this one runs:

- **Read `tasks/index.json` fresh just before writing it**, not the copy from Step 2. Merge your changes into that fresh copy, change only the entries you touch, and keep the file's encoding (escaped `\uXXXX` or raw UTF-8) and indent.
- **Allocate each new task ID as one more than the highest ID found in `tasks/index.json` or among the `tasks/T*.md` files on disk.** A concurrent session may have written a task file before its index entry. If the file for the chosen ID appears before you write it, take the next one.

Then write these in parallel:

- Update each modified task's `tasks/T00N.md` frontmatter (status, updated date)
- Update `tasks/index.json` with matching changes (and any new task entries)
- Append to `history.jsonl`: `status_change` entries + `task_created` entries, plus a session entry only when Step 2.5 did not write one. A `task_created` line for a task that Step 4.1 places carries `placed_in` (write the task first, place it, then append its line).
- Write `status.json`: curated briefing with summary, highlights, active/blocked/upcoming tasks

### Step 4.1: Place every new task in the tree

Every task this wrap-up creates gets placed in the portfolio tree, in automatic mode too. Esther never files tasks by hand; a task left unplaced shows in the inbox at the top of the Finder. This step never asks a question and never blocks the wrap-up. The full rule is "Placing tasks in the tree" in `/Users/esther/prog/missioncontrol/docs/tracking-protocol.md`.

Skip this step when the wrap-up created no task. A new subtask added under an existing task already has its parent and needs no placement.

1. **Look at the folders.** Run `python3 /Users/esther/prog/missioncontrol/scripts/tree_outline.py --folders-only --repo {repo}`. It prints the projects that hold this repo's tasks, with their folders, `portfolio:T0NN` keys and rollups; when no project holds the repo's tasks yet, it prints every folder. Use `--project "<title>"` instead when this session's work clearly belongs to one project. If the script reports that there is no portfolio tree yet, leave every new task unplaced and say so in one line.
2. **Choose the folder from the task's content and this session's context.** Pick the deepest folder that fits inside the right project, or the project folder itself when none of its folders fits; a folder marked `ongoing` also counts. A task that is a step of an existing task in this repo goes under that task instead (add its bare ID to the parent's `subtasks`, merged from the parent's file). Never place a task in the root, a group folder or a kind folder (Apps, Tools, Engines, Biomorphic design), and never in an archived or trashed folder.
3. **Write the placement, with the same atomic rules as task writes.**
   - Read the folder's file `/Users/esther/prog/missioncontrol/tracking/portfolio/tasks/T0NN.md` fresh. Append `"{repo}:T0NN"` (qualified and double-quoted) to the end of its `subtasks` list, or add `subtasks: ["{repo}:T0NN"]` on the line after `tags` when it has none. Set `updated` to today in the quoting the file already uses.
   - Read `/Users/esther/prog/missioncontrol/tracking/portfolio/tasks/index.json` fresh and give the folder's entry the same `subtasks` list and `updated` date. Edit only that entry, by an exact text edit, so the file keeps its encoding and indent.
   - Ensure `/Users/esther/prog/missioncontrol/tracking/portfolio/history.jsonl` ends with a newline, then append `{"type": "node_moved", "node": "{repo}:T0NN", "from_parent": null, "to_parent": "portfolio:T0NN", "position": <index in the new list>, "date": "YYYY-MM-DD", "timestamp": "YYYY-MM-DDTHH:MM:SS"}`.
   - Put `"placed_in": "portfolio:T0NN"` on the task's `task_created` line in this repo's history (the parent task's `{repo}:T0NN` for a placement under a task).
4. **When no folder fits with confidence, leave the task unplaced.** Do not guess, and do not create a folder. If a folder seems to be missing, name it in the summary as a suggestion.
5. **Record each placement for the report:** the task, the folder's path and key (for example `lytr:T046 → Lytr › Product (portfolio:T031)`), or one line per task left in the inbox with the reason.

### Step 4.2: Check the tracking writes

Run `python3 /Users/esther/prog/missioncontrol/scripts/rebuild-index.py {repo} --dry-run`, and `python3 /Users/esther/prog/missioncontrol/scripts/rebuild-index.py portfolio --dry-run` when Step 4.1 placed a task in a folder. Both should report "already in sync". If one does not and the difference is in an entry this wrap-up wrote, fix that entry so it matches its task file; otherwise mention the drift in the report and leave it.

### Step 4.5: Repo-specific wrap-up steps

If the repo's `CLAUDE.md` or `AGENTS.md` has a section `## Bij wrap-up` or `## At wrap-up`, carry out those steps now, before the commit. They hold work that only that repo needs at the end of a session, such as keeping a project index up to date. Repos without such a section skip this step.

### Step 5: Commit

If there are uncommitted changes in the current repo, stage and commit with a clear message. Commit tracking file changes in missioncontrol separately if needed.

### Step 6: Report

Show a brief summary of what was updated, starting with the logged time entry (minutes, session type, title). If the clock check was skipped, include that fact and the reason. List where each new task was placed (Step 4.1), and give one line for each task left in the Finder inbox. Name each existing task that was updated instead of duplicated, and each possible duplicate that was created anyway (Step 3.5).

## Rules

- **Only this conversation's clock is in scope.** Sibling sessions' clock files in `.active-clocks/` are owned by their conversations.
- **Ask only about time.** Session type, title and details are derived, not confirmed; the user can correct them afterwards or in the evening reconcile.
- **Update instead of duplicating, without asking.** A new item that updates an existing task changes that task; when unsure, create the task and mention the possible duplicate.
- **Placement never asks.** Each new task is placed from its content and the session's context, or left in the Finder inbox when no folder fits with confidence. Folders are never created by the wrap-up.
- **Session IDs are optional for wrap-up.** A skipped clock check must be reported, but it does not block tracking updates, repo-specific steps, or commits.
