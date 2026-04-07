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
- Suggested status (`backlog`, `todo`, `next`, `in_progress` -- infer from context)
- Suggested priority (`high`, `medium`, `low`)
- Relevant tags
- Any useful notes

### Step 3: Confirm with user

Present the proposed task and ask for confirmation before writing. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the task details and wait for the user's reply before proceeding.

### Step 4: Write task files

On confirmation, write the following in parallel:

- Create `missioncontrol/tracking/{repo}/tasks/T00N.md` with YAML frontmatter and notes body
- Add the entry to `missioncontrol/tracking/{repo}/tasks/index.json`
- Append a `task_created` entry to `missioncontrol/tracking/{repo}/history.jsonl`
