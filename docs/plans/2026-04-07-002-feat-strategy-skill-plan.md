---
title: "feat(strategy): Add /strategy skill for strategic PM thinking partnerships"
type: feat
status: completed
date: 2026-04-07
origin: docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md
---

# feat(strategy): Add /strategy skill for strategic PM thinking partnerships

## Overview

Add the second skill of the strategy toolkit: `/strategy` -- the project manager of strategic thinking. It loads `docs/strategy/context.md`, reviews the portfolio of knowledge artifacts in `docs/strategy/`, identifies tensions and gaps across concepts, and suggests what to think about next. It can invoke `/concept` for deep thinking on a specific idea and return to PM mode afterward. This skill curates the shared knowledge layer that `/concept` produces.

## Problem Frame

After `/concept` produces knowledge artifacts and shared vocabulary, there is no skill that maintains the big picture. Individual concept sessions produce sharp insights, but nobody reviews the portfolio for tensions, contradictions, or gaps. `context.md` accumulates entries from `/concept` sessions but is never pruned or reorganized. The strategic thinker has to manually track what open questions remain, which decisions might conflict, and what to think about next. (see origin: `docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md`)

The vision document (Modus 4: PM/orchestrator) describes this as "continuous awareness" -- not a mode you turn on and off, but the voice that says "wait, this contradicts what we decided about X" during a brainstorm. `/strategy` formalizes that into an invokable skill.

## Requirements Trace

From R15-R19 and R27-R33 of the origin document:

- R15. Load context.md and establish PM interaction rules: think together, never build, maintain big picture, produce prompts/briefs for execution conversations
- R16. Project-level strategic awareness: knows what concepts exist, what open questions remain, where tensions sit between existing decisions
- R17. Can invoke /concept when a specific idea needs deep thinking, and returns to PM mode afterward with context intact
- R18. Can invoke /whats-next when thinking is done and it's time to figure out execution
- R19. Maintains coherence: flags contradictions with earlier decisions, scope creep, threads that need reconciliation
- R27. context.md is a living file: shared vocabulary, frameworks, decisions, open questions
- R28. Knowledge artifacts are dated: `YYYY-MM-DD-<topic>.md`
- R29. context.md is cross-session memory for strategic work
- R30. Plugin provides skills/patterns; project-specific content lives in project repos
- R31. Skills live under a strategy/ category (implemented as flat naming per /concept precedent)
- R32. Follow existing command-module conventions
- R33. Agent references use fully-qualified namespace

## Scope Boundaries

- Only /strategy -- not /whats-next (that comes next)
- R18 (/whats-next invocation) is included as a **handoff point** only -- the /whats-next skill itself is not designed here
- No engineering execution, code, or build artifacts
- No multi-user collaboration
- /strategy does not define new context.md structure -- it uses the structure /concept already established
- /strategy does not replace Claude's memory system -- it supplements it (R29)

## Context & Research

### Relevant Code and Patterns

- `plugins/command-module/skills/concept/SKILL.md` -- direct sibling skill. /strategy reads the same `docs/strategy/` directory and `context.md` that /concept writes. Adopts: phase structure, state machine modeling, platform-agnostic interaction, context.md section structure. Differentiates: /concept appends to context.md, /strategy curates it; /concept does deep thinking, /strategy maintains the big picture
- `plugins/command-module/skills/brainstorm/SKILL.md` -- best example of cross-skill invocation (Pattern C: "load the `document-review` skill... when it returns, return to Phase 4 options"). Directly transferable to /strategy invoking /concept
- `plugins/command-module/skills/distill-refresh/SKILL.md` -- closest analog for portfolio management. Five-outcome classification (Keep/Update/Consolidate/Replace/Delete) is transferable to how /strategy should assess knowledge artifacts
- `plugins/command-module/skills/ideate/SKILL.md` -- agent dispatch pattern and directory scanning for existing artifacts within a time window

### Institutional Learnings

- **State machine design** (`docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`): Model the PM flow as explicit states with precondition checks at each transition. After /concept returns, re-read context.md before updating -- don't assume pre-/concept state still holds
- **Compound-refresh improvements** (`docs/solutions/skill-design/compound-refresh-skill-improvements.md`): Triage before asking -- scan the portfolio and identify tensions/gaps before presenting to the user. Don't ask "what should we focus on?" without evidence. Also: when handing off to another skill, verify the topic is well-formed for that skill's input expectations
- **Pass paths not content** (`docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md`): When invoking /concept about a tension between artifacts, pass artifact paths and let /concept read them
- **Script-first architecture** (`docs/solutions/skill-design/script-first-skill-architecture.md`): If portfolio grows large (>20 artifacts), a metadata extraction script saves tokens. Defer this -- premature for early use
- **Orchestration contract** (`docs/solutions/skill-design/beta-promotion-orchestration-contract.md`): When invoking /concept, hardcode the mode/arguments at the callsite. Don't rely on defaults

