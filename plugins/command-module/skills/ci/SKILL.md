---
name: ci
description: "Clock in to start tracking time. Use when the user says 'clock in', 'ci', 'start timer', 'start tracking', or wants to begin a timed work session. Also supports manual time entries for off-computer work."
argument-hint: "[repo] [start-end \"title\"]"
---

# Clock In

Start tracking time for a work session, or log a manual time entry for off-computer work.

## Context

- Per-session clock state: `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json`
- Timesheet CSV: `/Users/esther/prog/missioncontrol/reports/timesheet.csv`
- Repo-cluster mapping: `/Users/esther/prog/missioncontrol/projects.yaml`

## Detect Mode

Check `$ARGUMENTS`:

- **If arguments contain a time range** (pattern like `HH:MM-HH:MM` or `H:MM-H:MM`): → **Manual Entry mode**
- **Otherwise**: → **Normal Clock-In mode**

Manual Entry mode never reads or writes the per-session clock file — it logs straight to CSV. It does not require a session ID.

---

## Normal Clock-In

In Claude Code with the SessionStart clock hook installed, the hook creates a per-session clock at the beginning of a conversation, so bare `/ci` usually reports the existing clock. In Codex/ChatGPT or another host without that hook, `/ci` creates a clock when a valid session ID is available and no clock exists.

### Preamble: resolve session ID

Resolve `clock_session_id` once: use an explicit `--session-id <id>` or the ID the user supplies for this conversation, then a nonempty `$CODEX_THREAD_ID`, then a nonempty `$CLAUDE_SESSION_ID`. Remove `--session-id` and its value before interpreting remaining arguments. When called from wrap-up, use the ID it passes without reselecting it.

Before any clock operation, require a nonempty ID matching `^[A-Za-z0-9][A-Za-z0-9._-]*$`. If no valid ID is available, stop clock handling and report: "Cannot identify this conversation's clock. Supply --session-id <id> or a valid CODEX_THREAD_ID / CLAUDE_SESSION_ID. Wrap-up can still run without a clock check."

Use the same ID for the clock filename and CSV `session_id`. Never infer it from the repo name, recent transcripts, or other clock files, and never access `.active-clocks/.json`.

In each shell call that uses `${clock_session_id}`, bind the resolved value with proper shell quoting; assignments from earlier tool calls may not persist.

### Step 1: Check this session's clock

```bash
cat "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json"
```

- **If it exists** and `--force` is NOT in `$ARGUMENTS`: print informationally and stop.
  > Clock running for this session since {start_HH:MM} ({repo}, {cluster}). Use `/ci --force` to reset, or `/ci <repo> HH:MM-HH:MM "title"` for manual entry.
- **If it exists** and `--force` IS in `$ARGUMENTS`: close the existing clock by writing a CSV row (use end=now, session_type="auto-closed", title="Auto-closed by /ci --force", source="clock", session_id=$clock_session_id), delete the file, then continue to Step 2.
- **If it does not exist** (for example, the host has no SessionStart clock hook or the clock was manually cleared): continue to Step 2.

### Step 2: Identify repo

If `$ARGUMENTS` includes a repo name (and is not just `--force`), use it. Otherwise detect from the current working directory:

1. Read `/Users/esther/prog/missioncontrol/projects.yaml` to get `base_path` and all project entries
2. Determine the current working directory
3. Strip `base_path` prefix to get the repo directory name
4. Match against project entries (check `repo` field in all projects and clients)
5. If no match: use `repo = basename(cwd)`, `cluster = "unassigned"` — the same fallback as the SessionStart hook. `/co` will prompt to pick the real cluster at close time.

### Step 3: Resolve cluster

From the matched entry in `projects.yaml`, resolve the cluster name. If unmatched, use `"unassigned"`.

### Step 4: Write per-session clock

Get the current local time. Write `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${clock_session_id}.json`:

```json
{
  "session_id": "${clock_session_id}",
  "repo": "{repo_name}",
  "cluster": "{cluster_name}",
  "start": "{ISO 8601 local datetime}",
  "date": "{YYYY-MM-DD}",
  "cwd": "{current working directory}",
  "source_at_start": "manual-ci"
}
```

Create the parent directory `.active-clocks/` if it does not exist.

### Step 5: Confirm

Report to the user:

> Clocked in: **{repo}** ({cluster}) at {HH:MM} (session `${clock_session_id:0:8}`)

---

## Manual Entry

For logging off-computer work or work done without a session clock.

Example: `/ci portbase 09:00-12:00 "Steering committee meeting"`

### Step 1: Parse arguments

Extract from `$ARGUMENTS`:
- **repo** — the first word (required)
- **time range** — pattern `HH:MM-HH:MM` (required)
- **title** — quoted string after the time range (required)

If any part is missing, ask the user to provide it.

### Step 2: Resolve cluster

Look up the repo in `/Users/esther/prog/missioncontrol/projects.yaml` to get the cluster name.

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

Append an 11-column row to `/Users/esther/prog/missioncontrol/reports/timesheet.csv`:

```
{date},{start},{end},{repo},{cluster},{session_type},{minutes},{title},{details},manual,
```

The trailing comma is the empty `session_id` field — manual entries are not tied to a conversation. Use today's date unless the time range implies otherwise. Ask for optional details (semicolon-separated specifics); leave the column empty if none provided.

### Step 6: Write history.jsonl entry

Append a session entry to `/Users/esther/prog/missioncontrol/tracking/{repo}/history.jsonl`:

```json
{"type": "session", "date": "{date}", "timestamp": "{date}T{start}:00", "session_type": "{session_type}", "topic": "{title}", "summary": "{details}", "duration_hours": {minutes/60}}
```

### Step 7: Confirm

> Logged: **{minutes}** min on **{repo}** ({session_type}) — "{title}"

---

## Rules

- **No state file for manual entries.** They write directly to the CSV and history — no per-session clock file involved.
- **Always read `projects.yaml` for repo/cluster resolution.** Don't hardcode mappings.
- **Use current local time** for clock-in timestamp (not UTC).
- **Check before creating.** Bare `/ci` reports an existing clock; it creates one only when this session has no clock file.
- **CSV header has 11 columns** (10th = `source`, 11th = `session_id`). Manual entries leave `session_id` empty.
- **Require an ID for Normal mode.** Missing or invalid IDs stop clock handling with the specific guidance above. Manual entries remain available without an ID.
