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
- **Be concrete, but only with anchored detail.** Names, specific features, and qualitative outcomes are always welcome. Numbers are not automatically concrete: a count like "179.262 forecastregels", "1849 referentie-pools", "65.127 voorspellingsregels", or "594 vluchten" gives the reader nothing if they have no benchmark to compare it to. Only include a number when at least one of these is true: (a) it is anchored to a comparison the reader can read off the sentence ("kleiner dan de 2.300 van vorige maand", "alle 23 routes", "3 van de 6 opties"), or (b) the magnitude itself carries the message (e.g. "miljoenen regels" to convey scale, "twee fouten" to convey rarity). Otherwise replace the number with qualitative language: "identiek", "kleiner en zuiverder", "de meeste routes", "een handjevol uitzonderingen". A qualitative claim a stakeholder can act on beats a precise number they cannot interpret.
- **Be precise about deployment status.** Do not blur the difference between "code is written and tested locally", "running in acc / test environment", "running in prd", and "running in prd on its own automated trigger". Reserve "live", "in productie", "draait", "uitgebracht" for the last of those — automated and observable in production. If something is only in acc, name acc explicitly (Wolter and similar stakeholders know acc / prd as concepts). If a human still has to trigger it manually, say so. If a scheduler / automated trigger still needs to be built before the change is truly running on its own, say that as part of the same bullet so the reader does not infer "done" from "deployed". Drop CI/CD and pipeline tooling words; describe what is and is not yet automatic in plain language.
- **Each bullet stands alone — re-anchor cross-references.** Stakeholders scan reports; they do not read top-to-bottom. Phrases like "de fix", "deze aanpak", "hetzelfde probleem", "de overstap", "de eerder genoemde X" only land for someone reading sequentially. Every time such a reference appears, restate in one short clause what it refers to ("de fix voor de te hoge schattingen op MLTours", "de overstap naar revintel"). If you find yourself writing a bullet that depends on the previous bullet to be intelligible, rewrite the bullet to carry its own context.
- **Frame the problem in the reader's words before any internal terminology.** When a bullet describes a fix, an investigation, or a decision triggered by a problem, the *symptom* must land first in everyday language the stakeholder would use to describe it themselves ("het model schatte in sommige gevallen te hoog", "voorspellingen ontbraken voor bepaalde vluchten"). Internal debugging vocabulary — "oversprongen", "auto-end-gedrag", "rate dominant in de blend", method names like `growth_blend` / `growth_bayesian` — should not be the entry point. Prefer dropping internal method names entirely and describing what they do; only introduce a name when the stakeholder will see it referenced repeatedly across reports and needs a handle for it. The team's debug vocabulary, if used at all, comes after the symptom is anchored, not before.
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

**Refer to the substance, not the artifact.** When the work in the period included producing an internal artifact (plan, brainstorm, review, design doc, requirements doc, audit), the bullet must convey *what is in it* — the cause that was identified, the options on the table, the decision made, the findings — not the fact that the artifact exists. Phrasings like "we hebben een brainstorm gedaan" / "het plan is uitgewerkt" / "een review is afgerond" are still process jargon even when the technical term is removed, because they describe activity instead of outcome. The reader does not know what a brainstorm or plan or review *is* in our process and does not care; they care about what we now know or have decided that we did not before.

The test for this rule: after writing a bullet that references work-on-an-artifact, ask "if I struck the artifact word out entirely, would the bullet still tell the reader something concrete about the *content* of the work?" If not, rewrite the bullet around the content. Producing the artifact is our internal milestone; the substance inside it is the only thing that crosses to the stakeholder.

Example transformations:
- Avoid: "Plan klaar voor unified cross-route reference pool. Vier review-passes doorlopen."
- Prefer: "Het plan voor de volgende grote stap is klaar. In plaats van twee aparte voorspellingen mengen, gebruiken we straks één gezamenlijke referentiepool, wat de kwaliteit stabieler en inzichtelijker zou moeten maken. Het plan is in vier rondes kritisch tegen het licht gehouden en alle openstaande vragen zijn beantwoord, dus we kunnen beginnen met bouwen."
- Avoid (uses jargon term): "De brainstorm voor de growth_blend fix is uitgewerkt."
- Avoid (jargon removed but still about the artifact, not the substance): "Het plan voor de growth_blend fix is uitgewerkt."
- Prefer: "De oorzaak van de oversprongen op MLTours is gevonden: een onbegrensde rate die te lang dominant blijft in de blend. We hebben zes oplossingsrichtingen op een rij gezet met afwegingen per richting; welke we kiezen hangt af van een paar data-experimenten die we eerst draaien."
  - The first two skip the substance entirely. Only the third tells the reader what we now know, what options exist, and how the choice will be made.
