---
title: "feat(whats-next): Add /whats-next strategic execution advisor skill"
type: feat
status: active
date: 2026-04-07
origin: docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md
---

# feat(whats-next): Add /whats-next strategic execution advisor skill

## Overview

Add the third skill in the strategy toolkit: `/whats-next`, a strategic execution advisor that analyzes the output of /concept and /strategy sessions and translates sharpened concepts into opinionated, strategically-grounded task recommendations and self-contained prompt files for execution conversations.

## Problem Frame

When strategic thinking is done (/concept has sharpened the ideas, /strategy has reviewed the portfolio), there's a gap between "we know what we think" and "we know what to do." Currently this translation happens ad-hoc: the user manually decides what tasks to create and writes prompt files by hand. /whats-next formalizes the Translator mode from the strategic team vision (see origin: `docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md`, R20-R26).

The core value is strategic judgment, not mechanical task capture. The skill explains *why* each task matters, recommends what *not* to do, and presents trade-offs in strategic terms when multiple paths exist.

## Requirements Trace

- R20. Analyze output of strategy/concept sessions across deliverables and workstreams
- R21. Present task overview with reasoning about why each task matters and suggested approach/order
- R22. Opinionated perspective: recommend what to do and what not to do, multiple paths with strategic trade-offs
- R23. Options with trade-offs in strategic terms when genuinely different approaches exist
- R24. After user approval, delegate to `/capture` for mechanical task creation
- R25. Write prompt files to `docs/prompts/` -- self-contained execution briefs
- R26. Work both as end-phase of /strategy and standalone
- R27. Read `docs/strategy/context.md` for shared vocabulary and strategic context (knowledge layer)
- R28. Read knowledge artifacts from `docs/strategy/` (dated markdown files)

## Scope Boundaries

- Not building or modifying `/capture` -- it's a sibling plugin skill that handles missioncontrol integration
- Not modifying `/concept` or `/strategy` -- only reading their outputs
- Not building a task tracking system -- `/capture` handles the missioncontrol integration
- Not modifying `docs/strategy/context.md` -- /whats-next reads but does not write strategic artifacts (ownership belongs to /concept and /strategy)
- Not implementing multi-path execution or automated routing -- the skill presents options, the user decides

## Context & Research

### Relevant Code and Patterns

- `plugins/command-module/skills/concept/SKILL.md` -- sibling skill, primary reference for conventions (flat naming, frontmatter, context.md loading, state machine pattern, reference file inclusion)
- `plugins/command-module/skills/strategy/SKILL.md` -- sibling skill, reference for full portfolio scan pattern (read all artifacts, note topic/date/status from frontmatter)
- `plugins/command-module/skills/brainstorm/SKILL.md` -- reference for option presentation patterns, handoff phase, platform-agnostic question tools
- `plugins/command-module/skills/capture/SKILL.md` -- sibling plugin skill for task creation: drafts task with description, status, priority, tags, notes; confirms with user; writes to `missioncontrol/tracking/{repo}/tasks/`
- `docs/prompts/strategy-toolkit-plan-concept-skill.md` -- exemplar prompt file: brief (~30 lines), self-contained, with title, action instruction, context bullets, file paths
- `plugins/command-module/AGENTS.md` -- skill compliance checklist, cross-platform reference rules, reference file inclusion rules

### Institutional Learnings

- Evidence before options: read and analyze all strategy artifacts before presenting recommendations. Never ask "what should we work on?" cold (from `docs/solutions/skill-design/compound-refresh-skill-improvements.md`)
- Verify `/capture` preconditions before delegating: assemble task title, description, and context before handoff (same source)
- Pass paths not content when delegating to other skills (from `docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md`)
- Model "no context found" as a first-class state, not an error (from `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`)
- Platform-agnostic question phrasing: capability-first tool language, not hardcoded tool names (from skill compliance checklist)

## Key Technical Decisions

- **Flat naming, no subdirectory:** Skill lives at `plugins/command-module/skills/whats-next/SKILL.md`, matching the convention established by `/concept` and `/strategy`. The requirements doc (R31) originally proposed `strategy/` as a category, but the implemented siblings use flat names.

- **Read-only relationship to strategy artifacts:** /whats-next reads `docs/strategy/context.md` and knowledge artifacts but never modifies them. Its outputs are prompt files (`docs/prompts/`) and task recommendations (delegated to `/capture`). This preserves the ownership model: /concept appends to context.md, /strategy curates it.

- **`/capture` as sibling plugin skill:** `/capture` is a plugin skill (`plugins/command-module/skills/capture/SKILL.md`) that handles task creation in `missioncontrol/tracking/{repo}/tasks/`. /whats-next loads it after user approval using semantic invocation ("load the `capture` skill"). Since `/capture` is part of the same plugin, it's always available. However, the missioncontrol tracking directory may not exist in all projects -- `/capture` handles that concern, not /whats-next.

