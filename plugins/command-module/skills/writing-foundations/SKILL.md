---
name: writing-foundations
description: "Writing craft fundamentals -- clarity, structure, voice, sentence craft, persuasion, audience awareness. Load as a writing knowledge base when producing prose (articles, presentations, proposals, reports) or use to critique any written output. Medium-agnostic."
---

# Writing Foundations

Writing craft knowledge base covering clarity, structure, voice and tone, sentence craft, persuasion, audience awareness, and medium-specific conventions. Medium-agnostic -- the same principles apply whether the output is a presentation script, a strategy memo, a blog post, a proposal, or slide content.

## Two Modes

### Mode 1: Build (loaded by other skills or at session start)

When producing any prose, read both knowledge bases and apply them throughout the writing:

- `references/writing-principles.md` -- what good writing looks like (craft principles)
- `skills/proof/references/writing-style-en.md` -- what AI-generated writing looks like (antipatterns to avoid)

For Dutch prose, also read `skills/proof/references/writing-style-nl.md`.

Do not dump the principles as a checklist -- internalize them and let them guide decisions naturally as they arise. The antipatterns are not a review step; they are patterns to simply never produce in the first place.

This mode activates when:
- The user is writing or drafting a document, article, memo, proposal, or report
- The user is writing presentation content or speaker notes
- The user is producing marketing copy, blog posts, or external communications
- Another skill loads this one as a writing knowledge base
- The user asks to "write well" or "make it professional" without specifying a technique

In build mode, apply writing principles proactively during creation -- lead with the point, match voice to audience, vary sentence structure, cut what doesn't earn its place. Do not wait until the end to review.

Key build-mode behaviors:
- **Lead with the point.** Structure every section so the most important information comes first.
- **Match register to audience.** Adapt formality, vocabulary, and assumed context to who will read this.
- **Cut aggressively.** First drafts are always too long. Every word should do work.
- **Vary rhythm.** Mix sentence lengths and structures. Short after long. Simple after complex.
- **Be concrete.** Specific details over abstract categories. Numbers with context over vague qualifiers.

### Mode 2: Critique (invoked directly on a written artifact)

When given a document, draft, or any written output to evaluate:

1. Read `references/writing-principles.md` and the proof antipattern reference (`skills/proof/references/writing-style-en.md`, or the Dutch variant for Dutch text)
2. Follow the critique framework (section 8) to evaluate the artifact, also flagging AI-typical patterns from the antipattern reference
3. Produce a structured critique organized by discipline (clarity, structure, voice, sentence craft, purpose fit)
4. For each finding, explain:
   - **What**: the specific issue, with a quote from the text
   - **Why it matters**: the writing principle being violated
   - **How to fix it**: a concrete rewrite or suggestion
5. Rate overall writing quality on a 1-10 scale with a one-sentence justification

Critique is honest but constructive. Prioritize by impact -- address the three things that would improve the writing most, not twenty micro-issues. A piece with strong structure and clear argument but mediocre sentence craft is in better shape than a piece with polished sentences but no through-line.

#### Critique for different formats

When critiquing presentations, evaluate the slide content as writing (headlines, bullet text, speaker notes) against presentation-specific principles from section 7. When critiquing code documentation, focus on clarity and audience awareness over voice and style.

## Relationship to Other Skills

- **proof**: Specialized AI-pattern detector with an interactive review workflow (auto-fix tiers, findings documents, user choices). Writing-foundations loads proof's antipattern rules during both build and critique mode, so the patterns are avoided from the start. Proof remains useful as a standalone pass for documents that were written without writing-foundations loaded, or when the interactive tier-based review workflow is needed.
- **design-foundations**: Parallel skill for visual craft. Same two-mode structure (build + critique), different domain. When building something that has both visual and written components (presentations, reports with layout), both skills can be loaded together.
- **export-docx**: Utility for document conversion. Style-independent -- it doesn't care how well the writing is.
- **writing-style-editor** agent: Lightweight prose reviewer dispatched by other skills. Can reference writing-foundations principles for its evaluations.
