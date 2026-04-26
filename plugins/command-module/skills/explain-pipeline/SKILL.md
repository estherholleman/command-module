---
name: explain-pipeline
description: "Generate a grounded Markdown draft that explains how a data pipeline actually behaves -- entry points, decision branches, per-method walkthroughs, fallback cascades, quality gates, glossary -- with file:line citations on every algorithmic claim. Use when asked to 'explain this pipeline', 'document how this forecast/pipeline/algorithm works', 'write a walkthrough of method selection', 'draft a partner explainer for our forecasting logic', or 'trace how this analytical flow decides what to do'. The output is a draft with citations, not stakeholder-polished prose -- pair with /proof for narrative polish."
argument-hint: "<entry point path, method/function name, or short description of the pipeline to explain>"
---

# Explain Pipeline

Walk a data pipeline's source code and produce a grounded Markdown draft -- with file:line citations -- that explains how the pipeline actually behaves: where a run starts, how it picks which method to use, what each method does, what fallbacks fire when, and what quality gates apply.

This skill is for data-science codebases (forecasting pipelines, analytical flows, ETL with branching method selection) where readers -- internal reviewers, partner-facing explainer drafts, future maintainers -- need to understand decision logic without reading the source themselves.

The output is a **draft**, not a finished stakeholder doc. It is faithful to the code; narrative polish belongs to a separate pass.

## What this is not

- **Not `/onboarding`** -- that orients a new contributor to a codebase. This explains how one specific pipeline decides what to do.
- **Not `/proof`** -- that polishes prose. This produces grounded source material for `/proof` to polish.
- **Not `/distill`** -- that captures a problem-solution pair. This describes algorithmic behavior, not a fix.

If the user wants stakeholder-polished prose, generate the draft here, then load the `proof` skill on the result.

## Core Principles

1. **Write for humans first** -- The reader is a smart person who is not the code author. Prose first, code references in support.
2. **Show, don't just tell** -- Use ASCII flow diagrams for branching and fallback cascades, markdown tables for gate-to-method mappings, and backticks for every path/identifier.
3. **Six sections, each earning its place** -- If a section has no content in the code, say so plainly. Do not pad and do not invent.
4. **State what you can observe, not what you must infer** -- Every algorithmic claim cites `path:line`. If the code does not reveal *why* a decision was made, do not guess. Do not write fragility, risk, or quality assessments. Do not invent design rationale.
5. **Never include secrets** -- Reference environment variable *names* only (`STRIPE_SECRET_KEY`), never their values. Never read `.env` -- only `.env.example` or templates.
6. **Link, don't duplicate** -- If the inventory surfaces an existing doc that already explains a piece (a glossary, a config reference, a prior explainer), link to it inline rather than re-explaining.

## Execution Flow

### Phase 0: Resolve the Focus Argument

Before reading any code, turn the user's focus argument into a concrete starting file.

The focus argument can be:

- **A file path** (e.g., `revintel/src/forecasting/pipeline.py`) -- Confirm it exists using the native file-read tool. If it does not exist, ask the user to clarify.
- **A symbol or function name** (e.g., `select_method`, `run_forecast`) -- Use the native file-search/glob tool (e.g., `Glob` in Claude Code) and the native content-search tool (e.g., `Grep` in Claude Code) to locate plausible entry points. If exactly one match is found, use it. If multiple are plausible, ask the user to choose.
- **An English description** (e.g., "the cross-route forecaster", "the route-quality pipeline") -- Scan the repo using native search tools for files or top-level functions matching the description. If multiple plausible candidates exist, ask the user to choose.
- **Absent** -- Ask the user "Which pipeline should I explain? (entry point path, function/method name, or short description)" before doing anything else.

When asking the user a clarifying question, use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present numbered candidate options in chat and wait for a reply before proceeding.

Record the resolved entry-point path and a derived **focus slug** for the output filename. The slug is a kebab-cased, lowercased ASCII rendering of the focus argument:

- Path -> use the file's basename without extension (`pipeline.py` -> `pipeline`).
- Symbol -> use the symbol name lowercased (`runForecast` -> `run-forecast`).
- Description -> kebab-case the first 4-6 meaningful words (`"cross-route forecaster"` -> `cross-route-forecaster`).