### Research Foundation

- `docs/research/2026-04-06-conceptual-sparring-patterns.md` -- 27-conversation analysis. Relevant for /strategy: the PM mode described in the patterns (active cross-concept awareness, tension flagging)
- `docs/research/2026-04-06-strategic-team-vision.md` -- Modus 4 (PM) is the direct source. "Not checking after the fact, but active monitoring *during* thinking"

## Key Technical Decisions

- **context.md ownership: /strategy curates, /concept appends.** Both skills read `docs/strategy/context.md`. /concept writes new entries (vocabulary, decisions, questions) at session end. /strategy is the curator -- it reorganizes, prunes stale entries, resolves contradictions, and maintains coherence. This avoids the compound-refresh pitfall of contradictory rules when multiple skills write to the same file. /concept's writes are additive; /strategy's writes are editorial.

- **Flat directory naming (strategy, not strategy-pm).** Follows the /concept precedent. The skill is invoked as `/strategy` and lives at `skills/strategy/SKILL.md`. The three strategy toolkit skills are grouped conceptually via README documentation, not directory hierarchy.

- **PM interaction pattern as a reference file, not inline.** The PM interaction principles (maintain big picture, never build, think together, take positions on what to think about next) are substantial enough to warrant a `references/pm-interaction-principles.md` file, following the same pattern as /concept's `references/interaction-principles.md`. This keeps SKILL.md focused on flow and structure.

- **Portfolio review uses model judgment, not a script.** The portfolio will be small in early use (<10 artifacts). The value of /strategy is in identifying *tensions and connections*, which requires reading artifacts with understanding, not mechanical metadata extraction. A script-first approach is deferred until the portfolio grows beyond ~20 artifacts. The skill scans using native file-search tools, not shell commands.

- **/concept invocation uses Pattern C (load-and-return).** Following the brainstorm -> document-review pattern: "Load the `concept` skill with the selected topic. When concept returns (artifact captured or session ended), return to PM mode and refresh the portfolio view." This is a natural language handoff, not a programmatic callback.

- **/whats-next invocation is a terminal handoff (Pattern A).** When the user is done with strategic thinking and wants to move to execution, /strategy hands off to /whats-next with a sequential chain. There is no return to /strategy after /whats-next -- the session transitions to execution mode. Since /whats-next doesn't exist yet, this is documented as a future handoff point.

- **No sub-agent dispatch for portfolio analysis.** The skill's core value is the PM's own synthesis across concepts. Dispatching agents for analysis would fragment the holistic view that makes the PM mode valuable. The model reads the artifacts directly and builds the portfolio view itself.

## Open Questions

### Resolved During Planning

- **Q: How does /strategy invoke /concept and preserve context?** Pattern C from brainstorm: load the concept skill with a topic argument, then describe the return behavior in natural language. When concept completes, /strategy re-reads context.md and the portfolio to refresh its state. (addresses origin deferred question on R15, R17)

- **Q: Who owns context.md updates?** /strategy is the curator. /concept appends new entries at session end. /strategy reorganizes, prunes, and maintains coherence. When /strategy invokes /concept and /concept writes to context.md, /strategy re-reads after return. (see Key Technical Decisions)

- **Q: How does /strategy assess the portfolio?** Read all `docs/strategy/*.md` files (excluding context.md itself). For each artifact, note: topic, date, status, related-concepts, open questions, and connections. Build a mental model of the portfolio's themes, tensions, and gaps. Present findings with evidence before asking the user what to focus on. (informed by compound-refresh learning: triage before asking)

- **Q: Should /strategy support autonomous mode?** Not in v1. The PM interaction is inherently collaborative -- "think together" (R15). An autonomous report mode (scan portfolio, write findings to a file) is a natural extension but adds scope. Defer to a future iteration.

### Deferred to Implementation

- **Q: How much of context.md should /strategy read at load time?** For large context.md files, reading the full file may consume significant tokens. The answer depends on how large context.md actually grows in practice. Start by reading the full file; add selective reading if it becomes a problem.

- **Q: What's the right level of portfolio summary detail?** /strategy needs to present a portfolio overview that's useful without being overwhelming. The right balance between "here are 12 artifacts with full summaries" and "here are 3 themes worth attention" is an implementation-time discovery.

