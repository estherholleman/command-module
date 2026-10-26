---
name: weekly-review
description: "End-of-week review across all projects. Scans the last 7 days of history.jsonl across every onboarded repo and writes a markdown report to missioncontrol/reports/weekly-YYYY-MM-DD.md. Use when the user says 'weekly review', 'how was my week', 'wrap up the week', or runs /weekly-review."
---

# /weekly-review — Weekly Review

End-of-week review across every onboarded repo. Lead with wins, surface trends, recommend focus for next week. Save the report.

## Step 1: Window

Today is `$CURRENT_DATE`. The review covers the **past 7 days, today inclusive**.

- `end_date` = today
- `start_date` = today − 6 days

Compute both with the system clock (`date -v-6d "+%Y-%m-%d"` on macOS). State the window to the user up front:

> "Reviewing **{start_date} ({weekday}) → {end_date} ({weekday})** — last 7 days."

## Step 2: Scan all repos

Read `missioncontrol/projects.yaml` for the onboarded repos. Groups (Idea greenhouse, Portbase, Revenue management, Coaching, Personal life, System) come from the Finder tree in `missioncontrol/tracking/portfolio/`; the shared resolver maps every repo, project and old timesheet row to its group, and falls back to the `projects.yaml` cluster where the tree has no answer yet:

```bash
cd /Users/esther/prog/missioncontrol
python3 scripts/attribution.py hours --from {start_date} --to {end_date}      # hours per group, tree project and repo
python3 scripts/attribution.py activity --from {start_date} --to {end_date}   # activity lines per group and repo
python3 scripts/attribution.py schedule                                       # each group's weekday rule
```

Use these outputs for hours, attention and schedule; do not rebuild the mapping by hand. A label ending in "(cluster)" is a repo the tree has not placed yet: report it under that label rather than guessing a group.

**Activity** means `session`, `status_change`, `task_created` and `milestone_completed` lines only. A `status_change` that only renames a status (`done` to `completed`, `in-progress` to `in_progress`, or the same status twice) is not activity and is not a completion; `activity` already leaves these out and reports how many it skipped.

For every onboarded project, read in parallel:
1. `missioncontrol/tracking/{repo}/history.jsonl` — filter entries where `date` is within the window
2. `missioncontrol/tracking/{repo}/tasks/index.json` — for current task state, deadlines, and stuck-in-progress checks
3. `missioncontrol/tracking/{repo}/tasks/milestones.json` — for milestone snapshots (skip if missing)
4. `missioncontrol/tracking/{repo}/status.json` — editorial context, current highlights

If a repo's tracking dir is missing, note "not onboarded" and skip. Do not fail.

For each task that completed inside the window, optionally open `tracking/{repo}/tasks/T0NN.md` if the index entry alone doesn't make the win clear.

## Step 3: Aggregate

### 3a. Tasks completed this week
For every `status_change` entry in the window with `to: "completed"` (skip renames such as `from: "done"`, which re-record an earlier completion):
- Look up the task in index.json — capture `task` description, `created`, `priority`, `tags`
- Compute **time-to-completion** = days from `created` to the entry's `date`. If `created` is missing or older than 90 days, just note "(long-running)".
- Group by repo. Keep the highest-priority items at the top within each repo.

Also count `task_created` and `milestone_completed` events in the window.

### 3b. Hours worked per day + weekly total
Read `missioncontrol/tracking/missioncontrol/history.jsonl`. For every `day_end` entry in the window, take its `hours_worked`. Index by `date`.

