---
name: proof
description: "Review and edit long-form prose for natural writing style, removing AI-typical patterns. Use when finalizing articles, guides, tutorials, documentation pages, or any narrative prose."
argument-hint: "[file path]"
---

# Proof

Review and edit prose documents against comprehensive writing style references that identify AI-typical patterns: banned words, sentence structures, paragraph habits, punctuation quirks, and tone problems that make text read as machine-generated.

## Scope

Targets **long-form prose**: articles, blog posts, guides, tutorials, documentation pages, external communications, and similar narrative writing.

Does **not** apply to: implementation plans, brainstorm documents, commit messages, PR descriptions, code comments, changelogs, structured skill outputs, or internal working documents.

## Language Support

Two reference files contain the full antipattern rules, one per language:

- `references/writing-style-en.md` -- English writing patterns
- `references/writing-style-nl.md` -- Dutch writing patterns (includes Netherlands-specific conventions and anglicism detection)

Detect the document language from its content and load the matching reference. If the document mixes languages, load both.

## Phase 1: Identify the Document

**If a file path is provided in arguments:** Read it.

**If no path is provided:** Ask which document to review using the platform's question tool (AskUserQuestion in Claude Code, request_user_input in Codex, ask_user in Gemini). Suggest recent prose files if discoverable.

## Phase 2: Scan and Classify

Read the appropriate `references/writing-style-*.md` file for the full antipattern rules.

### Full-document scan

Before diving into sections, do a full-document scan using the native content-search tool (e.g., Grep in Claude Code) to count the scale of findings per category. This informs how to structure the review passes:

1. Grep for banned verbs, adjectives, nouns (case-insensitive)
2. Grep for filler phrases
3. Count em dash occurrences
4. Count bold-first bullet patterns (`- **...**:`)
5. Scan for "not X -- it's Y" constructions

Report the scale to the user: "Found approximately N banned words, M em dashes, K structural patterns across L lines. Here's how I recommend we approach this."

### Classify findings into tiers

Every finding gets assigned to one of two tiers:

**Tier 1 -- Auto-fix:** Mechanical substitutions where the replacement is clear and unambiguous. Apply these without asking. Examples:
- Banned verbs/adjectives with a single obvious everyday replacement ("benutten" -> "gebruiken", "cruciaal" -> "belangrijk", "utilize" -> "use")
- Filler phrases that should simply be deleted ("Het is belangrijk om te benadrukken dat...", "It's worth noting that...")
- Oxford comma removal in Dutch text
- English-style title capitalization in Dutch headings

**Tier 2 -- User decision:** Anything that requires judgment. Present these as multiple-choice in a findings document. Examples:
- Em dashes: the right replacement (comma, period, colon, parenthetical, or keep) depends on context
- Banned nouns that might be legitimate domain language ("landschap" in a strategy doc, "ecosystem" in a biology paper)
- Structural patterns where the rewrite could go several directions
- Tone issues where the fix changes meaning
- Bold-first bullets that might genuinely aid scannability
- Any pattern where there is only one occurrence in the entire document (might be fine to keep)

### For long documents (>500 lines)

Recommend a pass-based approach to the user:

- **Pass 1:** Banned words + filler phrases (auto-fix tier 1, present tier 2 word choices)
- **Pass 2:** Nouns that need judgment (domain language vs. lazy metaphor -- ask user for a blanket policy first, then present remaining cases)
- **Pass 3:** Em dashes (present with context-specific replacement options)
- **Pass 4:** Structural and tone patterns (requires reading prose in context -- go section by section)

For shorter documents, all passes can run in a single review.

## Phase 3: Auto-Fix (Tier 1)

Apply all tier 1 fixes directly to the document. Before applying, show a brief summary of what will change:

```
Auto-fixing 14 items:
- 5x banned verbs (benutten -> gebruiken, optimaliseren -> verbeteren, ...)
- 3x filler phrases removed
- 4x Oxford comma removed
- 2x heading capitalization fixed
```