Do not assume there is one canonical pipeline in the repo. Many data-science codebases host several -- ask rather than guess.

### Phase 1: Gather Inventory

Run the bundled inventory script (`scripts/inventory.mjs`) to get a structural map of the repository:

```bash
node scripts/inventory.mjs --root .
```

Parse the JSON output. Record:

- Project name, languages, frameworks
- Available scripts/commands
- Existing documentation files (with first-heading titles for triage)
- Test infrastructure
- Infrastructure and external dependencies (env files, services)

The inventory tells you what runtime, frameworks, and configuration shape the pipeline runs inside. It does not, by itself, tell you what the pipeline *does* -- Phase 2 reads code for that.

If the script fails or returns an error field, report the issue to the user and stop. Do not draft an explainer from incomplete data.

### Phase 2: Read Pipeline-Relevant Files

Starting from the resolved focus entry point, read outward. Use the native file-read tool, never shell `cat`/`head`.

Read in priority order (batch parallel reads where files do not depend on each other):

1. **The focus entry point file** -- Establish the run signature: how is the pipeline invoked, what are its inputs, what does it return, what side effects does it produce.
2. **Configuration the entry point references** -- YAML/JSON/TOML files loaded at start, schema definitions, default-value modules. Skip `.env` files; read `.env.example` only.
3. **Method/branch modules** -- Files containing the per-method logic (each `Method` class, each strategy function, each named branch). Follow imports from the entry point.
4. **Fallback logic modules** -- Anywhere `try`/`except`, `if not <quality_gate>`, retry policies, or "if A fails then B" chains live in the call graph from the entry point.
5. **Quality-gate modules** -- Validation, plausibility checks, threshold modules, anything the methods or fallbacks check before accepting an output.
6. **Existing documentation surfaced by the inventory** -- The inventory's `docs` list includes each file's title. Skim titles; read in full only those whose titles indicate direct relevance to this pipeline (e.g., a prior explainer, a methodology doc, a glossary).

Read only what is needed to write the six sections with concrete file:line citations. The point is grounded specificity, not exhaustive coverage. A simple pipeline might need 4-6 files; a multi-method forecaster with layered fallbacks might need 15-25.

Do not read speculatively. Every file read should be traceable to a specific section that needs it.

### Phase 3: Write the Explainer

Write the draft to `docs/pipeline-explanations/<focus-slug>.md`. Create the `docs/pipeline-explanations/` directory if it does not exist. If the file already exists, overwrite it -- drafts are cheap to regenerate.

**Title**: `# Pipeline Explanation: <focus>` where `<focus>` is the human-readable focus the user asked about (not the slug).

**Writing style** -- The document should read like a careful engineer walking a colleague through the code, pointing at lines as they go. Plain, direct, citation-heavy.

Voice and tone:

- Active voice and present tense: "`select_method()` reads the route's history length and dispatches to the appropriate forecaster" -- not "the appropriate forecaster is dispatched to based on...".
- Lead with what the code does, then the line reference: "When `history_length < 90`, the pipeline selects the growth-rate method (`forecaster.py:142`)."
- Match the formality of the codebase. Internal-facing analytical code can be casual; partner-facing explainer drafts should err on the side of precise.

Clarity:

- Every algorithmic claim carries a `path:line` citation. Without a citation, omit the claim.
- Prefer concrete over abstract: "`compute_blend_weights()` averages the last 4 weeks of MAPE per method" -- not "the blend module computes weights using historical accuracy data".
- Define a code term the first time it appears, in context.

What to avoid:

- No fabricated rationale -- "we chose X because" is allowed only if lifted verbatim from a docstring or comment with the citation.
- No fragility, risk, edge-case, or quality assessments -- only what the code says.
- No marketing language, no hedge words, no meta-commentary about the document.
- No domain vocabulary the code does not use (do not invent business terms).

**Formatting requirements** -- apply consistently:

- Use backticks for all paths, file names, function/class/method names, configuration keys, and environment variable names.
- Use `##` headers for the six sections, with horizontal rules (`---`) between them.
- Code blocks (ASCII flows, command examples, snippets) capped at **80 columns** -- markdown renders code blocks with `white-space: pre`, so wide lines cause horizontal scrolling. Tables are fine; renderers wrap them.
- ASCII flow diagrams stack vertically (no more than 2 boxes on a horizontal line, labels under 20 characters).

