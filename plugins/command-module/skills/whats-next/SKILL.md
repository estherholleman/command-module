---
name: whats-next
description: 'Strategic execution advisor that translates sharpened concepts and strategic decisions into opinionated task recommendations and self-contained prompt files. Use when strategic thinking is done and the user wants to know what to do next, says ''what should I work on'', ''what''s next'', ''translate this to tasks'', ''create prompts from this'', or wants to move from thinking to execution.'
argument-hint: "[optional: specific topic, workstream, or focus area]"
---

# Strategic Execution Advisor

Translate strategic thinking into opinionated, strategically-grounded task recommendations and self-contained prompt files for execution conversations. The core value is strategic judgment -- explaining *why* each task matters, recommending what *not* to do, and presenting trade-offs in strategic terms.

This skill reads two types of durable artifacts:
- **Knowledge artifacts** in `docs/strategy/YYYY-MM-DD-<topic>.md` -- produced by /concept sessions
- **Shared vocabulary** in `docs/strategy/context.md` -- accumulated terms, frameworks, decisions, and open questions

This skill produces two types of output:
- **Prompt files** in `docs/prompts/` -- self-contained execution briefs, one per discrete execution conversation
- **Tracked tasks** via the `capture` skill -- for items that warrant formal task tracking

## Core Principles

1. **Judge, don't list.** Every recommendation needs strategic reasoning. "Do X" is incomplete without "because Y." Recommendations without reasoning are just a backlog dump.
2. **Say what not to do.** The most valuable strategic advice is often what to defer. Explain why something that looks ready isn't the right next move.
3. **Present trade-offs in strategic terms.** When multiple paths exist, frame the choice in terms of strategic outcomes, not effort or complexity. "This path accelerates X but delays Y" beats "this is easier."
4. **Evidence before opinion.** Read and analyze all artifacts before forming recommendations. The portfolio state drives the advice, not assumptions about what the user wants to hear.
5. **Prompt files are execution briefs, not plans.** Each prompt file should give a fresh conversation everything it needs to start working -- context, action, file paths, strategic reasoning -- without requiring the reader to load additional artifacts.

## Execution Flow

### Phase 0: Ground

**Load strategic context:**
- If `docs/strategy/context.md` exists, read it fully. This is the shared vocabulary and strategic context.
- Scan `docs/strategy/` for all knowledge artifacts (excluding context.md) using the native file-search/glob tool (e.g., Glob in Claude Code). Note each artifact's topic, date, and status from frontmatter.
- Check `docs/prompts/` for existing prompt files to understand what execution work has already been scoped.

**Handle empty state:**
If no strategy artifacts and no context.md exist, this is a first-class state -- not an error. Explain that strategic analysis needs input to work from, and suggest running the `concept` skill to begin building the knowledge base or the `strategy` skill to sketch the big picture. Do not proceed with empty analysis.

**Establish scope:**
- If arguments were provided, use them to focus the analysis on a specific topic, workstream, or tension.
- If arriving as a handoff from a /strategy session, the strategic context is already warm -- acknowledge what was just discussed rather than re-presenting the full portfolio.
- If invoked standalone with existing artifacts, proceed to Phase 1 for full analysis.

**Transition:** Once the portfolio is loaded and scope is established, move to Phase 1.

### Phase 1: Analyze

The core value phase. Read all knowledge artifacts and context.md. Build a strategic picture across these dimensions:

**Maturity:** Which concepts are sharp enough to act on? Which are still forming and would produce weak execution if acted on now?

**Tensions:** Where do concepts pull in different directions? Acting on one may foreclose or complicate another.

**Momentum:** What has energy and recent attention? What has gone cold? Momentum is a real input -- a concept with recent sharpening cycles is cheaper to execute than one that needs re-grounding.

**Dependencies:** What naturally sequences first? Not task dependencies, but strategic dependencies -- which decisions enable or constrain others?

**Produce an opinionated assessment:**

- **Recommended actions** -- tasks worth doing now, each with strategic reasoning explaining why this is the right moment.
- **Recommended deferrals** -- things that look ready but shouldn't be acted on yet, with reasoning. This is often the most valuable part.
- **Strategic options** -- when genuinely different paths exist, present them with trade-offs framed in strategic terms. Not "Option A is easier" but "Option A accelerates the portfolio breadth play, Option B deepens the current strongest concept."

### Phase 2: Present and Approve

Present the assessment to the user in a structured format:

**States:**

```
assessment-presented -> user-reaction -> revision-or-approval -> cycle-decision
      ^                                                              |
      |________________________ revise ______________________________|
                                   |
                             approved (-> Phase 3)
```

**`assessment-presented`** -- Show recommended tasks grouped by theme or priority. Each task includes: what to do, why it matters strategically, and suggested approach. Show "not now" items with reasoning. When options exist, present paths with trade-offs.

**`user-reaction`** -- Wait for the user to respond. Do not proceed without input. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the assessment and wait for the user's reply before proceeding.

**`revision-or-approval`** -- The user may:
- Approve all recommendations
- Approve selectively (some tasks, not others)
- Push back on reasoning or priority
- Request changes or additions
- Ask to see different options explored

**`cycle-decision`** -- If the user requested changes, revise the assessment and return to `assessment-presented`. If the user has approved (fully or selectively), transition to Phase 3 with the approved set.

### Phase 3: Execute

Two parallel outputs for the approved items:

**1. Write prompt files**

Create `docs/prompts/` if it doesn't exist. Write one prompt file per approved execution conversation. Follow the existing format in `docs/prompts/`:

```markdown
# <Title with action type>

<One-line action instruction -- what skill to run or what to do>

## What to do

<Brief description of the work>

## Key context

- <Context bullet with file paths and strategic reasoning>
- <Another context bullet>
- <Relevant references>
```

Keep prompt files brief and self-contained. Each should give a fresh conversation everything it needs without loading additional artifacts. Use file paths to point at relevant resources rather than inlining content.

**2. Capture tracked tasks**

For each approved item that warrants a tracked task, load the `capture` skill with the task description and relevant file paths. Pass paths, not content -- the `capture` skill reads what it needs.

Not every prompt file needs a tracked task. Prompt files are execution briefs; tracked tasks are for items that need status visibility in the project tracking system. Use judgment about which items warrant both.

### Closing

Summarize what was produced:

```
Execution plan ready.

Prompt files written:
- docs/prompts/<file-1>.md
- docs/prompts/<file-2>.md

Tasks captured: [count, or "none -- prompt files are sufficient for this work"]
Deferred: [brief list of items recommended against, with one-line reasoning each]
```
