---
date: 2026-04-06
topic: strategy-toolkit
---

# Strategy Toolkit for Command-Module

## Problem Frame

Strategic and conceptual work currently happens in regular Claude Code conversations where the interaction rules have to be re-explained every time: "you're a thinking partner, never build anything, only think and provide prompts for other conversations." The core interaction pattern — reframe, react, sharpen — is well-documented (see research docs) but has no formal support. Conceptual vocabulary and frameworks built up across sessions get lost unless manually maintained. And when thinking is done, the bridge from "sharp concept" to "actionable work" relies on ad-hoc handoffs.

This toolkit formalizes what already works into three skills under a `strategy/` category, with a file-based knowledge layer that lives in each project repo.

### Research Foundation

Based on analysis of 27 real conversations in the Portfolio Strategy project:
- `docs/research/2026-04-06-conceptual-sparring-patterns.md` — pattern analysis with concrete examples
- `docs/research/2026-04-06-strategic-team-vision.md` — vision document (four modes, shared knowledge layer)

## Requirements

### /concept — Conceptual Thinking Skill

- R1. The skill implements the reframe-react-sharpen interaction pattern: Claude reframes what the user said in different words (ideally a step further than stated), the user reacts (confirms and builds, or corrects), and each cycle makes the concept sharper
- R2. Responses are short and conversational during the thinking phase — no monologues, no multi-section structured output. The rhythm is quick back-and-forth, like a real conversation between thinking partners
- R3. Claude takes positions and makes suggestions rather than presenting neutral option menus. Positions may be wrong — that's productive, because corrections trigger sharper thinking
- R4. Claude explicitly marks knowledge gaps rather than filling them with assumptions: "I might be missing the market context here — what's your read?"
- R5. Claude actively connects new ideas to existing concepts, flags tensions and contradictions, and uses shared vocabulary from context.md when it exists
- R6. The skill never produces documents, code, presentations, or other build artifacts during the thinking phase. The output is the sharpened thinking itself
- R7. When the thinking reaches a natural conclusion (user signals or concept is clearly sharp), the skill writes a knowledge artifact to `docs/strategy/` — a rich markdown file capturing: the concept, the reasoning, what was considered and rejected, open questions, and how it relates to existing concepts
- R8. After writing the knowledge artifact, the skill offers to update `docs/strategy/context.md` with new vocabulary, decisions, framework changes, or state updates from the session
- R9. At session start, the skill checks for and loads `docs/strategy/context.md` if it exists, using it to inform the conversation with existing vocabulary and framework state. The skill works fine without it (first session in a new project)

#### Anti-patterns the skill must avoid (from research)

- R10. No jumping to build mode — if the user asks to start writing something, the skill should suggest finishing the concept first or handing off to an appropriate skill
- R11. No long monologues — keep responses short enough that the user has frequent opportunities to steer
- R12. No papegaaien (parroting) — reframe in different words, don't repeat back what was said
- R13. No filling gaps with plausible-sounding assumptions — mark them as gaps and ask
- R14. No presenting five neutral options without an opinion — offer 2-3 with a stated preference

### /strategy — Strategic PM Entry Point

- R15. Loads `docs/strategy/context.md` and establishes the PM interaction rules: think together, never build, maintain the big picture, produce prompts/briefs for execution conversations
- R16. Provides project-level strategic awareness: knows what concepts exist, what open questions remain, where tensions sit between existing decisions
- R17. Can invoke /concept when a specific idea needs deep thinking, and returns to PM mode afterward with the context intact
- R18. Can invoke /whats-next when thinking is done and it's time to figure out execution
- R19. Maintains coherence — flags when a new insight contradicts an earlier decision, when scope is creeping, or when multiple threads need to be reconciled

### /whats-next — Strategic Execution Advisor

- R20. Takes the output of strategy/concept sessions and analyzes what needs to happen across deliverables and workstreams
- R21. Presents a task overview: "here's what I see needs to happen" — with reasoning about *why* each task matters and suggested approach/order
- R22. Has an educated, opinionated perspective on execution: recommends what to do and what *not* to do, considers multiple paths and suggests which one best serves the strategic context
- R23. Offers options when there are genuinely different approaches, with trade-offs explained in strategic terms (not just effort/complexity)
- R24. After user approval of the task list, delegates to the existing `/capture` skill for mechanical task creation in mission control
- R25. Writes prompt files to `docs/prompts/` — each one a self-contained brief for an execution conversation, with enough context about the concept and what needs to change
- R26. Works both as an end-phase of /strategy and as a standalone skill (for when you have notes or artifacts ready to turn into action without a live strategy session)

