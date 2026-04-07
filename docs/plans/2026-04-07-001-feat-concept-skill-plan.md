---
title: "feat(strategy): Add /concept skill for conceptual thinking partnerships"
type: feat
status: active
date: 2026-04-07
origin: docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md
---

# feat(strategy): Add /concept skill for conceptual thinking partnerships

## Overview

Add the first skill of the strategy toolkit: `/concept` -- a conceptual thinking partner that implements the reframe-react-sharpen interaction pattern. The skill produces knowledge artifacts and maintains a shared vocabulary through `docs/strategy/context.md`. This is the MVP that validates the core pattern before `/strategy` and `/whats-next` are built.

## Problem Frame

Strategic and conceptual work currently happens in regular conversations where the interaction rules have to be re-explained every time. The reframe-react-sharpen pattern is well-documented (27 analyzed conversations) but has no formal skill support. Conceptual vocabulary built across sessions gets lost unless manually maintained. (see origin: `docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md`)

## Requirements Trace

From R1-R14 and R27-R33 of the origin document:

- R1. Reframe-react-sharpen interaction pattern
- R2. Short, conversational responses -- no monologues
- R3. Take positions, not neutral option menus
- R4. Mark knowledge gaps explicitly
- R5. Connect ideas to existing concepts, flag tensions, use shared vocabulary
- R6. No build artifacts during thinking phase
- R7. Write knowledge artifact to `docs/strategy/` when thinking concludes
- R8. Offer to update `docs/strategy/context.md` after writing artifact
- R9. Load context.md at session start if it exists
- R10. Anti-pattern: no jumping to build mode
- R11. Anti-pattern: no long monologues
- R12. Anti-pattern: no parroting (papegaaien) -- reframe in different words
- R13. Anti-pattern: no filling gaps with assumptions
- R14. Anti-pattern: no five neutral options -- offer 2-3 with a preference
- R27. context.md is a living file: shared vocabulary, frameworks, decisions, open questions
- R28. Knowledge artifacts are dated: `YYYY-MM-DD-<topic>.md`
- R29. context.md is cross-session memory for strategic work, supplements Claude's memory system
- R30. Plugin provides skills/patterns; project-specific content lives in project repos
- R31. Skills live under a `strategy/` category
- R32. Follow existing command-module conventions
- R33. Agent references use fully-qualified namespace

## Scope Boundaries

- Only /concept -- not /strategy or /whats-next (those come after validation)
- No engineering execution, code, or build artifacts
- No multi-user collaboration patterns
- The content of any specific project's context.md is not defined here -- that emerges from use
- No custom agents or sub-agent dispatch -- this skill is a direct conversation between Claude and the user

## Context & Research

### Relevant Code and Patterns

- `plugins/command-module/skills/brainstorm/SKILL.md` -- closest analog: dialogue-based skill producing a durable artifact. Adopts: scope assessment, resume existing work, one-question-at-a-time rule, platform-agnostic interaction. Differentiates: brainstorm converges on requirements, /concept sharpens thinking through correction cycles
- `plugins/command-module/skills/ideate/SKILL.md` -- similar dialogue structure but focused on idea generation with filtering. /concept is more open-ended and doesn't filter down to a ranked list
- `plugins/command-module/skills/writing-foundations/SKILL.md` -- demonstrates the "knowledge base loaded by other skills" pattern with `references/`. /concept follows this pattern for its interaction principles
- `plugins/command-module/skills/distill/SKILL.md` -- demonstrates output artifact conventions with `assets/resolution-template.md` and frontmatter schema
- Skills directory uses **flat structure** -- all 39 skills directly under `skills/`, no subdirectories for categories

### Institutional Learnings

- **State machine design** (`docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`): Multi-cycle interaction patterns should model states and transitions explicitly, not as narrative prose. Define exit conditions as state transitions, not implicit fallthrough
- **Platform-agnostic interaction** (`docs/solutions/skill-design/compound-refresh-skill-improvements.md`): Never hardcode tool names. Use "the platform's blocking question tool" with named examples. "Triage before asking" -- ground every position in evidence
- **Script-first exception** (`docs/solutions/skill-design/script-first-skill-architecture.md`): Does not apply when the skill's core value is model judgment and unstructured natural language. /concept falls squarely in this exception
- **Pass paths not content** (`docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md`): When referencing artifacts, pass file paths. Relevant for context.md loading

