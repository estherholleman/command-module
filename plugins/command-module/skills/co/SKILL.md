---
name: co
description: "Clock out to stop tracking time. Use when the user says 'clock out', 'co', 'stop timer', 'stop tracking', or wants to end a timed work session. Derives session type and title from conversation context."
---

# Clock Out

Stop this conversation's time clock, derive session metadata from conversation context, and write the time entry.

## Context

- Per-session clock state: `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json`
- Timesheet CSV: `/Users/esther/prog/missioncontrol/reports/timesheet.csv`
- Attribution resolver (repo, project, group): `python3 /Users/esther/prog/missioncontrol/scripts/attribution.py resolve` (falls back to the `projects.yaml` cluster when the Finder tree has no answer)

## Preamble: resolve session ID

Resolve `clock_session_id` once: use an explicit `--session-id <id>` or the ID the user supplies for this conversation, then a nonempty `$CODEX_THREAD_ID`, then a nonempty `$CLAUDE_SESSION_ID`. Remove `--session-id` and its value before interpreting remaining arguments. When called from wrap-up, use the ID it passes without reselecting it.

## Quick mode (`--minutes <n>`)

Wrap-up passes `--minutes <n>` after the user has confirmed the time. In quick mode:

- Use `<n>` as `minutes` instead of computing elapsed time.
- Use the clock's `work_start` (falling back to `start`) for `start_HH:MM`, and the current local time for `end_HH:MM`.
- Derive session type, title and details from the conversation and write them without asking. Skip the confirmations in Steps 2 and 3 and the long-session check.
- Still resolve an `unassigned` repo in Step 1.5, because the row cannot be filed without one.
- Use the `--project <ref>` that wrap-up passes (the project of the tasks it touched) for the row's `project` and `group`; see Step 1.

Before any clock operation, require a nonempty ID matching `^[A-Za-z0-9][A-Za-z0-9._-]*$`. If no valid ID is available, stop clock handling and report: "Cannot identify this conversation's clock. Supply --session-id <id> or a valid CODEX_THREAD_ID / CLAUDE_SESSION_ID. Wrap-up can still run without a clock check."

Use the same ID for the clock filename and CSV `session_id`. Never infer it from the repo name, recent transcripts, or other clock files, and never access `.active-clocks/.json`.

In each shell call that uses `${clock_session_id}`, bind the resolved value with proper shell quoting; assignments from earlier tool calls may not persist.

## Workflow

### Step 1: Read this session's clock

```bash
cat "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json"
```

- **If the file does not exist**: tell the user verbatim:
  > No clock file at `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json` for this session. It may already have been closed, or this host may not have created one. Run `/ci --session-id <resolved-id>` to start a new clock if you want to log this session.
  
  Then stop.
- **If it exists**: extract `repo`, `cluster`, `project`, `group`, `start`, `date`, `session_id`. Calculate elapsed minutes (current time minus start).
- **Attribution.** If the clock has no `attribution` field (it was armed before 26 Oct 2026), or wrap-up passed `--project <ref>`, resolve it again and use the result's `repo`, `cluster`, `project` and `group`:

  ```bash
  python3 /Users/esther/prog/missioncontrol/scripts/attribution.py resolve --cwd "<clock cwd>" [--project <ref>]
  ```

  The resolver routes code repos such as `/Users/esther/prog/music` to `musical-ideas`, worktrees to their main repo, and chat folders and the home folder to `unassigned`. If the command fails, keep the clock's values.

### Step 1.5: Resolve the repo if "unassigned"

If `repo == "unassigned"` (the session ran in the home folder, a chat folder or another folder outside `~/prog`), ask the user which repo the work belongs to before writing the row, then run `attribution.py resolve --repo <answer>` for its cluster, project and group.

Offer the onboarded repos from `projects.yaml`. Use the platform's blocking question tool (Claude Code: `AskUserQuestion`; Codex: `request_user_input`; Gemini: `ask_user`). Fallback: present numbered options and wait for the user's reply.

If no question tool is available or the user does not respond, write the row with `repo="unassigned"`, `group="unassigned"`, skip the history entry in Step 5, and tell the user to correct it in the evening reconcile.

