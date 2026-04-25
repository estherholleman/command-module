---
title: "feat: /explain-pipeline skill — algorithmic flow explainer for data-science codebases"
type: feat
status: active
date: 2026-04-25
origin: missioncontrol/tracking/command-module/tasks/T016.md
---

# /explain-pipeline skill — algorithmic flow explainer for data-science codebases

## Overview

Add an `/explain-pipeline` skill to the `command-module` plugin that produces grounded, file:line-cited Markdown drafts explaining how a data pipeline behaves: entry points, decision branches, per-method walkthroughs, fallback cascades, quality gates, and a glossary. The skill forks the mechanics of `/onboarding` (repo crawl, observation discipline, structured Markdown output) but swaps the section template from "orientation" to "algorithmic walkthrough."

Primary callers: revintel (multiple forecast methods, blend logic, fallback cascades, quality gates) and portbase (analytical pipelines). External callers may include partner-facing explainer drafts (e.g., the recent ad-hoc Norbert doc at europeansleeper that motivated the task).

## Problem Frame

Writing readable explanations of *how a data pipeline actually behaves* is a recurring need across revintel and portbase:

- Each new forecasting feature needs a "what does it do" doc for internal review and external partners.
- The pipelines mix declarative config, branching method-selection logic, layered fallbacks, and quality gates that are hard to reconstruct from code alone.
- The recent ad-hoc research-agent run that produced the Norbert doc proved the shape works but is not repeatable — turning it into a skill makes it cheap to redo.

`/onboarding` is close in mechanics but wrong in shape: its sections answer "what is this codebase" not "how does this algorithm decide what to do." The discipline (file:line grounding, "state what you observe, don't infer") is exactly what should be preserved.

This skill is **not**: stakeholder-polished prose (`/proof` does that), problem-solution capture (`/distill`), nor a once-per-repo orientation doc (`/onboarding`). The output is a grounded *draft* — a faithful rendering of the algorithm with citations, ready for a human to wrap stakeholder framing around.

## Requirements Trace

- **R1.** Produce a grounded Markdown explainer of a pipeline's algorithmic behavior, with every claim tied to `path:line` references.
- **R2.** Cover six sections: entry points, decision tree, per-method walkthroughs, fallback cascade, quality gates, glossary (origin: T016 "Shape" sketch).
- **R3.** Domain-agnostic — must work on revintel (Python forecasting), portbase (analytical pipelines), and other data-science Python codebases without hardcoded domain vocabulary.
- **R4.** Preserve the `/onboarding` "state what you observe, don't infer" discipline: no fabricated rationale, no fragility/risk speculation, no inferred "why" without code evidence.
- **R5.** Output is a draft, not a stakeholder-ready doc — explicitly out of scope to polish prose, infer business framing, or capture solved problems.
- **R6.** Skill compliance: passes `bun test tests/frontmatter.test.ts`, passes `bun run release:validate`, and follows the plugin's skill-authoring rules (`AGENTS.md` § Skill Compliance Checklist).

## Scope Boundaries