For days with `day_start` but no `day_end`, mark "in progress" (or skip if it's not today).

Build a per-day table for the 7 days. Show 0h for days with no entry.

**Weekly total** = sum of `hours_worked` across the window.

### 3c. Hours per group and project
Take the hours from `attribution.py hours --from {start_date} --to {end_date}` (the timesheet is the primary time database):
- `group_hours` with `group_labels`: hours per group, the main table;
- `tree_project_hours` with `project_titles`: hours per project folder, once projects exist in the tree (empty until the migration places them);
- `project_hours`: hours per repo, for the per-repo detail and older reviews.

Old rows are mapped at read time (stray repos such as `music` count toward `musical-ideas`), so nothing is rewritten. If the timesheet has no rows for a day, fall back to the `day_end` entries (`group_hours` when present, else `project_hours`) and then to `duration_hours` from `session` entries.

Also note the share of the week each group consumed (`hours / weekly_total`).

### 3d. Session type distribution
Across all repos, count `session` entries by `session_type`:
- `planning`, `design`, `execution`, `review`, `maintenance`

Compute totals overall **and** per-project (for the projects with ≥3 sessions this week — fewer than that is noise).

### 3e. Group attention
Per group, from 3c and `attribution.py activity`:
- Total hours (3c) and sessions (`group_sessions`)
- Activity lines (`group_activity`)
- % of weekly hours

Compare against each group's `schedule` from `attribution.py schedule`: the group folder's `schedule` field when set (`source: "group folder"`), else the `projects.yaml` `time_allocation` of the clusters that map to it (`source: "projects.yaml"`). `days` lists the weekdays it claims. Flag groups that are way under or over their nominal allocation, but only flag, don't lecture.

### 3f. Stalled projects (no sessions in 10+ days)
For every onboarded repo, find the timestamp of the most recent `session` entry in its full history.jsonl (not just the window).

If `today − last_session_date > 10 days`, flag as stalled with the day count.

### 3g. Growing backlogs
For each repo:
- `created_in_window` = count of `task_created` events in the window
- `completed_in_window` = count of `status_change` events to `completed` in the window
- `delta = created − completed`

Flag repos with `delta ≥ 3` as backlog-growing.

### 3h. Stuck `in_progress`
From each repo's index.json, find tasks where `status: in_progress` and `updated` is older than 14 days. Flag with task ID, project, days stuck.

### 3i. Milestone progress
From each repo's milestones.json, list:
- Milestones that completed this week (look for `milestone_completed` entries in history)
- Milestones at ≥75% progress (close to done — surface as motivation)
- Milestones whose `target_date` is within the next 14 days

## Step 4: Write the report

Save to `missioncontrol/reports/weekly-{end_date}.md` (overwrite if it exists — running /weekly-review twice on the same day is fine).

Use this structure. Keep it scannable in 60 seconds. Tables and bullets, minimal prose.

```markdown
# Weekly Review — {start_date} → {end_date}

**{N} working days · {weekly_total}h total**

---

## ✅ Wins of the Week

[Lead here. Group by project. Within each project, lead with the biggest win.]

**{Project}**
- T0NN: {task description} — {N}d to ship
- T0MM: {task description} — {N}d to ship
- ...

[If a milestone hit completed this week, give it a top-level callout above the project list:]

> 🎯 **Milestone completed:** `{milestone-slug}` ({project})

---

## ⏱️ Time Investment

### By Day
| Day | Date | Hours |
|-----|------|------:|
| Mon | 2026-04-19 | 8.5 |
| Tue | 2026-04-20 | 7.0 |
| ... | ... | ... |
| **Total** | | **{weekly_total}** |

### By Group
| Group | Hours | % of Week |
|-------|------:|----------:|
| {group label} | {h} | {pct}% |
| ... |
| **Total** | **{weekly_total}** | **100%** |

### By Repo
| Repo | Hours |
|------|------:|
| {repo} | {h} |

### By Session Type
| Type | Sessions | % |
|------|---------:|--:|
| execution | 12 | 50% |
| planning | 6 | 25% |
| design | 3 | 13% |
| review | 2 | 8% |
| maintenance | 1 | 4% |

[One-line read on the shape of the week. Examples (pick whichever fits, don't list all):
 - "Heavy planning week — execution should follow next."
 - "Delivery week — execution + review dominate."
 - "Maintenance-heavy — system care, not new features."]

---

## 📊 Group Attention

| Group | Hours | Sessions | Schedule | vs. schedule |
|-------|------:|---------:|----------|--------------|
| Idea greenhouse | 8.0 | 5 | Tue, Fri gaps, weekends | on track / under / over |
| Portbase | 6.0 | 4 | Mon, Wed | ... |
| ... |

[Flag mismatches honestly. If Tue/Fri were Revenue management days but only 2h logged, name it. One sentence, no lecture. Repos the tree has not placed yet appear under their "(cluster)" label.]

### By Project
[Only when `tree_project_hours` is non-empty: one row per project folder with its hours.]

---

## ⚠️ Watch List

### Stalled (no sessions in 10+ days)
- **{project}** — last session {N} days ago
- ...

### Growing backlogs
- **{project}** — created {N}, completed {M} (delta: +{N−M})

### Stuck `in_progress` (>14 days)
- {project} TXX: {task} — {N} days

[If everything is clean, write: "Nothing stalled, nothing stuck — clean week."]

---

## 🎯 Milestone Progress

[Only show movement. If nothing moved, write: "No milestone movement this week."]

- **{milestone-slug}** ({project}): {start_pct}% → {end_pct}% [✅ completed]
- **{milestone-slug}** ({project}): at {pct}% — {one-line reason it matters}

---

## 🔮 Next Week

[Opinionated. Use the group schedules from `attribution.py schedule` (today: Mon/Wed = Portbase, Tue/Fri = Revenue management with Idea greenhouse and Coaching in the gaps, Thu = flexible, weekends = Idea greenhouse and Personal life) as a frame, then layer in what the data is telling you.]

**Top priorities:**
1. **{project}** — {task or direction}
   _Why: {one-line reason}_
2. ...
3. ...

**Should not slip:**
- {External dependency, deadline, or blocker that needs attention}

**Carry-forwards:**
- {tasks that have been `next` for too long or `in_progress` and need a push}
```

## Step 5: Present + log

After writing the file:

1. **Show a summary inline** — Wins section + Watch List highlights + the file path. Not the full report; the user can open the file.
2. **Append a session entry** to `missioncontrol/tracking/missioncontrol/history.jsonl`:

   ```json
   {"type": "session", "date": "{end_date}", "timestamp": "{end_date}T{HH:MM}:00", "session_type": "review", "topic": "Weekly review", "summary": "Generated weekly review for {start_date} → {end_date}: {weekly_total}h, {N} task completions, {M} stalled projects.", "duration_hours": 0.25}
   ```

3. If this is the first time `/weekly-review` produces a meaningful review and the user confirms, prompt to flip the `first-weekly-review` milestone in `missioncontrol/tracking/missioncontrol/tasks/milestones.json` to `completed` (100%) and append a `milestone_completed` entry to history. Do **not** auto-flip — ask first.

## Notes

- **Lead with wins.** Even a hard week probably had progress. Surface it.
- **Be opinionated about focus.** Don't list every backlog item — pick what matters most for next week.
- **Mismatched allocation is information.** If a group's schedule says Tue/Fri but the hours don't show it, name it without lecturing.
- **Stalled is a signal, not a verdict.** A project might be deliberately paused. Flag it without judgment.
- **Be honest about light weeks.** If little shipped, say so plainly. No filler, no padding.
- **Save the file.** This is a permanent record, not just a chat message. Path: `missioncontrol/reports/weekly-{end_date}.md`.
- **Don't replace `/evening`.** This is the weekly companion — daily wrap stays in `/evening`. Don't double-log day_end events.
- **Run on Friday or Sunday.** Friday for a week-of-work read; Sunday to set up Monday. Either works.