- Avoid: "Run-to-API script omzetten naar revintel."
- Prefer: "De volgende stap is om MLtours over te laten lopen via revintel, ons centrale forecastsysteem, in plaats van het losstaande script dat het nu nog gebruikt."

### Length
- Aim for brevity. A typical report should be 10-25 lines of content.
- The stakeholder should be able to read it in under 2 minutes.

## Phase 3: Style Pass

Once the draft markdown is written to a temp location (or the final path), run two passes against it before generating downstream formats: a cold-read persona pass for substance, then `proof` for language.

1. **Write the draft to its final markdown path** at `missioncontrol/reports/stakeholders/{stakeholder}-{YYYY-MM-DD}.md` so subsequent passes can edit it in place.

2. **Cold-read persona pass.** Re-read the draft from the seat of the actual stakeholder — someone who has *not* been in the build, who scans rather than reads, and who only knows their own domain. Use the stakeholder's profile and context file to ground the persona (their role, their domain vocabulary, what they have and have not been told before). Walk through the draft bullet by bullet and flag every instance of the four failure modes below; do not silently rewrite — surface the findings to the user with the offending phrasing and a proposed replacement, then apply the user's choices.

   Failure modes to flag:
   - **Unanchored numbers.** Any count, percentage, or magnitude that the reader has no benchmark to interpret. Propose either a qualitative replacement or, if the number is genuinely load-bearing, an anchor that gives it meaning ("vs. before", "of the total", "of N tried").
   - **Imprecise deployment status.** Any use of "live", "in productie", "draait", "uitgebracht", "deployed", or equivalent that is not actually true of the change being described — e.g. only in acc, only manually triggered, or still waiting on someone else to wire up automation. Propose phrasing that names the actual state and what is still needed before it is truly running on its own.
   - **Cross-section anaphora.** Any "de fix", "deze aanpak", "hetzelfde probleem", "de overstap", "de eerder genoemde X" that requires the reader to remember an earlier bullet to be intelligible when scanning. Propose a re-anchored phrasing that restates what is being referred to in one short clause.
   - **Symptom not in reader's words.** Any fix or investigation bullet whose entry point is internal debug vocabulary — "oversprongen", "auto-end", method names like `growth_blend` / `growth_bayesian`, internal feature names — instead of the symptom as the stakeholder would describe it. Propose a rewrite that leads with the symptom in plain language and either drops the internal name or defers it to after the symptom is anchored.

   After the user resolves these findings, apply them in the markdown before moving on to proof.

3. **Invoke the `proof` skill on the draft.** Pass the file path as the argument. Proof will scan for AI-typical patterns, auto-fix tier 1 items (banned words, filler phrases), and generate a tier 2 findings document for items that need judgment (em dashes, structural rewrites). For Dutch reports, proof loads `references/writing-style-nl.md` automatically.

4. **Wait for the user's tier 2 choices**, then apply them. The skill should not proceed to format generation until the user has resolved the findings (or explicitly skipped them).

5. **Em dash spot-check.** After proof applies fixes, do a final grep for `—` in the markdown. If any remain, replace them with commas, periods, colons, or parentheses based on the surrounding clause — em dashes should never appear in the final output for stakeholders who have flagged them.

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
- **Never include a number the reader cannot benchmark.** Counts of internal artifacts (forecast rows, pool counts, flight counts) without a comparison are noise, not concreteness. Anchor the number or replace it with qualitative language. See "Be concrete, but only with anchored detail" in Phase 2.
- **Never overstate deployment status.** "Live", "in productie", "draait", "uitgebracht" mean running in prd on an automated trigger. Anything earlier (acc only, manual trigger, awaiting scheduler) must be named as such in the same bullet. See "Be precise about deployment status" in Phase 2.
- **Never leave a back-reference unanchored across sections.** "De fix", "deze aanpak", "hetzelfde probleem" must each restate what they refer to in one short clause every time they appear. Stakeholders scan; bullets must stand alone.
- **Never lead a fix bullet with internal debug vocabulary.** The symptom comes first in the reader's own words; method names and team shorthand come after, or not at all.