Ask for a quick confirmation before applying. After applying, report what changed.

## Phase 4: Findings Document (Tier 2)

Generate a findings document for all tier 2 items. Write this to a file alongside the reviewed document (e.g., `[document-name]-proof-findings.md`).

### Findings document format

```markdown
# Proof Findings: [document name]

**Document:** [file path]
**Language:** [detected]
**Date:** [today]

## How to use this document

Review each finding below. Each has labeled options (A, B, C, etc.).
Option A is always "keep as-is." Return your choices as a list:
F1: B, F2: A, F3: C, ...

---

## Pass 1: Word Choice

### F1: "cruciaal" (line 214)

> Het verschil tussen latent en afgewezen is **cruciaal** voor de positiebepaling.

Context: appears 4 times in the document (lines 214, 723, 1272, 1330).

- **A: Keep as-is.** "Cruciaal" is strong but may be the right word here given the emphasis needed.
- **B:** "...is **belangrijk** voor de positiebepaling." (neutral, safe)
- **C:** "...is **bepalend** voor de positiebepaling." (stronger, more precise)

---

### F2: "ecosysteem" (line 64)

> het ecosysteem dat Portbase bedient

Context: appears 15 times across the document. This is a recurring term -- your decision here sets the policy for the other 14 instances.

- **A: Keep as-is.** This may be legitimate domain language for a port logistics context.
- **B:** Replace with "de sector" or "de keten" depending on context.
- **C:** Keep in section titles and definitions, replace with plainer alternatives in body text.

---

## Pass 2: Em Dashes

### F3: Em dash (line 550)

> Partneren? Faciliteren? — **Stop.** Niet doen.

- **A: Keep as-is.** The dramatic pause works here.
- **B:** "Partneren? Faciliteren? Nee. Niet doen." (period for hard stop)
- **C:** "Partneren? Faciliteren? Stop. Niet doen." (just remove the dash)

---

## Pass 3: Structure and Tone

### F4: Participial phrase tacking (line 318)

> De omzet steeg met 40%, wat de sterke marktpositie onderstreept.

Context: 3 similar constructions in the document (lines 318, 456, 891).

- **A: Keep as-is.**
- **B:** "De omzet steeg met 40%. Die groei kwam vrijwel volledig uit de Aziatische markt." (promote to own sentence with new information)
- **C:** "De omzet steeg met 40%." (cut the participial phrase entirely -- it adds nothing)

---
```

### Key rules for the findings document

- **Option A is always "keep as-is"** -- never assume something must change
- **Include context**: how many times this pattern appears in the document, whether this is the only instance, what section it's in
- **When a finding sets a policy** (like a word that appears 15 times), flag it: "your decision here sets the policy for the other N instances"
- **Group related findings**: if the same banned word appears 4 times, present them as one finding with a policy decision, not 4 separate findings
- **Label findings sequentially** (F1, F2, F3...) across all passes for easy reference
- **Keep options concrete**: show the actual rewritten sentence, not abstract guidance

## Phase 5: Apply User Choices

When the user returns their choices (e.g., "F1: B, F2: C, F3: A, F4: C"):

1. Parse the choices
2. Apply each selected fix to the document (skip any marked A / keep-as-is)
3. For policy decisions (e.g., F2: C means "keep ecosysteem in titles, replace in body"), apply the policy across all matching instances
4. After applying, report what changed and what was kept

If the user provides choices in any reasonable format (numbered list, comma-separated, conversational), interpret them. Do not require exact formatting.

## Sub-Agent Dispatch Mode

When dispatched by another skill (such as distill or changelog) or invoked non-interactively, run in report-only mode: skip tier 1 auto-fixes, skip the findings document, and return a structured summary of findings to the orchestrating skill. The orchestrator decides what to do with them.

To run a lightweight parallel review from another skill, dispatch the `command-module:docs:writing-style-editor` agent instead of loading this full skill.
