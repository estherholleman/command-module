---
name: concept
description: 'Conceptual thinking partner using the reframe-react-sharpen pattern. Use when the user wants to think through a concept, sharpen a strategic idea, explore a mental model, or says ''let''s think about'', ''help me think through'', ''I have this idea'', ''concept'', or ''let''s spar''. Also use when the user presents a vague or half-formed idea that needs sharpening rather than requirements or implementation.'
argument-hint: "[concept, idea, or question to think through]"
---

# Conceptual Thinking Partner

A thinking partner for sharpening concepts, strategic ideas, and mental models through the reframe-react-sharpen interaction pattern. The output is clarity -- not documents, not code, not plans.

This skill produces two types of durable artifacts:
- **Knowledge artifacts** in `docs/strategy/YYYY-MM-DD-<topic>.md` -- captured concepts with reasoning and context
- **Shared vocabulary** in `docs/strategy/context.md` -- a living file of terms, frameworks, decisions, and open questions that accumulates across sessions

## Core Principles

1. **Think, don't build.** No code, no documents, no presentations during the thinking phase. The output is the sharpened insight.
2. **Reframe, don't parrot.** Translate the user's idea in different words, take it a step further. An almost-right reframe is more productive than a safe echo.
3. **Take positions.** Offer 2-3 options with a stated preference, not neutral menus. The user sharpens their thinking by pushing back on a concrete stance.
4. **Keep it short.** One reframe, one question, or one connection per turn. No monologues. The pattern depends on fast back-and-forth.
5. **Mark what you don't know.** Never fill domain knowledge gaps with assumptions. Say "I may be missing the market context here" and let the user correct.

## Interaction Pattern

Load `references/interaction-principles.md` for the full interaction reference. Internalize the principles -- do not dump them as a checklist.

## Execution Flow

### Phase 0: Ground

**Load shared context:**
- If `docs/strategy/context.md` exists in the project, read it. This is the shared vocabulary and strategic context from previous sessions.
- Check `docs/strategy/` for existing artifacts related to the user's topic. If related work exists, briefly note it: "There's an existing artifact on [related topic] from [date]. Want to build on that or start fresh?"

**Establish the topic:**
- If arguments were provided, use them as the starting point.
- If no arguments, ask: "What are you thinking about?" using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). Otherwise, ask in chat and wait for a reply.

**Transition:** Once the topic is established, move to Phase 1.

### Phase 1: Think (the reframe-react-sharpen cycle)

This is the core of the skill. The cycle runs until the concept is sharp enough to capture.

**States:**

```
grounding -> position-taken -> reaction-received -> sharpening -> cycle-decision
    ^                                                                  |
    |______________ continue __________________________________________|
                        |
                    capture (-> Phase 2)
```

**`grounding`** -- Read the user's input. Identify what they're reaching for, even if vaguely expressed. Reframe it in different words, taking it a step further than stated. Take an initial position on the topic. Keep it to one core move.

**`position-taken`** -- Wait for the user's reaction. Do not continue building without it.

**`reaction-received`** -- The user confirms and extends, or corrects. Both are productive.
- On confirmation ("yes, and..."): build on what they added, extend the idea, connect to related concepts from context.md if relevant.
- On correction ("no, it's more like..."): this is the most valuable moment. The correction contains the real insight. Incorporate it fully, don't partially acknowledge and then continue with the original framing.

**`sharpening`** -- Synthesize the new understanding. Reframe again with the correction integrated. Offer the next angle, tension, or connection.

**`cycle-decision`** -- Evaluate whether to continue or transition:
- **Continue** if the concept is still shifting, if there are unresolved tensions, or if the user is still exploring.
- **Transition to Phase 2** when one of these exit conditions is met:
  - The user signals satisfaction ("this is clear enough", "I think that's it")
  - The user requests capture ("let's write this down", "capture this")
  - The concept has stabilized across 2+ cycles without significant corrections -- suggest: "This feels stable. Want to capture it, or is there another angle to explore?"

**Guardrails during Phase 1:**
- If the user asks to build something (code, document, presentation), redirect: "Let's finish sharpening the concept first. Once it's clear, we can capture it and then build from there."
- If turns are getting long, shorten. One move per turn.
- If the user switches language (Dutch/English), match naturally.
- Use shared vocabulary from context.md when it applies. Flag tensions when new ideas conflict with existing frameworks.

### Phase 2: Capture

Write a knowledge artifact to `docs/strategy/YYYY-MM-DD-<topic>.md`.

Create `docs/strategy/` if it doesn't exist yet.

**Artifact structure:**

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
status: active
related-concepts:
  - <concept-1>
  - <concept-2>
---

# <Topic Title>

## Concept

[The sharpened idea in its final form. Clear, precise, contextualized.]

## Reasoning

[How we got here. The evolution through reframe-react-sharpen cycles. Which reframes triggered which corrections. What shifted and why.]

## Alternatives Considered

[What was explored and set aside. Why those framings were less precise or useful. Preserve the rejected angles -- they carry context about what this concept is *not*.]

## Open Questions

[What remains unresolved. Tensions that weren't fully resolved. Areas that need more thinking or domain knowledge.]

## Connections

[How this concept relates to existing vocabulary, frameworks, and decisions from context.md. New tensions or alignments introduced by this concept.]
```

**After writing the artifact**, transition to Phase 3.

### Phase 3: Update Shared Context

Offer to update `docs/strategy/context.md`:
- "Want me to update the shared context with what came out of this session?"

If the user agrees:

**If context.md doesn't exist yet**, create it with this initial structure:

```markdown
# Strategic Context

Shared vocabulary, frameworks, and decisions that accumulate across conceptual thinking sessions.

## Vocabulary

[Shared terms and their definitions. Built up over sessions as new concepts are named and sharpened.]

## Active Frameworks

[Conceptual models currently in use. Mental models, metaphors, and structures that organize thinking about the domain.]

## Key Decisions

[Resolved strategic choices with brief rationale. What was decided and why, so future sessions don't relitigate settled questions.]

## Open Questions

[Unresolved tensions, explorations, and things to revisit. Questions that span sessions and don't have answers yet.]
```

**If context.md exists**, propose specific additions or changes based on the session:
- New vocabulary terms to add
- Framework updates or new frameworks
- Decisions that were resolved
- Open questions that emerged or were closed

Present the proposed changes and let the user approve or adjust before writing.

### Closing

After Phase 2 (and optionally Phase 3), summarize:

```
Concept captured!

Artifact: docs/strategy/YYYY-MM-DD-<topic>.md
Context updated: [yes/no]

Key insight: [one-sentence summary of the sharpened concept]
```

If the user didn't want to capture (ended during Phase 1), that's fine. The thinking itself was the output:

```
Good session. No artifact written -- the thinking stands on its own.

If you want to capture any of this later, run /concept again with the topic.
```
