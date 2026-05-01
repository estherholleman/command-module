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

4. **For every completed, in_progress, or next task in scope, read its `tasks/T00N.md` and capture the `origin` field.** Origin is the trigger/context the task was created from; it is what makes accurate, non-misleading framing possible. If origin is missing or generic on a task that will appear in the report, **pause and ask the user** for the actual trigger before drafting — do not paper over it with a generic phrasing.

5. **Read the stakeholder context file** at `missioncontrol/reports/stakeholders/{stakeholder}-context.md` if it exists. This holds prior framings, what the stakeholder has been told, and which clients / pipelines they associate with what behaviour. Treat it as load-bearing: the report must not contradict it without explicit acknowledgement.

## Phase 2: Write Draft

Before drafting, load the `writing-foundations` skill as a writing knowledge base. Apply its build-mode principles (lead with the point, match register to audience, vary rhythm, be concrete) and its antipattern rules throughout the report. For Dutch reports, use the Dutch antipattern reference.

Generate a markdown draft following these rules:

### Language & Tone
- Write the **entire report** in the stakeholder's configured language (e.g., Dutch for Wolter).
- Match the configured tone (e.g., direct and concrete for Wolter).
- **No technical jargon.** No git terminology, no function names, no architecture references.
- Frame everything in terms of **business value and user impact**.
- Use natural, professional language — write like a colleague updating another colleague over coffee, not like notes to self.

### Sentence Craft
- **Write full conversational sentences, not fragments.** A bullet point should read as a complete thought, often two short sentences instead of one telegraphic one. The lead clause states what happened, then a follow-up sentence explains the consequence or context in plain language.
  - Avoid (notes-to-self): "Validatie afgerond. Geen problemen. ~55 functies gedocumenteerd."
  - Prefer (conversational): "De validatie is afgerond zonder problemen. Het document beschrijft inmiddels ongeveer 55 functies en dient als naslag voor toekomstige vragen."
- **Connect ideas with transitions.** When two facts belong together, link them with words like "waardoor", "zodat", "omdat", "dit betekent dat" — don't strand them as bare clauses separated by periods or semicolons.
- **No em dashes (`—`) in the output.** Use commas for parenthetical asides, periods for hard stops, colons before lists or explanations, and parentheses for genuine parentheticals. Em dashes are an AI-writing tell and the stakeholder has flagged them as cluttering.
- **Avoid bold-first bullets that swallow the sentence.** A bold lead phrase is fine when it is a true topic label followed by an explanatory sentence; it is not fine when the entire bullet is bolded summary with the explanation appended as a fragment.

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

### Framing Rule: never imply prior suboptimal behaviour for the reader

Capability changes ("now X is possible", "each direction can now have its own pool") read by default as if the system did not previously have X. For a stakeholder whose pipeline already had X, that framing is misleading — and worse, can contradict things they've previously been told.

For every item that describes a new capability, generalisation, or configurability:

1. Look at the task's `origin` field. It should tell you which client / pipeline / situation triggered the change.
2. Cross-reference the stakeholder context file: did the stakeholder's pipeline already have this behaviour? Were they previously told it did?
3. If the change was triggered by a *different* client or context than the reader's, **make that scope explicit** in the bullet. Name the client / pipeline the change was for, so the reader does not infer that their own setup was previously broken.
4. If origin is missing and you cannot determine scope, ask the user before drafting that bullet. Do not guess.

