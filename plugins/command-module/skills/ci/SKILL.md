---
name: ci
description: "Clock in to start tracking time. Use when the user says 'clock in', 'ci', 'start timer', 'start tracking', or wants to begin a timed work session. Also supports manual time entries for off-computer work."
argument-hint: "[repo] [start-end \"title\"]"
---

# Clock In

Start tracking time for a work session, or log a manual time entry for off-computer work.

## Context

- Active clock state: `missioncontrol/tracking/.active-clock.json`
- Timesheet CSV: `missioncontrol/reports/timesheet.csv`
- Repo-cluster mapping: `missioncontrol/projects.yaml`

## Detect Mode

Check `$ARGUMENTS`:

- **If arguments contain a time range** (pattern like `HH:MM-HH:MM` or `H:MM-H:MM`): → **Manual Entry mode**
- **Otherwise**: → **Normal Clock-In mode**

---

## Normal Clock-In

### Step 1: Identify repo

If `$ARGUMENTS` includes a repo name, use it. Otherwise, detect from the current working directory:

1. Read `missioncontrol/projects.yaml` to get `base_path` and all project entries
2. Determine the current working directory
3. Strip `base_path` prefix to get the repo directory name
4. Match against project entries (check `repo` field in all projects and clients)
5. If no match (e.g. running from missioncontrol itself): ask the user which repo to clock into

### Step 2: Resolve cluster

From the matched project entry in `projects.yaml`, resolve the cluster name (e.g. `revenuemanagement`, `portbase`, `meta`).

### Step 3: Check for existing clock

Read `missioncontrol/tracking/.active-clock.json`:

- **If it exists**: warn the user:
  > "Clock already running on {repo} since {start_time} ({X} minutes ago). Run /co first to close it, or use `/ci --force` to auto-close and start fresh."
  
  If `$ARGUMENTS` contains `--force`: auto-close the existing clock by writing a CSV row with end=now, session_type="auto-closed", title="Auto-closed (forgot to clock out)", source=clock. Then proceed to Step 4.
  
  Otherwise: stop here.

- **If it doesn't exist**: proceed to Step 4.

### Step 4: Write active clock

Get the current local time. Write `missioncontrol/tracking/.active-clock.json`:

```json
{
  "repo": "{repo_name}",
  "cluster": "{cluster_name}",
  "start": "{ISO 8601 local datetime}",
  "date": "{YYYY-MM-DD}"
}
```

### Step 5: Confirm

Report to the user:

> Clocked in: **{repo}** ({cluster}) at {HH:MM}

---

## Manual Entry

For logging off-computer work or work done outside Claude Code.

Example: `/ci portbase 09:00-12:00 "Steering committee meeting"`

### Step 1: Parse arguments

Extract from `$ARGUMENTS`:
- **repo** — the first word (required)
- **time range** — pattern `HH:MM-HH:MM` (required)
- **title** — quoted string after the time range (required)

If any part is missing, ask the user to provide it.

### Step 2: Resolve cluster

Look up the repo in `missioncontrol/projects.yaml` to get the cluster name.

### Step 3: Calculate duration

Parse start and end times, calculate minutes. If end < start, assume it crosses midnight (add 24h to end).

### Step 4: Determine session type

Suggest a session_type based on keywords in the title:
- "meeting", "presentation", "stakeholder", "review" → planning
- "design", "architecture", "model" → design
- "build", "implement", "code", "fix", "deploy" → execution
- "test", "review", "check", "audit" → review
- "refactor", "clean", "update", "migrate" → maintenance

Default to `planning` for manual entries (most off-computer work is meetings/discussions).

Present the suggestion and let the user confirm or override.

### Step 5: Write CSV row

Append a row to `missioncontrol/reports/timesheet.csv`:

```
{date},{start},{end},{repo},{cluster},{session_type},{minutes},{title},{details},manual
```

Use today's date (`$CURRENT_DATE`) unless the time range implies otherwise. Ask for optional details (semicolon-separated specifics). If the user doesn't provide details, leave the column empty.

### Step 6: Write history.jsonl entry

Append a session entry to `missioncontrol/tracking/{repo}/history.jsonl` for backward compatibility:

```json
{"type": "session", "date": "{date}", "timestamp": "{date}T{start}:00", "session_type": "{session_type}", "topic": "{title}", "summary": "{details}", "duration_hours": {minutes/60}}
```

### Step 7: Confirm

> Logged: **{minutes}** min on **{repo}** ({session_type}) — "{title}"

---

## Rules

- **No state file for manual entries.** They write directly to the CSV and history — no `.active-clock.json` involved.
- **Always read `projects.yaml` for repo/cluster resolution.** Don't hardcode mappings.
- **Use current local time** for clock-in timestamp (not UTC).
- **If the CSV file doesn't exist yet**, create it with the header row first:
  ```
  date,start,end,repo,cluster,session_type,minutes,title,details,source
  ```