#### Section 1: Entry Points

Answer: How is a run invoked, what does it take as input, what does it produce, and what configuration shapes a run?

Cover:

- The invocation surface(s): CLI command, function call, scheduled job, API endpoint -- whatever fires the pipeline. Cite the entry point file:line.
- The run signature: inputs (with types if visible), outputs, side effects (writes to disk, DB, queue).
- Configuration shape: the config files or default modules referenced from the entry point. List the key fields the pipeline reads, with file:line for each. Reference variable *names* for env-driven config, not values.
- What "a run" means in plain language: one route's forecast for one horizon? one daily batch over all SKUs? one analytical pass over a date range? Lift this from the code, not from intuition.

If multiple entry points exist (CLI + library function + scheduled job), document each that the focus argument plausibly covers.

#### Section 2: Decision Tree

Answer: How does the pipeline decide which method, branch, or path to take for a given input?

Cover:

- The selection logic: every `if`/`match`/`switch`/dispatch table that picks between methods or branches. Cite each branch with `path:line`.
- The conditions: what variable, threshold, or feature each branch keys on (e.g., "history length", "category type", "presence of recent data").
- An ASCII flow diagram when nesting is non-trivial. Vertical-stack format:

```
+------------------------+
| select_method()        |
| forecaster.py:118      |
+----------+-------------+
           |
   history_length < 90?
           |
       +---+---+
       |       |
      yes      no
       |       |
       v       v
  growth-rate  bayesian
  :142         :167
```

- If selection logic is a flat dispatch table (e.g., a dict mapping method name -> function), present it as a table:

```
| Method        | Selected when                   | Cited at         |
|---------------|---------------------------------|------------------|
| `growth_rate` | `history_length < 90`           | `forecaster.py:142` |
| `bayesian`    | `history_length >= 90`          | `forecaster.py:167` |
| `cross_route` | `category in CROSS_ROUTE_TYPES` | `forecaster.py:189` |
```

If the pipeline has only one method (no branching), say so plainly: "This pipeline does not branch -- a single method handles every input. Section 3 walks through that method."

#### Section 3: Per-Method Walkthroughs

Answer: For each method or branch the pipeline can pick, what does it do step by step?

Use one `###` subsection per method discovered in Section 2. Do not invent methods that are not in the code. If only one method exists, this section has one subsection.

For each method:

- **When it fires** -- The condition or trigger, with `path:line`. Match the row from the Section 2 table where one exists.
- **Inputs** -- What this method needs from upstream: data shape, config keys, prior-state lookups. Cite the lines where each is read.
- **Algorithm** -- The steps the method executes, in order, each with a citation. Be specific about transformations, smoothing, filters, model fits, output shaping. Lift the step labels from the code -- function names, comment headings, log messages -- where possible.
- **Outputs** -- The shape returned to the caller and where it goes next.

For methods that wrap or compose other methods (e.g., a "blend" method that combines two underlying methods), walk through the composition: which children fire, how their outputs combine, where the combination weights come from.

#### Section 4: Fallback Cascade

Answer: When a method does not produce a usable output, what happens next?

Cover:

- **Trigger conditions** -- What counts as "method failed" or "method output unusable" in this pipeline. Cite the check site (`path:line`). This is often a quality-gate failure (Section 5), an exception, or an empty/null result.
- **Cascade order** -- The sequence of fallback attempts. Use a numbered list or ASCII flow. Cite each step.
- **Coverage rules** -- What the pipeline does when no fallback applies (skip the input, return null, return a sentinel, raise). Cite the terminal branch.

If no fallback logic exists, state plainly: "This pipeline has no fallback logic -- if the primary method fails, the failure propagates to the caller. See `<file:line>` for the call site."

ASCII cascade diagram (vertical, narrow):

```
Primary method
    |
    +--> succeeds --> return
    |
    +--> fails (gate G1, quality.py:34)
         |
         v
    Fallback A (forecaster.py:212)
         |
         +--> succeeds --> return
         |
         +--> fails (gate G2, quality.py:51)
              |
              v
         Fallback B (forecaster.py:247)
              |
              +--> succeeds --> return
              |
              +--> fails --> coverage rule
                            (forecaster.py:271)
```