Example:
- Misleading: "Each direction on a route can now have its own reference pool." (Reads as: previously it couldn't, for everyone.)
- Accurate: "For MLtours specifically, each flight direction on a route can now use its own reference pool. For ES this was already the case via the Market column; the change makes the same behaviour available to clients where Market does not encode direction."

### Writing for the Reader's Domain (not ours)

Assume the reader knows their own domain (revenue management, port logistics, cycling sponsorship, whatever the stakeholder's profile says) but does **not** know how we work or what our internal vocabulary means. Detail is welcome — but only when it is explained in their language, not ours.

Two distinct kinds of jargon to watch for, and both must go:

1. **Technical jargon** (already covered in the rules above): git terms, function names, architecture words, code references.

2. **Process and tooling jargon from how we work** — equally invisible to the stakeholder, equally exclusionary. Examples to translate or rewrite, not just delete:
   - Workflow names: "implementation-plan", "brainstorm", "distill", "code-review", "/work", "ce:", "skill", "agent", "command-module" — never use these in the report. Rewrite as what the work actually was: "een plan geschreven voor X", "we hebben X uitgewerkt en de aanpak gekozen", "de aanpak is gevalideerd", etc.
   - Repository and tooling words: "PR", "merge", "branch", "main", "deploy" (use "in productie gezet" or "uitgebracht" instead), "commit", "push", "issue", "ticket", "backlog", "sprint", "Linear", "GitHub" — replace with what the activity meant for the work itself.
   - Internal artifact types: "brainstormdocument", "tech plan", "review pass", "iteratie n", "v0.6.1" without context — name *what was decided or shipped*, not the artifact format. A version number is fine when paired with what is in it.
   - Method-internal shorthand: "growth_blend", "fallback pool", "donor-route", "warping" — these *can* appear if explained the first time they show up in the report. Treat the first mention as if writing for someone smart who has not seen the term before: define it in one short clause, then use it.

**The test:** if a sentence uses a word or short phrase that only makes sense to someone who has worked inside this codebase or this team, it is shorthand and needs to be unpacked. Detail is good; assumed knowledge is not. Imagine the reader pausing on a word and asking "what does that mean here?" — every such word should already be answered in the surrounding sentence.

Example transformations:
- Avoid: "Plan klaar voor unified cross-route reference pool. Vier review-passes doorlopen."
- Prefer: "Het plan voor de volgende grote stap is klaar. In plaats van twee aparte voorspellingen mengen, gebruiken we straks één gezamenlijke referentiepool, wat de kwaliteit stabieler en inzichtelijker zou moeten maken. Het plan is in vier rondes kritisch tegen het licht gehouden en alle openstaande vragen zijn beantwoord, dus we kunnen beginnen met bouwen."
- Avoid: "Run-to-API script omzetten naar revintel."
- Prefer: "De volgende stap is om MLtours over te laten lopen via revintel, ons centrale forecastsysteem, in plaats van het losstaande script dat het nu nog gebruikt."

### Length
- Aim for brevity. A typical report should be 10-25 lines of content.
- The stakeholder should be able to read it in under 2 minutes.

## Phase 3: Style Pass

Once the draft markdown is written to a temp location (or the final path), run a style pass against it before generating downstream formats.

1. **Write the draft to its final markdown path** at `missioncontrol/reports/stakeholders/{stakeholder}-{YYYY-MM-DD}.md` so the proof skill can edit it in place.

2. **Invoke the `proof` skill on the draft.** Pass the file path as the argument. Proof will scan for AI-typical patterns, auto-fix tier 1 items (banned words, filler phrases), and generate a tier 2 findings document for items that need judgment (em dashes, structural rewrites). For Dutch reports, proof loads `references/writing-style-nl.md` automatically.

3. **Wait for the user's tier 2 choices**, then apply them. The skill should not proceed to format generation until the user has resolved the findings (or explicitly skipped them).

4. **Em dash spot-check.** After proof applies fixes, do a final grep for `—` in the markdown. If any remain, replace them with commas, periods, colons, or parentheses based on the surrounding clause — em dashes should never appear in the final output for stakeholders who have flagged them.

## Phase 4: Generate Outputs

Always generate three artifacts: markdown (already saved), HTML, and DOCX.

### HTML output

1. **Always generate an HTML version** to `missioncontrol/reports/stakeholders/{stakeholder}-{YYYY-MM-DD}.html`.

2. Convert the polished markdown to HTML using this template (matches the April 12 reference report — clean, readable, suitable for pasting into email or viewing in a browser):

   ```html
   <!DOCTYPE html>
   <html lang="{lang}">
   <head>
   <meta charset="utf-8">
   <style>
     body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 680px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.5; font-size: 15px; }
     ul { padding-left: 20px; margin: 0; }
     li { margin-bottom: 4px; }
     hr { border: none; border-top: 1px solid #ccc; margin: 20px 0 8px 0; }
   </style>
   </head>
   <body>
   {content}
   </body>
   </html>
   ```

3. Inside the body, render the markdown structure with `<h1>` for the report title, `<h2>` for each project, `<p><strong>...</strong></p>` for "Wat er is gedaan" / "Wat eraan komt" labels, `<ul><li>` for bullets, and `<hr>` between projects. Use `<em>` for the period line.

4. Set `lang` to match the stakeholder's configured language (`nl`, `en`, etc.).

### DOCX output

5. **Generate a .docx version** using python-docx. Use proper heading sizes (title 20pt, project names 16pt, section labels 11pt bold grey) and list bullets. Name the docx for SharePoint: `update{D}{month}{YYYY}.docx` (e.g. `update12april2026.docx`) — no stakeholder prefix, since these go into per-stakeholder folders on SharePoint.

## Phase 5: Log & Show

1. **Append to the report log** at `missioncontrol/reports/stakeholders/report-log.csv`:
   ```
   stakeholder,date,period_start,period_end,report_file
   wolter,2026-04-12,2026-04-01,2026-04-12,wolter-2026-04-12.md
   ```
   If the CSV doesn't exist yet, create it with the header row first.

2. **Show the report** to the user in the conversation, along with the paths to all three artifacts. They may want to adjust before sending.

## Guardrails

- **Never fabricate progress.** Only report what the tracking data shows. If the data is sparse, the report should be short.
- **Never include raw task IDs** (T001, T002) in the report — stakeholders don't care about internal tracking codes.
- **Don't editorialize beyond the data.** Observations like "great progress this week" are fine if earned. Don't add filler praise.
- **If no work was done** in the time range for a project, say so in one line. Don't generate an empty report structure.
- **Respect stakeholder boundaries.** Only report on projects listed in their profile, even if other projects had activity.
- **Never guess what route codes, airport codes, or destination names mean.** Use abbreviations exactly as they appear in the data. If a stakeholder's profile has `route_naming: abbreviations_only`, use codes without translating them to city or country names.
- **Respect `section_headers`** from the stakeholder profile. If configured, use those exact headers instead of the defaults.
- **Never assume the reader knows our jargon.** This is broader than the `skip` list: even if a stakeholder is comfortable with their own domain (e.g. revenue management for Wolter), they do not know our process or tooling vocabulary. Words like "implementation-plan", "brainstorm", "skill", "PR", "deploy", "branch", "ticket", "backlog", or any internal method shorthand ("growth_blend", "fallback pool") must be either translated into plain language or, if kept, defined in one short clause on first use. Detail is welcome; shorthand is not.
- **Never describe a capability change in a way that implies the reader's pipeline was previously broken.** See the "Framing Rule" in Phase 2. Use the task's `origin` field and the stakeholder context file to scope each change to the client / pipeline it was actually for. If origin is missing on a task that needs framing, ask the user before writing the bullet — do not paper over the gap with a generic phrasing.
