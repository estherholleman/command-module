---
name: capture
description: "Capture a task from the current conversation. Use when the user says 'capture this', 'save this as a task', 'add a task', or wants to record work items discovered during a session."
---

# Capture

Capture a task from the current conversation into the project's tracking system.

## Context

Tracking data lives in `missioncontrol/tracking/{repo-name}/` -- determine the repo name from the current working directory.

## Workflow

### Step 1: Read current task state

Read `missioncontrol/tracking/{repo}/tasks/index.json` for the current tasks. The next ID is allocated in Step 4, just before writing.

### Step 1.5: Check for an existing task

Look through the repo's open tasks and its tasks updated in the last 30 days, and the tasks in the folder where the new task would go (`python3 /Users/esther/prog/missioncontrol/scripts/tree_outline.py --project "<title>"` lists them). When the item is an update of an existing task, update that task instead of creating a duplicate: change its title, description or status where needed and append a dated note to its file, then report which task was updated and why. Do not ask whether it is a duplicate. When it is unclear, capture the new task and name the possible duplicate in the report. The rule is "Check for an existing task first" in `/Users/esther/prog/missioncontrol/docs/tracking-protocol.md`.

### Step 2: Draft the task

Based on recent conversation context (or `$ARGUMENTS` if provided), draft a task entry with:

- A clear, actionable task description
- **An `origin` field** (mandatory) — one to three sentences capturing *why this task exists*: the conversation, observation, or incident that surfaced it, including which client / pipeline / context triggered it. Not what the task does (that's `task`), but what made it necessary.
  - Good: "Surfaced while analysing MLtours forecasts: the Market column has no directionality for MLtours (unlike for ES, where it does). Revintel must therefore allow the directionality column to be configurable per client."
  - Bad: "From conversation." / "User asked for this." / Empty.
- Suggested status (`backlog`, `todo`, `next`, `in_progress` -- infer from context)
- Suggested priority (`high`, `medium`, `low`)
- Relevant tags
- Any useful notes

If the conversation context is too thin to draft a real `origin`, **do not invent one**. In Step 3, explicitly ask the user for the trigger/context before writing. Capturing a task with a vague origin defeats the purpose of the field.

### Step 3: Confirm with user

When Step 1.5 found an existing task that this item updates, the proposal is that update (which task, and what changes), not a new task. Present the proposed task — including the drafted `origin` — and ask for confirmation before writing. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the task details and wait for the user's reply before proceeding.

If `origin` is missing or generic, ask for it explicitly: "What surfaced this task — which conversation, observation, or client situation made it necessary?" Do not proceed to Step 4 until the user has supplied (or confirmed) a substantive `origin`.

### Step 4: Write task files

On confirmation, read `missioncontrol/tracking/{repo}/tasks/index.json` fresh and list the `tasks/T*.md` files on disk. The new ID is one more than the highest ID found in either, because another session may have written a task file before its index entry. Then write:

- Create `missioncontrol/tracking/{repo}/tasks/T00N.md` with YAML frontmatter (including `origin`) and notes body
- Add the entry to `missioncontrol/tracking/{repo}/tasks/index.json` (including `origin`), merged into the fresh copy, keeping the file's encoding and indent
- Append a `task_created` entry to `missioncontrol/tracking/{repo}/history.jsonl` (ensure a trailing newline first), with `placed_in` when Step 5 places the task

For an update of an existing task, write that task's file and its index entry instead (both read fresh, `updated` set to today), append a `status_change` line when its status changed, and skip Step 5, because the task already has its place.

### Step 5: Place the task in the tree

Place the new task in the portfolio tree, following "Placing tasks in the tree" in `/Users/esther/prog/missioncontrol/docs/tracking-protocol.md`. This step asks nothing, and nothing depends on `/capture` running, because `/wrap-up` places the tasks it creates and the Finder inbox catches the rest.

1. Run `python3 /Users/esther/prog/missioncontrol/scripts/tree_outline.py --folders-only --repo {repo}` (or `--project "<title>"`). If it reports no portfolio tree yet, skip this step.
2. Choose the deepest folder that fits inside the right project (or the project folder itself, or a folder marked `ongoing`), or a same-repo parent task when the new task is a step of it. Never the root, a group or kind folder, or an archived or trashed folder.
3. Read the folder's file in `missioncontrol/tracking/portfolio/tasks/` fresh, append `"{repo}:T0NN"` to its `subtasks` (or add the list after `tags`) and set `updated`; give its entry in `missioncontrol/tracking/portfolio/tasks/index.json` the same list and date with an exact text edit; append a `node_moved` line to `missioncontrol/tracking/portfolio/history.jsonl` as the protocol shows.
4. When no folder fits with confidence, leave the task unplaced and say in one line that it waits in the Finder inbox. Never create a folder without asking.

Report the task's ID and where it was placed.
