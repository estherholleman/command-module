---
name: co
description: "Clock out to stop tracking time. Use when the user says 'clock out', 'co', 'stop timer', 'stop tracking', or wants to end a timed work session. Derives session type and title from conversation context."
---

# Clock Out

Stop this conversation's time clock, derive session metadata from conversation context, and write the time entry.

## Context

- Per-session clock state: `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json`
- Timesheet CSV: `/Users/esther/prog/missioncontrol/reports/timesheet.csv`
- Repo-cluster mapping: `/Users/esther/prog/missioncontrol/projects.yaml`

## Preamble: assert session id

Before any clock operation, run a single Bash check to fail loud if `$CLAUDE_SESSION_ID` is missing:

```bash
test -n "$CLAUDE_SESSION_ID" && echo "ok: $CLAUDE_SESSION_ID" || { echo "ERROR: CLAUDE_SESSION_ID is empty. SessionStart hook did not set it (CLAUDE_ENV_FILE mechanism). Cannot identify this conversation's clock. Aborting."; exit 1; }
```

If this prints the ERROR line, stop. Do not proceed. Surface the message verbatim to the user — this is the silent-miss bug the per-session design is meant to prevent.

## Workflow

### Step 1: Read this session's clock

```bash
cat "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json"
```

- **If the file does not exist**: tell the user verbatim:
  > No clock file at `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` for this session. Either it was already closed by `/co`, finalized by SessionEnd, or the SessionStart hook never wrote one. Run `/ci` to start a new clock if you want to log this session.
  
  Then stop.
- **If it exists**: extract `repo`, `cluster`, `start`, `date`, `session_id`. Calculate elapsed minutes (current time minus start).

### Step 1.5: Resolve cluster if "unassigned"

If `cluster == "unassigned"` (the SessionStart hook ran in a cwd not mapped in `projects.yaml`), prompt the user to pick a cluster before writing the row.

Read `projects.yaml` to enumerate available clusters. Use the platform's blocking question tool (Claude Code: `AskUserQuestion`; Codex: `request_user_input`; Gemini: `ask_user`). Fallback: present numbered options and wait for the user's reply.

Update `cluster` to the user's choice. If no question tool is available and the user does not respond, write the row with `cluster="unassigned"` and warn the user to correct manually later.

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

Append an 11-column row to `/Users/esther/prog/missioncontrol/reports/timesheet.csv`:

```
{date},{start_HH:MM},{end_HH:MM},{repo},{cluster},{session_type},{minutes},{title},{details},clock,{session_id}
```

Where:
- `date` is from the clock file
- `start_HH:MM` is extracted from the clock's `start` timestamp
- `end_HH:MM` is the current local time
- `minutes` is the calculated elapsed time
- `session_id` is `$CLAUDE_SESSION_ID`

**If the CSV does not exist**, create it with the 11-column header first:
```
date,start,end,repo,cluster,session_type,minutes,title,details,source,session_id
```

### Step 5: Write history.jsonl entry

Append a session entry to `/Users/esther/prog/missioncontrol/tracking/{repo}/history.jsonl`:

```json
{"type": "session", "date": "{date}", "timestamp": "{start_iso}", "session_type": "{session_type}", "topic": "{title}", "summary": "{details}", "duration_hours": {minutes/60 rounded to 2 decimals}}
```

### Step 6: Delete this session's clock file only

```bash
rm "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json"
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
- **Parallel conversations**: Each conversation's `$CLAUDE_SESSION_ID` keys its own clock file. `/co` here only finalizes this session's clock — sibling sessions are unaffected.

## Rules

- **Fail loud, never silent.** Empty `$CLAUDE_SESSION_ID` or missing clock file must surface a specific error naming the absolute path and the variable. Never respond with a generic "no active clock" — that was the silent-miss bug.
- **Always confirm** session_type, title, and details before writing.
- **Use current local time** for the end timestamp.
- **Write to both CSV and history.jsonl** — CSV is the primary database, JSONL maintains backward compatibility.
- **Delete this session's clock file only after successfully writing** the CSV row.
