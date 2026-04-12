---
name: co
description: "Clock out to stop tracking time. Use when the user says 'clock out', 'co', 'stop timer', 'stop tracking', or wants to end a timed work session. Derives session type and title from conversation context."
---

# Clock Out

Stop the active time clock, derive session metadata from conversation context, and write the time entry.

## Context

- Active clock state: `missioncontrol/tracking/.active-clock.json`
- Timesheet CSV: `missioncontrol/reports/timesheet.csv`

## Workflow

### Step 1: Read active clock

Read `missioncontrol/tracking/.active-clock.json`.

- **If it doesn't exist**: tell the user "No active clock. Nothing to clock out." and stop.
- **If it exists**: extract repo, cluster, start timestamp, date. Calculate elapsed minutes (current time minus start).

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

Append a row to `missioncontrol/reports/timesheet.csv`:

```
{date},{start_HH:MM},{end_HH:MM},{repo},{cluster},{session_type},{minutes},{title},{details},clock
```

Where:
- `date` is from the active clock
- `start_HH:MM` is extracted from the start timestamp
- `end_HH:MM` is the current time
- `minutes` is the calculated elapsed time

**If the CSV file doesn't exist**, create it with the header row first.

### Step 5: Write history.jsonl entry

Append a session entry to `missioncontrol/tracking/{repo}/history.jsonl` for backward compatibility:

```json
{"type": "session", "date": "{date}", "timestamp": "{start_iso}", "session_type": "{session_type}", "topic": "{title}", "summary": "{details}", "duration_hours": {minutes/60 rounded to 2 decimals}}
```

### Step 6: Delete active clock

Delete `missioncontrol/tracking/.active-clock.json`.

### Step 7: Confirm

Report to the user:

> Clocked out: **{minutes}** min on **{repo}** ({session_type}) — "{title}"

---

## Edge Cases

- **Very short sessions (<5 min)**: Still log them. The user explicitly clocked in and out.
- **Very long sessions (>8 hours)**: Flag it — "This session is {X} hours. Does that look right, or did you forget to clock out earlier?" If the user provides a corrected end time, use that instead of now.
- **Clock spans midnight**: The date stays as the clock-in date. Minutes are calculated correctly across midnight.
- **Conversation has no useful context** (e.g. user just chatted briefly): Ask the user directly for title and session_type rather than guessing.

## Rules

- **Always confirm** session_type, title, and details before writing. These are the user's time records.
- **Use current local time** for the end timestamp.
- **Write to both CSV and history.jsonl** — CSV is the primary database, JSONL maintains backward compatibility.
- **Delete the state file only after successfully writing** the CSV row.