### Knowledge Layer

- R27. `docs/strategy/context.md` is a living file in each project repo: shared vocabulary, active frameworks, key decisions, open questions, current state of strategic thinking
- R28. `docs/strategy/` also contains individual knowledge artifacts (dated, like other skill outputs): `YYYY-MM-DD-<topic>.md`
- R29. The context.md file is the primary cross-session memory for strategic work. Skills read it at start and offer to update it at end. It supplements (does not replace) Claude's memory system
- R30. The command-module plugin provides the skills and interaction patterns. All project-specific content (vocabulary, frameworks, domain knowledge) lives in the project repo, not in the plugin

### Skill Category and Organization

- R31. All three skills live under a `strategy/` category in the skills directory
- R32. Skills follow existing command-module conventions: SKILL.md with frontmatter, references/ subdirectory where needed
- R33. Agent references use fully-qualified namespace: `compound-engineering:strategy:<agent-name>`

## Success Criteria

- The /concept skill produces conversations that follow the reframe-react-sharpen pattern naturally, with short back-and-forth exchanges
- A user can start a /strategy session, dive into /concept for a specific idea, and return to the PM conversation with context preserved
- /whats-next produces actionable task overviews with strategic reasoning, not just task lists
- Knowledge artifacts capture enough context that a future session can pick up where the last one left off
- context.md accumulates useful shared vocabulary over multiple sessions without becoming bloated
- The toolkit works for any domain of conceptual/strategic work, not just portfolio strategy

## Scope Boundaries

- **Not building:** Writing/prose capabilities — these exist in writing-foundations and proof
- **Not building:** Visual/design evaluation — this exists in design-foundations and design-critic
- **Not building:** The mission control task system itself — /whats-next delegates to /capture
- **Not building:** Engineering execution — that's what plan, work, and code-review are for
- **Not scope:** Defining the content of any specific project's context.md — that emerges from use
- **Not scope:** Multi-user collaboration patterns — this is for one person thinking with Claude

## Key Decisions

- **Three skills, not one:** /concept (deep thinking), /strategy (PM entry point), /whats-next (execution advisor). Each has a distinct interaction pattern and can work standalone or chained
- **No plugin-level knowledge base:** Command-module provides skills. Domain knowledge lives in each repo under docs/strategy/
- **PM is not a persistent agent:** It's the behavior of the main conversation when /strategy is active, supported by context.md as shared memory
- **Build /concept first:** It's the core pattern that everything else depends on. If the reframe-react-sharpen cycle works as a skill, the rest follows naturally
- **Naming:** /concept, /strategy, /whats-next. Agent names can be longer and descriptive (e.g., strategic-execution-advisor)

## Dependencies / Assumptions

- Existing `/capture` skill works for task creation (used by /whats-next)
- `docs/prompts/` convention for prompt files (created by /whats-next if it doesn't exist)
- `docs/strategy/` convention for knowledge layer (created by skills if it doesn't exist)
- Mission control task tracking exists in project repos

## Outstanding Questions

### Deferred to Planning

- [Affects R7, R8] [Needs research] What structure should knowledge artifacts follow? The research says "rich and contextual" but the exact template should emerge from looking at what information is most useful across sessions
- [Affects R27] [Needs research] What structure should context.md follow? Sections for vocabulary, decisions, open questions, framework state — but the right organization should be informed by how similar living documents work in practice
- [Affects R15, R17] [Technical] How does /strategy invoke /concept and preserve context? In Claude Code, skill invocation within a conversation — need to verify the mechanics
- [Affects R24, R25] [Technical] Integration with /capture and docs/prompts/ — verify the capture skill's interface and the prompt file convention across repos
- [Affects R31] [Technical] Skills directory currently uses flat organization. "strategy/" as a category prefix in skill names (strategy-concept, strategy-whats-next) or as a subdirectory — check which pattern the plugin supports

## Next Steps

-> `/implementation-plan` for structured implementation planning, starting with /concept as the MVP