- **Q: Should /strategy detect language from context.md?** Like /concept, it should probably match the user's language naturally. Whether this needs explicit instruction is an implementation-time discovery.

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

```
Phase 0: Ground
  |
  v
Phase 1: Review Portfolio
  |-- scan docs/strategy/*.md artifacts
  |-- read docs/strategy/context.md
  |-- identify themes, tensions, gaps, stale entries
  |
  v
Phase 2: PM Conversation (the main loop)
  |
  |-- present findings -> user reacts -> refine focus
  |       |
  |       v
  |-- BRANCH: invoke /concept (Pattern C)
  |       |-- frame tension/gap as thinking prompt
  |       |-- load concept skill with topic
  |       |-- on return: re-read portfolio, refresh state
  |       |-- resume PM conversation
  |       v
  |-- BRANCH: curate context.md
  |       |-- propose reorganization, pruning, or updates
  |       |-- user approves or adjusts
  |       |-- write changes
  |       v
  |-- BRANCH: user explores a thread
  |       |-- PM takes position on direction
  |       |-- reframe-and-react (lighter than /concept, focused on big picture)
  |       |-- feed insight back into portfolio view
  |       v
  |-- cycle-decision: continue PM conversation or transition
  |
  v
Phase 3: Transition
  |-- OPTION A: hand off to /whats-next (Pattern A, terminal)
  |-- OPTION B: session end with portfolio summary
  |-- OPTION C: invoke /concept for one more deep dive (loop to Phase 2)
```

## Implementation Units

- [x] **Unit 1: Create PM interaction principles reference file**

  **Goal:** Distill the PM mode principles from the research and requirements into a compact reference that SKILL.md loads on demand -- capturing how to be an effective strategic PM thinking partner.

  **Requirements:** R15, R16, R19

  **Dependencies:** None

  **Files:**
  - Create: `plugins/command-module/skills/strategy/references/pm-interaction-principles.md`

  **Approach:**
  - Draw from Modus 4 (PM) in `docs/research/2026-04-06-strategic-team-vision.md` and R15-R19 in the origin doc
  - Organize around: the PM mindset (big picture, never build, think together), portfolio awareness techniques (scanning for tensions, tracking open questions, flagging contradictions), context.md curation principles (when to add, when to prune, how to reorganize), and the transition from PM thinking to execution readiness
  - Include concrete examples of PM-mode thinking: "wait, this contradicts what we decided about X", "there's a gap between concept A and concept B that nobody has addressed", "these three open questions are really the same question"
  - Define anti-patterns specific to PM mode: don't dive into implementation details, don't resolve tensions by picking sides without the user, don't present the portfolio as a neutral inventory without analysis

  **Patterns to follow:**
  - `plugins/command-module/skills/concept/references/interaction-principles.md` -- same structure: distilled principles from research, organized by category, with concrete examples

  **Test scenarios:**
  - The file is self-contained: an implementer reading only this file understands how PM-mode interaction works
  - The principles are distinct from /concept's interaction principles -- PM mode is about the big picture, not the reframe-react-sharpen cycle
  - The file is under ~150 lines

  **Verification:**
  - Covers the PM behaviors from R15, R16, and R19
  - Anti-patterns are specific and actionable
  - Referenceable from SKILL.md via `` `references/pm-interaction-principles.md` ``