### Research Foundation

- `docs/research/2026-04-06-conceptual-sparring-patterns.md` -- 27-conversation analysis identifying the reframe-react-sharpen pattern, Esther's thinking style (starts vague, sharpens via reaction), anti-patterns, and the asymmetric value of "almost right" reframes
- `docs/research/2026-04-06-strategic-team-vision.md` -- four-mode vision (Thinker, Writer, Translator, PM), shared knowledge layer design, design principles (P1-P6)

## Key Technical Decisions

- **Flat directory naming, not a strategy/ subdirectory**: R31 calls for a "strategy/ category" but existing convention is flat with 39 skills. Introducing the first subdirectory creates a structural precedent that affects the converter CLI and plugin discovery. Instead, name the skill `concept` (matching its invocation as `/concept`). When `/strategy` and `/whats-next` are added later, all three can be grouped conceptually via README documentation and skill descriptions without breaking directory conventions. If a category mechanism is later added to the plugin spec, these skills can be tagged then.

- **Interaction pattern as explicit states, not narrative prose**: The reframe-react-sharpen cycle is modeled as named states with transitions (grounding -> position -> reaction -> sharpening -> cycle-decision) rather than a flowing description. This follows the state-machine learning and makes the pattern reproducible across models.

- **Knowledge artifact structure defined inline in SKILL.md, not as a separate template**: The artifact format is simple enough (frontmatter + 5-6 sections) that a separate template file adds indirection without value. Brainstorm follows the same pattern -- its output format is defined inline. If the format grows complex, a `references/` or `assets/` file can be extracted later.

- **context.md structure defined in SKILL.md, not as a template**: The initial sections are prescribed, but the file is meant to evolve organically per project. Prescribing a rigid template would fight against the "living document" intent (R27). The skill defines what sections to start with and how to update them.

- **No sub-agents**: The skill's core value is direct conversational interaction. Dispatching to research or writing agents would break the flow. The skill reads context.md itself and writes artifacts directly.

- **Interaction principles as a reference file**: The research doc (`conceptual-sparring-patterns.md`) distills into a compact set of interaction principles (~100-150 lines) that the skill loads on demand via backtick path. This keeps the SKILL.md focused on structure/flow while the reference file captures the nuance of "how to be a good thinking partner."

## Open Questions

### Resolved During Planning

- **Q: Should the skill use a `strategy/` subdirectory?** No -- flat naming follows existing convention and avoids structural precedent. The category relationship is documented in README and descriptions. (see Key Technical Decisions)

- **Q: What structure should knowledge artifacts follow?** A dated markdown file with frontmatter (date, topic, status, related-concepts) and sections for: the concept itself, the reasoning/evolution, what was considered and rejected, open questions, and connections to existing concepts. Format defined inline in SKILL.md. (addresses origin deferred question on R7, R8)

- **Q: What structure should context.md follow?** Four sections: Vocabulary (shared terms and definitions), Active Frameworks (current conceptual models in use), Key Decisions (resolved strategic choices with rationale), and Open Questions (unresolved tensions and explorations). The skill creates this structure on first write and appends/updates on subsequent sessions. (addresses origin deferred question on R27)

- **Q: How does the cycle end?** Three exit paths: (1) user signals satisfaction ("this is clear enough"), (2) user requests artifact writing ("let's capture this"), (3) the concept has stabilized and Claude suggests writing it down. All three transition to the artifact-writing phase.

### Deferred to Implementation

- **Q: How long should the interaction principles reference file be?** The research doc is 400+ lines. The distilled principles need to be long enough to capture nuance but short enough to be useful as context. Target ~100-150 lines; adjust based on what fits naturally.

- **Q: Should the skill detect language (Dutch/English) from user input?** Esther works in both. The research doc is in Dutch. The skill should probably match the user's language naturally, but whether this needs explicit instruction or happens implicitly is an implementation-time discovery.

## Implementation Units