**In scope**
- New skill at `plugins/command-module/skills/explain-pipeline/SKILL.md`
- A focused inventory step (reuse `/onboarding`'s `inventory.mjs` for stack/scripts/docs detection)
- Section-by-section authoring guidance with file:line grounding rules
- Catalog updates: README.md table entry + skill count, `plugin.json` description count if it references skill totals

**Out of scope**
- Auto-detecting "the pipeline" in a multi-pipeline repo — caller specifies a focus (entry point, method name, or English description)
- Prose polishing or stakeholder framing (defer to `/proof`)
- Pipeline visualization (mermaid/graphviz output) — Markdown + ASCII diagrams only, matching `/onboarding` conventions
- Non-Python pipelines as a first-class concern — the skill should be domain-agnostic but the discipline reference examples and inventory tuning lean toward Python data-science codebases the user actually works in
- Hand-bumping `plugin.json` or `marketplace.json` `version` fields (release automation owns those — see plugin `AGENTS.md`)

## Context & Research

### Relevant Code and Patterns

- `plugins/command-module/skills/onboarding/SKILL.md` — fork source. Five-section template, observation discipline, 80-column code-block constraint, ASCII diagram conventions, "Phase N" execution flow shape, post-write next-steps prompt.
- `plugins/command-module/skills/onboarding/scripts/inventory.mjs` — language/framework/scripts/docs detector. Detects Python via `requirements.txt`/`pyproject.toml`/`Pipfile`/`setup.py` (`MANIFEST_MAP` lines ~121-142). The output JSON is sufficient for `/explain-pipeline`'s stack-orientation needs; no parser changes required.
- `plugins/command-module/skills/distill/SKILL.md` — argument-hint frontmatter pattern (`argument-hint: "[optional: brief context about the fix]"`).
- `plugins/command-module/skills/proof/SKILL.md` — boundary reference for the "this is not a polishing skill" disclaimer.
- `plugins/command-module/skills/report/SKILL.md` — boundary reference for the "this is not a stakeholder-ready report" disclaimer.

### Institutional Learnings

- `docs/solutions/skill-design/script-first-skill-architecture.md` — defer deterministic work to scripts, save tokens for judgment. Justifies reusing `inventory.mjs`.
- `docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md` — when sub-agents are used, pass file paths not content. (`/explain-pipeline` is largely single-agent; this still applies if any phase ever spawns research helpers.)
- `plugins/command-module/AGENTS.md` § Skill Compliance Checklist — frontmatter rules, `@` vs backtick reference inclusion, native-tool-over-shell preference, cross-platform user-interaction conventions.

### External References

External research not run. Local pattern is strong (a near-identical sibling skill exists), domain knowledge for revintel/portbase is already in the user's head, and the work is mostly about specifying *what to write* rather than discovering new techniques.

## Key Technical Decisions

- **Fork by copy, not by abstraction.** Create `skills/explain-pipeline/` as a peer of `skills/onboarding/`, copying the inventory script and the structural conventions. **Why:** these skills will diverge over time (different sections, different focus argument, different output path); a shared base would couple them prematurely. Onboarding doesn't import from explain-pipeline today and won't in the foreseeable future.
- **Reuse `inventory.mjs` verbatim.** Copy `plugins/command-module/skills/onboarding/scripts/inventory.mjs` into `plugins/command-module/skills/explain-pipeline/scripts/inventory.mjs` unchanged. **Why:** the script's stack/framework/scripts/docs output is exactly the orientation data `/explain-pipeline` needs before it dives into pipeline-specific code-reading. No tuning needed for v1; if Python-pipeline-specific signals (e.g., detecting `prefect`/`dagster`/`luigi` orchestrators or `sklearn`/`pandas` heavy modules) prove valuable later, extend the script in a follow-up.
- **Require an explicit focus argument.** The skill takes a focus string — entry-point path, method name, or English description like "the cross-route forecaster." If absent or ambiguous after a quick scan, ask the user with the platform's blocking question tool. **Why:** auto-detecting "the pipeline" in a multi-pipeline repo (revintel has several forecast methods, portbase has multiple analytical flows) is brittle and produces wrong drafts. Cheaper to ask once than to draft the wrong pipeline.
- **Default output path: `docs/pipeline-explanations/<focus-slug>.md`.** Multiple per-pipeline docs are expected; `/onboarding`'s single-file-at-repo-root model would clobber priors. The skill creates the directory if absent. Caller may override the output path.
- **Domain-agnostic vocabulary in the template.** Use "stages" / "branches" / "methods" / "guards" rather than forecasting-specific terms. **Why:** the same template must serve revintel forecasting and portbase analytics. Reference examples in the skill body can be domain-flavored ("e.g., a forecast method, an ETL stage, an analytical step") without baking domain into the section names.
- **Preserve `/onboarding`'s observation discipline verbatim.** Same five core principles (write for humans first; show, don't tell; sections earn their place; observe, don't infer; never include secrets). The fifth-principle wording ("link, don't duplicate") still applies to existing docs the skill discovers.
- **`scripts/inventory.mjs` invoked via `node scripts/inventory.mjs --root .`** — same backtick-path convention as `/onboarding` (per AGENTS.md skill-script reference rules).

## Open Questions

### Resolved During Planning

- **Sections list?** — Use the six sections from the T016 sketch verbatim: Entry Points, Decision Tree, Per-Method Walkthroughs, Fallback Cascade, Quality Gates, Glossary. (Origin: T016.md "Shape (initial sketch)".)
- **Output filename?** — `docs/pipeline-explanations/<focus-slug>.md`. The slug is derived from the focus argument (kebab-cased, lowercased ASCII).
- **Focus argument required?** — Yes, with a "ask if missing" flow.
- **Inventory script: copy or share?** — Copy. Skill independence over deduplication; the script is small enough that copy-cost is acceptable.
- **External research needed?** — No. Local pattern is strong; user owns the domain.

### Deferred to Implementation

- **Exact `<focus-slug>` derivation rule when the focus is an English description rather than a path or symbol** — pick something simple at implementation time (e.g., kebab-case the first 4-6 words). The implementer can choose without a planning blocker.
- **Whether the inventory script ever needs Python-data-science-specific signal detection** — defer until v2. v1 ships with the verbatim script.
- **Whether to add a Phase 0.5 "find existing draft" check** — `/onboarding` always overwrites; `/explain-pipeline` writes per-pipeline files so collisions are less likely. Decide during implementation whether to warn-on-overwrite. Lean: just overwrite, matching `/onboarding`'s behavior, since drafts are cheap to regenerate.

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

Skill execution shape (mirrors `/onboarding`'s phased structure):

```
Phase 0: Resolve focus argument
  - If absent: ask the user (blocking question tool)
  - If a path: confirm it exists
  - If a symbol/description: scan for candidate entry points,
    confirm choice with user when >1 plausible match

Phase 1: Gather inventory
  - Run scripts/inventory.mjs --root .
  - Parse JSON; record stack, scripts, docs, entry points

Phase 2: Read pipeline-relevant files
  - Start from focus entry point; follow imports/calls
  - Read config files (yaml/json/toml) referenced from entry
  - Read method modules, fallback logic, quality-gate modules
  - Use native file-read tool, not shell

Phase 3: Write the explainer
  - Six sections, each with file:line citations
  - 80-column code blocks; ASCII diagrams where they help
  - "State what you observe, don't infer" applies throughout

Phase 4: Quality check (checklist)

Phase 5: Present result + next-steps prompt
  (Open / Share to Proof / Done — same shape as /onboarding)
```

Section sketch (the shape the skill produces, not the skill's own structure):

```
# Pipeline Explanation: <focus>

## 1. Entry Points
   - How a run is invoked (CLI, function call, scheduler)
   - Config shape (referenced files + key fields w/ file:line)
   - What "a run" means (inputs, outputs, side effects)

## 2. Decision Tree
   - Method/branch selection logic w/ file:line for each branch
   - ASCII flow if branches are nested

## 3. Per-Method Walkthroughs
   ### Method A
     - When it fires (conditions, file:line)
     - Inputs needed
     - What it does (algorithmic steps, file:line)
   ### Method B ...

## 4. Fallback Cascade
   - Trigger conditions (file:line)
   - Order of fallback attempts
   - Coverage rules (when no fallback applies)

## 5. Quality Gates
   - Which gates apply to which methods (table)
   - Failure -> fallback wiring (file:line)

## 6. Glossary
   - Code term -> business term mapping
   - Domain terms used inside the codebase
```

## Implementation Units

- [ ] **Unit 1: Skill scaffolding + inventory script**

**Goal:** Create the skill directory with valid frontmatter and the copied inventory script ready to run.

**Requirements:** R6

**Dependencies:** None

**Files:**
- Create: `plugins/command-module/skills/explain-pipeline/SKILL.md` (frontmatter + placeholder body)
- Create: `plugins/command-module/skills/explain-pipeline/scripts/inventory.mjs` (verbatim copy of `plugins/command-module/skills/onboarding/scripts/inventory.mjs`)

**Approach:**
- Frontmatter fields: `name: explain-pipeline`, `description: "Generate a grounded Markdown draft that explains how a data pipeline actually behaves -- entry points, decision branches, per-method walkthroughs, fallback cascades, quality gates. Use when ... <list trigger phrases>. Output is a file:line-grounded draft, not stakeholder-polished prose."`, `argument-hint: "<entry point path, method name, or short description of the pipeline to explain>"`.
- Quote the description (per AGENTS.md frontmatter rule — colons inside the string need quoting to keep `js-yaml` strict parsing happy).
- Copy `inventory.mjs` byte-for-byte; do not refactor.

**Patterns to follow:**
- `plugins/command-module/skills/onboarding/SKILL.md` frontmatter shape
- `plugins/command-module/skills/distill/SKILL.md` `argument-hint` placement

**Test scenarios:**
- `bun test tests/frontmatter.test.ts` passes (no YAML parse error)
- Running `node plugins/command-module/skills/explain-pipeline/scripts/inventory.mjs --root .` from the repo root produces valid JSON

**Verification:**
- `bun run release:validate` passes
- The skill appears as a discoverable skill in the plugin (no broken refs)

---

- [ ] **Unit 2: Focus-argument resolution + entry-point discovery flow**

**Goal:** Specify (in SKILL.md prose) how the skill turns the user's focus argument into a concrete starting file before any reading begins.

**Requirements:** R3, R5

**Dependencies:** Unit 1

**Files:**
- Modify: `plugins/command-module/skills/explain-pipeline/SKILL.md` (add Phase 0 section)

**Approach:**
- Phase 0 resolves the focus argument:
  - If a file path: confirm via native file-read; if missing, ask the user.
  - If a symbol or English description: scan repo for plausible entry points using the native file-search/glob tool (e.g., search for top-level functions or files matching the description). When more than one plausible match exists, present them to the user with the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini); fall back to numbered options in chat if no question tool is available.
  - If absent: ask the user "Which pipeline should I explain? (entry point path, method name, or short description)" before doing anything else.
- Record the resolved entry-point path; subsequent phases read outward from there.
- Specify that focus-derivation should *not* assume "the" pipeline — repos may host many.

**Patterns to follow:**
- AGENTS.md § Cross-Platform User Interaction (blocking question tool + fallback)
- AGENTS.md § Tool Selection in Agents and Skills (native search/read, not shell)

**Test scenarios:**
- (Manual smoke) Skill invoked with no argument prompts the user.
- (Manual smoke) Skill invoked with a non-existent path asks for clarification rather than silently failing.
- (Manual smoke) Skill invoked with an English description scans the repo and presents candidate entry points when more than one matches.

**Verification:**
- The Phase 0 prose makes the resolution sequence unambiguous to a fresh reader.

---

- [ ] **Unit 3: Section-by-section authoring template**

**Goal:** Specify (in SKILL.md prose) the six output sections with concrete authoring rules and file:line examples.

**Requirements:** R1, R2, R3

**Dependencies:** Unit 1

**Files:**
- Modify: `plugins/command-module/skills/explain-pipeline/SKILL.md` (Phase 3 section)

**Approach:**
- Six sections, in order: Entry Points, Decision Tree, Per-Method Walkthroughs, Fallback Cascade, Quality Gates, Glossary.
- For each section, specify: question answered, what to include, what evidence shape (file:line, ASCII diagram, table), and what to do when the section is genuinely empty (e.g., "no fallback logic detected" — say so plainly, do not fabricate).
- Per-method walkthroughs use one `###` subsection per method discovered; do not invent methods that aren't in the code.
- Quality Gates uses a table mapping gate -> methods covered -> failure behavior.
- Glossary uses a two-column table: code term / business meaning. Empty if no jargon detected.
- Domain-agnostic vocabulary throughout — "stage," "branch," "method," "guard" — with examples that flag both forecasting (revintel) and analytics (portbase) flavors.
- Reuse `/onboarding`'s formatting rules verbatim: 80-column code blocks, backticks for paths/identifiers, ASCII diagrams stacked vertically, horizontal rules between top-level sections.
- Every algorithmic claim must carry a `path:line` citation. The skill must not state "method X fires when Y" without a citation; if no citation can be produced, the claim must be omitted.

**Patterns to follow:**
- `plugins/command-module/skills/onboarding/SKILL.md` § Phase 3 (formatting requirements, ASCII diagram width rules)
- `/onboarding`'s "show, don't just tell" principle for diagrams and tables

**Test scenarios:**
- (Manual smoke) Skill applied to a revintel forecast pipeline produces all six sections with file:line refs throughout.
- (Manual smoke) Skill applied to a pipeline without quality gates produces a Quality Gates section that states the absence plainly rather than fabricating gates.
- (Manual smoke) Skill applied to a portbase analytical pipeline (different domain vocabulary) still uses the same section names without sounding forced.

**Verification:**
- Section template prose is clear enough that a different agent reading the skill could produce comparable output on a third codebase.

---

- [ ] **Unit 4: Discipline + quality-check phase**

**Goal:** Carry forward `/onboarding`'s observation discipline and add a checklist tuned to the pipeline use case.

**Requirements:** R1, R4, R5

**Dependencies:** Unit 3

**Files:**
- Modify: `plugins/command-module/skills/explain-pipeline/SKILL.md` (Core Principles + Phase 4 quality check)

**Approach:**
- Core Principles section mirrors `/onboarding`'s five principles, adapted:
  1. Write for humans first
  2. Show, don't just tell (ASCII flows for branching/fallback are particularly valuable here)
  3. Six sections, each earning its place
  4. **State what you observe, not what you must infer** (carry verbatim — this is the load-bearing principle)
  5. Never include secrets
  6. Link, don't duplicate (existing docs the skill encounters in `inventory.mjs`'s `docs` list)
- Add an explicit "this is a draft, not a stakeholder doc" callout near the top, with a one-line pointer to `/proof` for prose polishing and a contrast with `/onboarding` and `/distill`.
- Phase 4 quality checklist (boxes the skill walks through before writing):
  - Every algorithmic claim cites `path:line`
  - No fabricated rationale ("we chose X because…") unless lifted verbatim from a docstring/comment
  - No fragility / risk / quality assessments — only what the code says
  - Empty sections are stated plainly, not padded
  - No secrets, env values, or credential strings (extract names only)
  - 80-column rule applied to all code blocks
  - File paths in citations correspond to real files from the inventory output

**Patterns to follow:**
- `plugins/command-module/skills/onboarding/SKILL.md` § Phase 4 quality check
- `plugins/command-module/skills/onboarding/SKILL.md` § Core Principles wording for the observation discipline

**Test scenarios:**
- (Manual smoke) On a pipeline with sparse comments, the draft does not invent design rationale.
- (Manual smoke) The draft does not include a "risks" or "fragility" section.

**Verification:**
- Discipline language reads as load-bearing, not boilerplate.

---

- [ ] **Unit 5: Catalog updates + validation**

**Goal:** Register the skill in plugin docs so discovery and counts stay accurate; run the standard validation pipeline.

**Requirements:** R6

**Dependencies:** Units 1-4

**Files:**
- Modify: `plugins/command-module/README.md` (add `/explain-pipeline` row to the "Workflow Utilities" table next to `/onboarding`; bump skill count `42 -> 43` in the Components table)
- Verify: `plugins/command-module/.claude-plugin/plugin.json` description (only modify if the description references skill totals — current value `"Personal development toolkit for code review, research, design, and workflow automation."` does not, so likely no change needed)

**Approach:**
- Place the new row directly under `/onboarding` in `### Workflow Utilities` (these two skills are siblings; readers scanning for "documentation generators" should see them together).
- Row description (one line): "Generate a grounded Markdown draft explaining how a data pipeline behaves (entry points, branches, fallbacks, gates), with file:line citations."
- Bump the Skill count from `42` to `43` in the Components table.
- Do **not** bump version in `plugin.json` or `marketplace.json` — release automation owns those (per plugin `AGENTS.md`).
- Do **not** add a `CHANGELOG.md` entry — release automation owns that.

**Patterns to follow:**
- AGENTS.md § Plugin Maintenance (run `bun run release:validate` after adding a skill)
- AGENTS.md § Pre-Commit Checklist (no manual version bumps; counts verified)

**Test scenarios:**
- `bun test` (full suite) passes
- `bun run release:validate` passes
- `bun test tests/frontmatter.test.ts` passes (catches any unquoted-colon YAML errors in the new SKILL.md description)

**Verification:**
- README.md table renders with the new row in correct alphabetical/logical position
- Components table count matches actual skill count (43)
- Validation script reports no warnings about the new skill

## System-Wide Impact

- **Interaction graph:** The skill is self-contained — no agents dispatched, no other skills invoked at runtime. It does read `inventory.mjs`'s output, which is also used by `/onboarding`; copying the script (rather than sharing) means future onboarding-side changes do not silently change explain-pipeline behavior.
- **Error propagation:** If `inventory.mjs` errors, the skill reports and stops — same fail-fast behavior as `/onboarding` Phase 1. If focus resolution fails after asking the user, stop rather than guessing.
- **State lifecycle risks:** The skill creates `docs/pipeline-explanations/<slug>.md`. If the file exists, it is overwritten without prompting (matches `/onboarding`'s overwrite-on-regenerate behavior). Drafts are cheap to regenerate; loss-of-edits risk is low because polished versions live elsewhere (e.g., shared with stakeholders via `/proof`).
- **API surface parity:** Documentation surfaces in the README skills table and the plugin manifest description must stay in sync; Unit 5 enforces this. No CLI/converter changes — the skill is plain Markdown that converters copy through.
- **Integration coverage:** No new converter behavior is introduced. The skill follows existing skill-conversion paths (claude/opencode/codex/etc.) without target-specific work. Existing per-target writer tests already cover the "skills get copied" path; no new test fixtures needed.

## Risks & Dependencies

- **Risk: domain-leaky vocabulary creeps into the section template.** Mitigation: Unit 3 explicitly calls for "stage / branch / method / guard" wording with both forecasting and analytics flavor examples. Reviewer should grep the new SKILL.md for "forecast" / "blend" / "cross-route" — those should appear only as examples, never as section names.
- **Risk: discipline drift — the skill produces inferred-rationale prose that reads convincing but isn't grounded.** Mitigation: Unit 4 carries `/onboarding`'s "state what you observe, don't infer" principle verbatim and adds an explicit checklist item that every algorithmic claim must cite `path:line`.
- **Risk: skill collides with future stakeholder-facing skill.** Mitigation: explicit boundary callout in the skill body — `/explain-pipeline` produces a draft, `/proof` polishes prose, `/distill` captures problem-solution pairs, `/onboarding` orients new contributors. Boundaries are stated, not implied.
- **Dependency: `inventory.mjs` continues to detect Python correctly.** It does today (lines ~127-130 of the script handle `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`). No action needed unless a Python project the user runs the skill on uses something exotic.
- **Dependency: skill-author conventions in plugin AGENTS.md remain stable.** They have not changed materially during this branch; no coordination needed.

## Documentation / Operational Notes

- README.md table update + count bump (Unit 5) — these are the only doc surfaces that need touching.
- No release notes to author by hand (release automation owns the changelog).
- After the first real use on revintel and portbase, capture any discipline-violation patterns the user catches in `docs/solutions/skill-design/` so future iterations of the skill (or its sibling `/onboarding`) can learn from them.

## Sources & References

- **Origin task:** [missioncontrol/tracking/command-module/tasks/T016.md](../../../missioncontrol/tracking/command-module/tasks/T016.md)
- Fork source: [plugins/command-module/skills/onboarding/SKILL.md](../../plugins/command-module/skills/onboarding/SKILL.md)
- Inventory script: [plugins/command-module/skills/onboarding/scripts/inventory.mjs](../../plugins/command-module/skills/onboarding/scripts/inventory.mjs)
- Plugin authoring rules: [plugins/command-module/AGENTS.md](../../plugins/command-module/AGENTS.md) § Skill Compliance Checklist
- Boundary references: [plugins/command-module/skills/proof/SKILL.md](../../plugins/command-module/skills/proof/SKILL.md), [plugins/command-module/skills/distill/SKILL.md](../../plugins/command-module/skills/distill/SKILL.md)
- Institutional learnings: [docs/solutions/skill-design/script-first-skill-architecture.md](../solutions/skill-design/script-first-skill-architecture.md), [docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md](../solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md)