- **Prompt file format follows existing convention:** The `docs/prompts/` files in this repo are brief, self-contained handoff briefs. /whats-next generates files following the same structure: title with action, what to do, key context with file paths, and relevant strategic reasoning. Not a new format.

- **No reference files needed initially:** The interaction pattern for /whats-next is simpler than /concept or /strategy (no reframe-react-sharpen cycle, no PM curation loop). The phases can be fully described in SKILL.md without extracting to reference files. If the prompt file template or analysis framework grows complex, a `references/` file can be added later.

- **Full portfolio scan like /strategy:** /whats-next needs the same complete view of `docs/strategy/` that /strategy has -- all artifacts with topic, date, status, and the full context.md. This supports making strategic recommendations about what to prioritize.

## Open Questions

### Resolved During Planning

- **Should /whats-next generate one prompt file per task or one consolidated file?** Resolution: One file per discrete execution conversation. Each prompt file should be self-contained so it can be used independently. A portfolio view might span 2-5 prompt files for different workstreams, each with its own strategic context and action.

- **What structure should prompt files follow?** Resolution: Follow the existing convention in `docs/prompts/`. Each file has: a title with action type, a one-line skill/action instruction, a "what to do" section, key context with file paths and strategic reasoning, and relevant references. Keep them brief and self-contained.

### Deferred to Implementation

- Exact naming convention for generated prompt files (likely `docs/prompts/YYYY-MM-DD-<topic>-<action>.md` but the implementer should check what fits naturally with existing files)
- Whether the "not recommended" items need their own section in the output or are woven into the recommendation narrative -- let the interaction pattern evolve

## Implementation Units

