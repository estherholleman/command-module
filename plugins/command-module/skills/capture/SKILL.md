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

Read `missioncontrol/tracking/{repo}/tasks/index.json` to find the next available task ID.

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

Present the proposed task — including the drafted `origin` — and ask for confirmation before writing. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the task details and wait for the user's reply before proceeding.

If `origin` is missing or generic, ask for it explicitly: "What surfaced this task — which conversation, observation, or client situation made it necessary?" Do not proceed to Step 4 until the user has supplied (or confirmed) a substantive `origin`.

### Step 4: Write task files

On confirmation, write the following in parallel:

- Create `missioncontrol/tracking/{repo}/tasks/T00N.md` with YAML frontmatter (including `origin`) and notes body
- Add the entry to `missioncontrol/tracking/{repo}/tasks/index.json` (including `origin`)
- Append a `task_created` entry to `missioncontrol/tracking/{repo}/history.jsonl`