#### Section 5: Quality Gates

Answer: What checks does the pipeline run on intermediate or final outputs, and what do those checks decide?

Cover:

- A table mapping each gate to (a) which methods it applies to, (b) what it checks, (c) what happens on failure. Cite each row with `path:line`.

```
| Gate              | Applies to       | Checks                         | On failure          | Cited at         |
|-------------------|------------------|--------------------------------|---------------------|------------------|
| `min_history`     | growth_rate, bayesian | history length >= threshold | drop method, fall back | `quality.py:34` |
| `output_finite`   | all              | no NaN or inf in forecast      | raise + fall back   | `quality.py:51` |
| `monotonicity`    | bayesian only    | output series non-decreasing   | drop output         | `quality.py:78` |
```

- A short prose paragraph describing how gate failures wire to the fallback cascade -- cite the wiring site.

If no quality gates exist, state plainly: "No explicit quality gates in this pipeline. The methods' outputs are returned as-is. See `<file:line>`."

#### Section 6: Glossary

Answer: What vocabulary does a reader of this draft need to understand?

Two-column table mapping code term -> meaning in this codebase. Include:

- **Domain terms** the code uses that a reader outside the project would not immediately recognize.
- **Method names**, especially when the code's name and the human/business name diverge (e.g., the code calls it `cross_route` but internally it is described as "borrowing from analogous routes").
- **Configuration concepts** that appear in the explainer and need a one-liner to be intelligible.

```
| Term            | Meaning in this pipeline                              |
|-----------------|-------------------------------------------------------|
| `cross_route`   | Forecaster that borrows demand patterns from analogous routes when own history is sparse. `forecaster.py:189`. |
| `blend`         | Weighted average of two or more method outputs; weights from `compute_blend_weights()` (`blend.py:24`). |
| Coverage rule   | The pipeline's behavior when every fallback fails: returns `None` and logs a `coverage_failed` event (`forecaster.py:271`). |
```

If the pipeline has no jargon (rare in real codebases but possible), state: "No domain-specific vocabulary required for this pipeline."

#### Inline Documentation Links

While writing each section, check whether any file from the inventory's `docs` list is directly relevant. If so, link inline:

> The blend-weight derivation is documented separately -- see [`docs/methodology/blend-weights.md`](docs/methodology/blend-weights.md) for the rationale.

Do not create a separate references section. If no relevant docs exist for a section, the section stands alone.

### Phase 4: Quality Check

Before writing the file, walk this checklist:

- [ ] Every algorithmic claim cites `path:line`. Claims without citations have been omitted.
- [ ] No fabricated rationale -- "we chose X because" appears only when lifted verbatim from a docstring or comment with citation.
- [ ] No fragility, risk, edge-case, or quality assessments. Only what the code says.
- [ ] Empty sections are stated plainly ("No fallback logic in this pipeline"), not padded with speculation.
- [ ] No secrets, API keys, tokens, or credential values anywhere. Environment variable *names* only.
- [ ] All code-block content (ASCII flows, examples) fits within 80 columns.
- [ ] All file paths in citations correspond to real files from the inventory output.
- [ ] Six sections present and ordered: Entry Points, Decision Tree, Per-Method Walkthroughs, Fallback Cascade, Quality Gates, Glossary.
- [ ] Backticks applied to every path, identifier, configuration key, and environment variable name.
- [ ] Section vocabulary is domain-agnostic in the headers ("methods", "branches", "gates"); domain terms appear in the body where the code uses them.
- [ ] No marketing language, hedge words, or meta-commentary about the document.

Then write the file to `docs/pipeline-explanations/<focus-slug>.md`.

### Phase 5: Present Result

After writing, inform the user that the draft has been generated and report the path. Offer next steps using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present numbered options and wait for a reply.

Options:

1. Open the file for review
2. Polish with `/proof`
3. Done

Based on selection:

- **Open for review** -> Open `docs/pipeline-explanations/<focus-slug>.md` using the platform's file-open or editor mechanism.
- **Polish with `/proof`** -> Load the `proof` skill on the just-written file. The draft is the input; `/proof` produces the polished prose.
- **Done** -> No further action.