- [ ] **Unit 1: Create SKILL.md with core structure**

  **Goal:** Create the /whats-next skill with frontmatter, core principles, and the full execution flow.

  **Requirements:** R20, R21, R22, R23, R24, R25, R26

  **Dependencies:** None (reads outputs of /concept and /strategy but doesn't modify them)

  **Files:**
  - Create: `plugins/command-module/skills/whats-next/SKILL.md`

  **Approach:**

  Follow the structural conventions from `/concept` and `/strategy`:
  - YAML frontmatter with `name`, `description` (quoted, describes what + when), `argument-hint`
  - Core Principles section (4-5 numbered principles capturing the strategic judgment ethos)
  - Execution Flow with explicit phases and state machine diagram

  The execution flow has four phases:

  **Phase 0: Ground** -- Load `docs/strategy/context.md` and scan `docs/strategy/` for all knowledge artifacts (full portfolio scan, same as /strategy). Also check `docs/prompts/` for existing prompt files. Handle "no context found" as a first-class state: if no strategy artifacts exist, suggest running `/concept` or `/strategy` first rather than proceeding with empty analysis. If arguments were provided, use them to focus the analysis scope. Works standalone or as continuation of a /strategy session.

  **Phase 1: Analyze** -- The core value phase. Read all knowledge artifacts and context.md. Build a strategic picture across dimensions: what concepts are mature enough to act on, what's still forming, what tensions exist between concepts, what the current priorities and open questions suggest about sequencing. Produce an opinionated assessment: recommended actions (with strategic reasoning for each), recommended deferrals (what not to act on yet, with reasoning), and when multiple paths exist, present them with trade-offs in strategic terms (not effort/complexity). This is the "Translator" mode from the vision doc -- understanding concepts well enough to know what's essential vs. what's implementation detail.

  **Phase 2: Present and Approve** -- Present the task overview with explicit state machine for the approval cycle. Show recommended tasks grouped by priority/theme, each with strategic reasoning. Show "not now" items with reasoning. When options exist, present paths with trade-offs. Wait for user reaction -- they may approve all, approve selectively, push back, or request changes. Cycle until the user is satisfied with the plan. Use platform-agnostic question tools (AskUserQuestion in Claude Code, etc.) with fallback to numbered options.

  **Phase 3: Execute** -- Two parallel outputs after approval:
  1. Write prompt files to `docs/prompts/` -- one per approved execution conversation, following the existing format (title, action, context, file paths, strategic reasoning). Create `docs/prompts/` if it doesn't exist.
  2. Load the `capture` skill for each approved task that warrants a tracked task. Pass task description and relevant paths, not content.

  **Closing** -- Summary of what was produced: prompt files written (with paths), tasks captured (count + status), items deferred (brief list).

  **Patterns to follow:**
  - `/concept` SKILL.md for frontmatter format, phase structure, state machine diagrams, platform-agnostic question tools
  - `/strategy` SKILL.md for full portfolio scan in Phase 0, the evidence-first presentation pattern
  - `/brainstorm` SKILL.md for option presentation and handoff patterns
  - Existing `docs/prompts/` files for prompt file format

  **Test scenarios:**
  - Standalone invocation with existing strategy artifacts: should produce analysis + recommendations
  - Standalone invocation with no strategy artifacts: should suggest /concept or /strategy first
  - Invocation with arguments focusing on a specific topic: should scope analysis accordingly
  - Multiple viable paths: should present options with strategic trade-offs, not just list them
  - User partially approves: should generate prompt files only for approved items
  - Project without missioncontrol tracking: `/capture` handles that gracefully; /whats-next just loads it

  **Verification:**
  - SKILL.md passes frontmatter validation (`bun test tests/frontmatter.test.ts`)
  - Skill follows all compliance checklist items from `plugins/command-module/AGENTS.md` (quoted description, no markdown link refs, imperative form, platform-agnostic question tools)
  - Phase structure matches sibling skills (/concept, /strategy)
  - No implementation code or shell commands in the skill definition

- [ ] **Unit 2: Update /strategy to reference /whats-next**

  **Goal:** Replace the placeholder text in `/strategy`'s Phase 3, Option C with a real invocation of /whats-next.

  **Requirements:** R18 (from /strategy: "Can invoke /whats-next when thinking is done"), R26 (works as end-phase of /strategy)

  **Dependencies:** Unit 1

  **Files:**
  - Modify: `plugins/command-module/skills/strategy/SKILL.md`

  **Approach:**

  The current `/strategy` SKILL.md has this at line 123:
  > Option C: Hand off to execution. Note: the `/whats-next` skill is planned but not yet available. For now, summarize the strategic decisions...

  Replace with a real handoff that loads the `whats-next` skill, similar to how `/strategy` invokes `/concept` (line 92). Pass the current portfolio context so /whats-next doesn't need to re-scan.

  **Patterns to follow:**
  - `/strategy`'s existing `/concept` invocation pattern (line 92): "load the `concept` skill with the selected topic"

  **Test scenarios:**
  - /strategy's Option C loads /whats-next with appropriate context
  - The wording uses semantic "load the `whats-next` skill" phrasing per cross-platform reference rules

  **Verification:**
  - The placeholder text is fully removed
  - The new text follows the cross-skill invocation convention from AGENTS.md

- [ ] **Unit 3: Update plugin metadata**

  **Goal:** Update README.md skill counts and tables to include /whats-next.

  **Requirements:** Plugin maintenance rules from AGENTS.md

  **Dependencies:** Unit 1

  **Files:**
  - Modify: `plugins/command-module/README.md`

  **Approach:**

  Add /whats-next to the skills table in README.md under the appropriate category. Update the skill count. Run `bun run release:validate` to verify consistency.

  **Patterns to follow:**
  - Existing skill entries in README.md

  **Test scenarios:**
  - Skill count in README matches actual skill count
  - `bun run release:validate` passes

  **Verification:**
  - `bun run release:validate` succeeds
  - README.md accurately lists /whats-next with a one-line description

## System-Wide Impact

- **Interaction graph:** /whats-next reads from /concept's and /strategy's output artifacts (`docs/strategy/`). /strategy invokes /whats-next as an exit option. /whats-next loads `/capture` (sibling plugin skill) for task creation. No circular dependencies.
- **Error propagation:** If `docs/strategy/` is empty, /whats-next handles this as a first-class state (suggest /concept or /strategy first). `/capture` handles its own error cases (missing missioncontrol tracking, etc.).
- **State lifecycle risks:** None significant. /whats-next is read-only for strategy artifacts and write-only for prompt files. No shared mutable state.
- **API surface parity:** Not applicable -- this is a new skill, not modifying an existing interface.
- **Integration coverage:** The /strategy -> /whats-next handoff (Unit 2) is the primary integration seam to verify.

## Risks & Dependencies

- **Strategy artifact volume:** If a project has many knowledge artifacts, the full portfolio scan could consume significant context. Mitigated by the same approach /strategy uses -- scan frontmatter first, read full content selectively. If this becomes a problem in practice, a script-first architecture could be adopted later (per learnings).

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md](docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md) (R20-R26, R27-R30)
- **Research:** [docs/research/2026-04-06-strategic-team-vision.md](docs/research/2026-04-06-strategic-team-vision.md) (Translator mode, section 2.3)
- Related skills: `plugins/command-module/skills/concept/SKILL.md`, `plugins/command-module/skills/strategy/SKILL.md`
- Learnings: `docs/solutions/skill-design/compound-refresh-skill-improvements.md`, `docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md`, `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`