- [ ] **Unit 1: Create interaction principles reference file**

  **Goal:** Distill the research findings into a compact reference that the SKILL.md can load on demand, capturing how to be a good conceptual thinking partner.

  **Requirements:** R1, R2, R3, R4, R5, R10-R14

  **Dependencies:** None

  **Files:**
  - Create: `plugins/command-module/skills/concept/references/interaction-principles.md`

  **Approach:**
  - Distill `docs/research/2026-04-06-conceptual-sparring-patterns.md` into actionable principles
  - Organize around: the core reframe-react-sharpen cycle, effective thinking moves (structuring, connecting, challenging), anti-patterns with concrete examples, Esther's thinking style characteristics
  - Include the concrete examples from the research (the "Gratis-paradox" correction, "bezettingsstroming" emergence) as illustrations of what the pattern looks like in practice
  - Keep the tone instructional but grounded -- these are real patterns from real conversations, not abstract ideals

  **Patterns to follow:**
  - `plugins/command-module/skills/writing-foundations/references/writing-principles.md` -- a reference file that captures domain knowledge for a skill to load on demand
  - `plugins/command-module/skills/proof/references/writing-style-en.md` -- another reference loaded via backtick path

  **Test scenarios:**
  - The file is self-contained: an implementer reading only this file understands how the interaction pattern works
  - The anti-patterns are specific enough to be actionable, not generic platitudes
  - The file is under ~150 lines (ideally) to keep context load reasonable

  **Verification:**
  - The reference file covers all anti-patterns from R10-R14
  - Examples from the research are preserved as concrete illustrations
  - The file can be referenced from SKILL.md via backtick path: `` `references/interaction-principles.md` ``

- [ ] **Unit 2: Create SKILL.md with interaction pattern and output conventions**

  **Goal:** Define the complete skill: frontmatter, interaction states, context.md loading, knowledge artifact writing, and context.md updating.

  **Requirements:** R1-R14, R27-R30, R32-R33

  **Dependencies:** Unit 1 (reference file exists to be referenced)

  **Files:**
  - Create: `plugins/command-module/skills/concept/SKILL.md`

  **Approach:**

  The SKILL.md has four phases modeled as states:

  **Phase 0: Ground** -- Load context.md if it exists (R9). Assess whether there's existing work to resume (check `docs/strategy/` for related artifacts). Establish the topic from user input or arguments.

  **Phase 1: Think (the reframe-react-sharpen cycle)** -- The core loop. Claude reads the user's input, reframes it in different words (ideally a step further than stated), and waits for reaction. Each cycle sharpens the concept. This phase references `` `references/interaction-principles.md` `` for the interaction pattern details.

  State transitions within Phase 1:
  - `grounding` -> Claude takes an initial position on the user's topic
  - `position-taken` -> waiting for user reaction
  - `reaction-received` -> Claude sharpens based on the reaction (confirm+build or correct)
  - `cycle-decision` -> continue the cycle or transition to Phase 2

  Exit conditions: user signals satisfaction, user requests capture, or concept has stabilized and Claude suggests capturing.

  **Phase 2: Capture** -- Write a knowledge artifact to `docs/strategy/YYYY-MM-DD-<topic>.md`. The artifact structure:
  - Frontmatter: `date`, `topic`, `status` (active/superseded), `related-concepts` (list)
  - Sections: Concept (the sharpened idea), Reasoning (how we got here, the evolution through cycles), Alternatives Considered (what was explored and rejected), Open Questions (what remains unresolved), Connections (how this relates to existing concepts and vocabulary)

  **Phase 3: Update** -- Offer to update `docs/strategy/context.md` (R8). If context.md doesn't exist yet, create it with initial structure:
  - **Vocabulary** -- shared terms and their definitions
  - **Active Frameworks** -- conceptual models currently in use
  - **Key Decisions** -- resolved strategic choices with brief rationale
  - **Open Questions** -- unresolved tensions, explorations, things to revisit

  If it exists, propose specific additions/changes based on the session.

  **Skill compliance:**
  - Frontmatter: `name: concept`, `description:` with trigger phrases, optional `argument-hint`
  - Platform-agnostic interaction: use blocking question tool with named examples
  - Backtick path for reference file
  - No shell commands for file discovery
  - Imperative/infinitive writing style

  **Patterns to follow:**
  - `plugins/command-module/skills/brainstorm/SKILL.md` -- phase structure, resume logic, scope assessment, output writing conventions
  - `plugins/command-module/skills/distill/SKILL.md` -- artifact output with frontmatter and structured sections
  - State machine pattern from `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`

  **Test scenarios:**
  - A user starts `/concept` with a vague idea -- the skill loads context.md (if present), takes an initial position, and enters the reframe cycle
  - A user starts `/concept` in a repo with no `docs/strategy/` -- the skill works fine, creates the directory when writing the first artifact
  - Mid-conversation, the user says "actually let's write this down" -- the skill transitions cleanly to artifact writing
  - The cycle runs 3+ times with corrections -- each reframe builds on the previous correction, not on stale earlier framing
  - A user tries to ask Claude to build something during the thinking phase -- the skill redirects to finishing the concept first (R10)
  - The artifact includes what was rejected, not just the final concept

  **Verification:**
  - SKILL.md passes the skill compliance checklist from AGENTS.md
  - The interaction pattern is modeled as explicit states, not just narrative description
  - All anti-patterns from R10-R14 are addressed
  - context.md loading (R9) and updating (R8) are both covered
  - Knowledge artifact format is defined with frontmatter and all required sections
  - The skill description includes trigger phrases for model invocation