- [x] **Unit 2: Create SKILL.md with portfolio review, PM conversation, and cross-skill invocation**

  **Goal:** Define the complete skill: frontmatter, portfolio scanning, PM conversation loop, /concept invocation, context.md curation, and session transitions.

  **Requirements:** R15-R19, R27-R30, R32-R33

  **Dependencies:** Unit 1 (reference file exists to be referenced)

  **Files:**
  - Create: `plugins/command-module/skills/strategy/SKILL.md`

  **Approach:**

  The SKILL.md has four phases:

  **Phase 0: Ground** -- Load `docs/strategy/context.md` if it exists. Scan `docs/strategy/` for all knowledge artifacts. Establish PM interaction rules. If no artifacts or context.md exist, note this is a fresh strategic landscape and offer to start a /concept session or begin building the big picture from scratch.

  **Phase 1: Review Portfolio** -- This is where /strategy differentiates from /concept. Read all artifacts in `docs/strategy/` (excluding context.md). Build a portfolio view:
  - Themes: what topics have been explored, how they cluster
  - Tensions: where do concepts pull in different directions, or where do decisions conflict
  - Gaps: what open questions span multiple artifacts, what adjacent areas haven't been explored
  - Staleness: which artifacts or context.md entries are outdated given more recent thinking
  - Coherence: does context.md accurately reflect the current state of the portfolio

  Present findings with evidence (specific artifact references, specific tensions). Take a position on what deserves attention. Let the user confirm or redirect.

  **Phase 2: PM Conversation (the main loop)** -- The PM thinking cycle. Modeled as states:

  ```
  findings-presented -> user-direction -> focus-selected -> pm-thinking -> action-decision
       ^                                                                        |
       |_________________________ continue _____________________________________|
                                     |
                              transition (-> Phase 3)
  ```

  - `findings-presented`: present portfolio review or updated findings after a /concept return
  - `user-direction`: wait for user to confirm focus or redirect
  - `focus-selected`: the PM and user are aligned on what to think about
  - `pm-thinking`: discuss the topic from a big-picture perspective. This is lighter than /concept's reframe cycle -- focused on connections, implications, and priorities rather than sharpening a single concept
  - `action-decision`: evaluate what to do next:
    - **Invoke /concept** if a specific idea needs deep thinking. Frame the tension/gap as a thinking prompt suitable for /concept's input. Use Pattern C: "Load the `concept` skill with [topic]. When concept returns, return to Phase 2 and refresh the portfolio view."
    - **Curate context.md** if the conversation has produced insights that should update shared vocabulary, resolve open questions, or reorganize the framework
    - **Continue PM conversation** if there are more threads to explore
    - **Transition to Phase 3** when the user signals they're done or ready for execution

  **Guardrails during Phase 2:**
  - If the user asks to build something, redirect: "That's execution work. Want to capture what we've decided and hand off to /whats-next, or is there more to think through first?"
  - If a single topic is absorbing too much depth, suggest: "This feels like it needs its own /concept session. Want to dive in?"
  - After returning from /concept, always re-read context.md and re-scan for the new artifact before continuing

  **Phase 3: Transition** -- Three exit paths:
  1. Hand off to /whats-next (Pattern A, terminal): "Load the `/whats-next` skill. The strategic context is at `docs/strategy/context.md` and artifacts are in `docs/strategy/`." (Note: /whats-next is not yet built; present this option only when it exists)
  2. Session summary: summarize what was reviewed, what tensions were identified, what was curated, what open questions remain
  3. One more /concept dive: loop back to Phase 2 via /concept invocation

  **context.md curation within the PM conversation:**
  When the conversation reveals that context.md needs changes, propose specific updates:
  - Add new vocabulary or framework entries
  - Mark decisions as resolved (move from Open Questions to Key Decisions)
  - Flag entries that are contradicted by more recent artifacts
  - Propose reorganization when sections have grown unwieldy
  - Prune entries that are superseded or no longer relevant
  Present proposed changes and wait for user approval before writing.

  **Skill compliance:**
  - Frontmatter: `name: strategy`, `description:` with trigger phrases, optional `argument-hint`
  - Platform-agnostic interaction: use blocking question tool with named examples
  - Backtick path for reference file
  - No shell commands for file discovery -- use native file-search/glob tools
  - Imperative/infinitive writing style

  **Patterns to follow:**
  - `plugins/command-module/skills/concept/SKILL.md` -- phase structure, context.md loading, artifact writing conventions
  - `plugins/command-module/skills/brainstorm/SKILL.md` -- cross-skill invocation Pattern C (load skill, describe return behavior)
  - `plugins/command-module/skills/distill-refresh/SKILL.md` -- portfolio assessment model
  - State machine pattern from `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`

  **Test scenarios:**
  - A user starts `/strategy` in a repo with 3+ knowledge artifacts and a populated context.md -- the skill presents a portfolio view with tensions/gaps identified
  - A user starts `/strategy` in a repo with no `docs/strategy/` -- the skill explains this is a fresh strategic landscape and offers to start a /concept session
  - During the PM conversation, the user says "let's think through X more deeply" -- the skill invokes /concept with a well-framed topic
  - After returning from /concept, the skill re-reads context.md and the new artifact, then updates its portfolio view
  - The user asks to "just update the context file" -- the skill proposes specific changes to context.md with evidence from the conversation
  - The user asks to build something -- the skill redirects to finishing strategic thinking first or handing off
  - context.md has a stale entry that contradicts a recent artifact -- the skill flags it and proposes a resolution

  **Verification:**
  - SKILL.md passes the skill compliance checklist from AGENTS.md
  - The PM conversation is modeled as explicit states, not narrative description
  - /concept invocation uses Pattern C with explicit return behavior
  - /whats-next handoff is documented as a future handoff point (Pattern A)
  - context.md curation is a distinct capability, not just "offer to update" like /concept does
  - All PM behaviors from R15-R19 are addressed