### Step 2: Derive session type

Scan the current conversation for what happened. Classify based on the dominant activity:

| Activity signals | Session type |
|---|---|
| Wrote or edited source code files, built features, fixed bugs | execution |
| Reviewed code, ran tests, validated output, checked PRs | review |
| Created plans, broke down tasks, brainstormed, discussed approaches | planning |
| Designed architecture, data models, APIs, schemas, system design | design |
| Refactored code, updated dependencies, cleaned up, migrated | maintenance |

Present the classification for confirmation:
> Session type: **{type}** — sound right?

If the user overrides, use their choice.

### Step 3: Propose title and details

Based on what happened in the conversation:

- **Title**: A concise 1-line summary of the main accomplishment (like a commit message). Keep it under ~80 characters.
- **Details**: A compact semicolon-separated list of specifics — what was done, key decisions, outcomes.

Present both for the user to confirm or edit:
> **Title**: {proposed title}
> **Details**: {proposed details}

### Step 4: Write CSV row

Append a 13-column row to `/Users/esther/prog/missioncontrol/reports/timesheet.csv` (quote any field that holds a comma, and make sure the file ends with a newline before appending):

```
{date},{start_HH:MM},{end_HH:MM},{repo},{cluster},{session_type},{minutes},{title},{details},clock,{session_id},{project},{group}
```

Where:
- `date` is from the clock file
- `start_HH:MM` is extracted from the clock's `start` timestamp
- `end_HH:MM` is the current local time
- `minutes` is the calculated elapsed time
- `session_id` is the resolved `clock_session_id`
- `project` is the qualified project folder ref (for example `portfolio:T020`), empty when unknown; `group` is the group key (for example `idea-greenhouse`), empty when only the cluster is known

The file's header line still lists 11 columns; older rows stay as they are, and readers pad them and map them at read time.

**If the CSV does not exist**, create it with the 13-column header first:
```
date,start,end,repo,cluster,session_type,minutes,title,details,source,session_id,project,group
```

### Step 5: Write history.jsonl entry

Skip this step when `repo` is `unassigned` or `/Users/esther/prog/missioncontrol/tracking/{repo}/` does not exist: never create a new tracking directory from a clock-out.

Append a session entry to `/Users/esther/prog/missioncontrol/tracking/{repo}/history.jsonl`:

```json
{"type": "session", "date": "{date}", "timestamp": "{start_iso}", "session_type": "{session_type}", "topic": "{title}", "summary": "{details}", "duration_hours": {minutes/60 rounded to 2 decimals}}
```

### Step 6: Delete this session's clock file only

```bash
rm "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json"
```

Other sessions' clock files in the same directory must remain untouched.

### Step 7: Confirm

Report to the user:

> Clocked out: **{minutes}** min on **{repo}** ({session_type}) — "{title}"

---

## Edge Cases

- **Very short sessions (<5 min)**: Still log them. The user explicitly clocked in and out.
- **Very long sessions (>8 hours)**: Flag it — "This session is {X} hours. Does that look right, or did you forget to clock out earlier?" If the user provides a corrected end time, use that instead of now.
- **Clock spans midnight**: The date stays as the clock-in date. Minutes are calculated correctly across midnight.
- **Conversation has no useful context**: Ask the user directly for title and session_type rather than guessing.
- **Parallel conversations**: Each conversation's resolved `clock_session_id` keys its own clock file. `/co` here only finalizes this session's clock — sibling sessions are unaffected.

## Rules

- **Fail loud, never silent.** Missing or invalid session IDs must surface the guidance above; a missing clock file must name the resolved absolute path. Never respond with a generic "no active clock" — that was the silent-miss bug.
- **Always confirm** session_type, title, and details before writing, except in quick mode, where wrap-up has already confirmed the time and nothing else is asked.
- **Use current local time** for the end timestamp.
- **Write to both CSV and history.jsonl** — CSV is the primary database, JSONL maintains backward compatibility.
- **Delete this session's clock file only after successfully writing** the CSV row.