- [ ] **Unit 3: Update README.md with new skill**

  **Goal:** Add /concept to the plugin's skill inventory so it's discoverable and the counts stay accurate.

  **Requirements:** R32

  **Dependencies:** Unit 2

  **Files:**
  - Modify: `plugins/command-module/README.md`

  **Approach:**
  - Add concept to the appropriate skill category table
  - Update skill count in description
  - Group it conceptually with a "Strategy" label or section if the README already has category groupings

  **Patterns to follow:**
  - Existing README table entries for other skills

  **Test scenarios:**
  - The skill appears in the README with accurate name and description
  - Skill count matches actual directory count

  **Verification:**
  - `bun run release:validate` passes
  - README count matches `ls plugins/command-module/skills/ | wc -l`

## System-Wide Impact

- **New output directory convention:** `docs/strategy/` will be created in project repos by this skill. Other skills don't currently write there. No conflicts expected.
- **context.md as cross-session state:** This introduces a new pattern where a skill reads and writes a living document across sessions. Similar to how memory works but file-based and project-scoped. No interaction with Claude's memory system beyond supplementing it (R29).
- **No API surface changes:** This is a new skill, not a modification. No existing behavior changes.
- **Converter/CLI impact:** New skill directory will be picked up by the converter automatically. Flat naming ensures no special handling needed.

## Risks & Dependencies

- **Risk: Interaction pattern may be too prescriptive or too loose.** The state machine model is a best guess at formalizing a naturally flowing conversation pattern. If it feels mechanical in practice, the states may need to be softened into guidelines. Mitigation: the states are described as a mental model for the skill, not rigid transitions that must be followed mechanically.
- **Risk: context.md could grow unwieldy.** No size management is specified. Mitigation: defer to /strategy (the PM skill) to handle context.md curation. For now, the skill only appends; pruning is a future concern.
- **Dependency: /concept must prove the pattern works before /strategy and /whats-next are built.** This is by design (see origin Key Decisions). If the reframe-react-sharpen cycle doesn't work well as a formalized skill, the other two skills need rethinking.

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md](docs/brainstorms/2026-04-06-strategy-toolkit-requirements.md)
- **Research:** [docs/research/2026-04-06-conceptual-sparring-patterns.md](docs/research/2026-04-06-conceptual-sparring-patterns.md) -- 27-conversation pattern analysis
- **Research:** [docs/research/2026-04-06-strategic-team-vision.md](docs/research/2026-04-06-strategic-team-vision.md) -- four-mode vision and design principles
- **Learnings:** `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`
- **Learnings:** `docs/solutions/skill-design/compound-refresh-skill-improvements.md`
- **Pattern reference:** `plugins/command-module/skills/brainstorm/SKILL.md`
- **Pattern reference:** `plugins/command-module/skills/distill/SKILL.md`