- [x] **Unit 3: Update README.md with new skill**

  **Goal:** Add /strategy to the plugin's skill inventory so it's discoverable and counts stay accurate.

  **Requirements:** R32

  **Dependencies:** Unit 2

  **Files:**
  - Modify: `plugins/command-module/README.md`

  **Approach:**
  - Add strategy to the same category grouping as concept (both are strategy toolkit skills)
  - Update skill count in description
  - Brief description that captures the PM role: "Strategic PM for portfolio review, tension analysis, and thinking direction"

  **Patterns to follow:**
  - Existing README table entries, especially the concept skill entry

  **Test scenarios:**
  - The skill appears in the README with accurate name and description
  - Skill count matches actual directory count
  - Both concept and strategy are visually grouped as strategy toolkit skills

  **Verification:**
  - `bun run release:validate` passes
  - README count matches `ls plugins/command-module/skills/ | wc -l`

## System-Wide Impact

- **context.md ownership model:** This introduces a curator/appender split. /concept appends new entries; /strategy reorganizes, prunes, and maintains coherence. No technical enforcement -- the ownership model is documented in both skills' SKILL.md files. Risk: if /concept is used without /strategy, context.md may grow uncurated. Mitigation: this is acceptable -- /concept works standalone, and curation is a bonus that /strategy provides.
- **Cross-skill invocation:** /strategy is the second skill to use Pattern C (load-and-return). The first is brainstorm -> document-review. If Pattern C proves fragile in practice, both skills are affected.
- **Portfolio scanning convention:** /strategy establishes that `docs/strategy/` is not just an output directory but a portfolio that gets reviewed across sessions. No other skill currently treats a `docs/` subdirectory this way (distill-refresh reviews `docs/solutions/` but for maintenance, not strategic synthesis).
- **No API surface changes:** New skill, no modifications to existing behavior.
- **Converter/CLI impact:** New skill directory picked up automatically. Flat naming ensures no special handling.

## Risks & Dependencies

- **Risk: Portfolio scanning could be token-expensive.** Reading all artifacts in `docs/strategy/` to build a portfolio view could consume significant context for projects with many artifacts. Mitigation: start with full reads; if portfolio grows beyond ~20 artifacts, extract metadata first and read full content selectively. The script-first architecture learning provides the upgrade path.
- **Risk: Pattern C (load-and-return) may not preserve PM context well.** When /strategy invokes /concept and concept runs its full cycle, the PM's portfolio view and conversation state could be stale or lost by the time concept returns. Mitigation: /strategy explicitly re-reads context.md and re-scans the portfolio after every /concept return, rebuilding its state from files rather than relying on in-memory continuity.
- **Risk: PM mode may feel too passive.** If /strategy just presents findings and waits, it becomes a portfolio dashboard, not a thinking partner. Mitigation: the PM interaction principles reference file must emphasize taking positions, suggesting connections, and actively steering -- not just summarizing.
- **Dependency: /concept must be working.** /strategy's /concept invocation (R17) depends on /concept being live and functional. This is satisfied -- /concept is already implemented.
- **Dependency: /whats-next does not exist yet.** The R18 handoff point is documented but non-functional until /whats-next is built. The skill should check for /whats-next's existence before offering the handoff option.

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md](docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md)
- **Research:** [docs/research/2026-04-06-conceptual-sparring-patterns.md](docs/research/2026-04-06-conceptual-sparring-patterns.md) -- 27-conversation pattern analysis
- **Research:** [docs/research/2026-04-06-strategic-team-vision.md](docs/research/2026-04-06-strategic-team-vision.md) -- Modus 4 (PM) vision and design principles
- **Sibling skill:** [plugins/command-module/skills/concept/SKILL.md](plugins/command-module/skills/concept/SKILL.md) -- direct pattern reference and invocation target
- **Pattern reference:** [plugins/command-module/skills/brainstorm/SKILL.md](plugins/command-module/skills/brainstorm/SKILL.md) -- cross-skill invocation Pattern C
- **Pattern reference:** [plugins/command-module/skills/distill-refresh/SKILL.md](plugins/command-module/skills/distill-refresh/SKILL.md) -- portfolio management model
- **Learnings:** `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`
- **Learnings:** `docs/solutions/skill-design/compound-refresh-skill-improvements.md`
- **Learnings:** `docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md`
- **Learnings:** `docs/solutions/skill-design/beta-promotion-orchestration-contract.md`
