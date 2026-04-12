---
name: report
description: "Generate a stakeholder-facing progress report from missioncontrol tracking data. Writes in the stakeholder's language, scoped to what changed since their last report."
argument-hint: "[stakeholder name] [optional: time range like 'today', 'this week', 'since april 1']"
---

# /report — Stakeholder Progress Report

Generate a concise, non-technical progress report for a specific stakeholder, based on missioncontrol tracking data. The report is written in the stakeholder's language and focused on what they care about.

## Invocation

```
/report wolter              → report for Wolter, auto-scoped since his last report
/report wolter today        → report for Wolter, scoped to today only
/report wolter this week    → report for Wolter, scoped to this calendar week
/report wolter since apr 1  → report for Wolter, from April 1 to now
/report                     → prompt for stakeholder name
```

## Phase 0: Parse & Load

1. **Parse the argument.** Extract:
   - Stakeholder name (required — if missing, ask with AskUserQuestion: "Who is this report for?")
   - Time range (optional — if missing, will auto-scope from report log)

2. **Load stakeholder profile** from `missioncontrol/stakeholders.yaml`. Match the name case-insensitively. If no match, list available stakeholders and ask.

3. **Determine time range.**
   - Read `missioncontrol/reports/stakeholders/report-log.csv` to find the most recent report date for this stakeholder.
   - If the user specified a time range, use that.
   - If not, and a previous report exists, scope from the day after the last report date to today.
   - If not, and no previous report exists, default to the last 14 days and note this in the report intro.

## Phase 1: Gather Data

For each project the stakeholder cares about (from their profile in `stakeholders.yaml`):

1. **Read `missioncontrol/tracking/{project}/history.jsonl`** — filter entries within the time range. Collect:
   - Sessions (with summaries and types)
   - Task completions (status_change to `completed`)
   - New tasks created
   - Milestone completions

2. **Read `missioncontrol/tracking/{project}/tasks/index.json`** — for current state context:
   - Tasks currently `in_progress` or `next`
   - Tasks with approaching deadlines

3. **Read `missioncontrol/tracking/{project}/status.json`** — for editorial context and highlights.

4. For completed tasks that need more context, read individual task files (`tasks/T00N.md`) to get the notes body.

## Phase 2: Write Report

Generate a markdown report following these rules:

### Language & Tone
- Write the **entire report** in the stakeholder's configured language (e.g., Dutch for Wolter).
- Match the configured tone (e.g., direct and concrete for Wolter).
- **No technical jargon.** No git terminology, no function names, no architecture references.
- Frame everything in terms of **business value and user impact**.
- Use natural, professional language — not AI-formal. Write like a colleague updating another colleague.

### Structure

The report should follow this structure (section headers in the stakeholder's language):

```markdown
# [Project Name] — Voortgangsrapport [Date]

*Periode: [start date] – [end date]*

## Wat is er gedaan
- Concrete accomplishments, framed as business outcomes
- Group related work into coherent bullet points
- Lead with the most impactful items

## Wat komt eraan
- Tasks that are in_progress or next
- Upcoming milestones and deadlines
- Expected focus for the next period

## Aandachtspunten
- Only if relevant: blockers, risks, decisions needed from the stakeholder
- Skip this section entirely if there's nothing to flag
```

The section headers above are Dutch examples — adapt to the stakeholder's language. Keep the structure but adjust the headers.

### Content Rules
- **Lead with impact, not activity.** "Gebruikers kunnen nu X" not "We hebben Y geïmplementeerd".
- **Be concrete.** Numbers, names, specific features — not vague summaries.
- **Be honest.** If little was done in the period, say so briefly. Don't pad.
- **Skip empty sections.** If there are no blockers, don't include an empty "Aandachtspunten" section.
- **Consolidate related work.** Five commits on the same feature = one bullet point about the feature, not five bullet points about commits.
- **Respect the `skip` list** from the stakeholder profile. If it says skip technical details, do not mention implementation specifics even if they were the bulk of the work — translate to what it means for the user/business.

### Length
- Aim for brevity. A typical report should be 10-25 lines of content.
- The stakeholder should be able to read it in under 2 minutes.

## Phase 3: Save & Log

1. **Write the markdown report** to `missioncontrol/reports/stakeholders/{stakeholder}-{YYYY-MM-DD}.md`

2. **Generate a .docx version** using python-docx. Use proper heading sizes (title 20pt, project names 16pt, section labels 11pt bold grey) and list bullets. Name the docx for SharePoint: `update{D}{month}{YYYY}.docx` (e.g. `update12april2026.docx`) — no stakeholder prefix, since these go into per-stakeholder folders on SharePoint.

3. **Append to the report log** at `missioncontrol/reports/stakeholders/report-log.csv`:
   ```
   stakeholder,date,period_start,period_end,report_file
   wolter,2026-04-12,2026-04-01,2026-04-12,wolter-2026-04-12.md
   ```
   If the CSV doesn't exist yet, create it with the header row first.

4. **Show the report** to the user in the conversation. They may want to adjust before sending.

## Guardrails

- **Never fabricate progress.** Only report what the tracking data shows. If the data is sparse, the report should be short.
- **Never include raw task IDs** (T001, T002) in the report — stakeholders don't care about internal tracking codes.
- **Don't editorialize beyond the data.** Observations like "great progress this week" are fine if earned. Don't add filler praise.
- **If no work was done** in the time range for a project, say so in one line. Don't generate an empty report structure.
- **Respect stakeholder boundaries.** Only report on projects listed in their profile, even if other projects had activity.
- **Never guess what route codes, airport codes, or destination names mean.** Use abbreviations exactly as they appear in the data. If a stakeholder's profile has `route_naming: abbreviations_only`, use codes without translating them to city or country names.
- **Respect `section_headers`** from the stakeholder profile. If configured, use those exact headers instead of the defaults.
