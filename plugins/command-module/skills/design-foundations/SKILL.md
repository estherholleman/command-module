---
name: design-foundations
description: "Graphic design fundamentals -- typography, color, composition, spacing, hierarchy, Gestalt. Load as a design knowledge base when building visual artifacts (slides, PDFs, web pages, posters) or use to critique any visual output. Medium-agnostic."
---

# Design Foundations

Graphic design knowledge base covering typography, color theory, composition, spacing, visual hierarchy, white space, and Gestalt principles. Medium-agnostic -- the same principles apply whether the output is a presentation slide, a PDF, a React component, a poster, or a dashboard.

## Two Modes

### Mode 1: Build (loaded by other skills or at session start)

When building any visual artifact, read `references/design-principles.md` and apply its principles throughout the work. Do not dump the principles as a checklist -- internalize them and let them guide decisions naturally as they arise.

This mode activates when:
- The user is building a presentation, slide deck, or pitch deck
- The user is creating or modifying a PDF, report, or print layout
- The user is designing a poster, flyer, or visual communication
- Another skill loads this one as a design knowledge base
- The user asks to "use good design" or "make it look professional" without specifying a medium

In build mode, apply design principles proactively during creation -- choose appropriate type hierarchy, build a coherent color palette, structure the layout with intentional spacing and alignment. Do not wait until the end to review.

### Mode 2: Critique (invoked directly on a visual artifact)

When given a screenshot, PDF, image, or rendered output to evaluate:

1. Read `references/design-principles.md`
2. Follow the critique framework (section 8) to evaluate the artifact
3. Produce a structured critique organized by discipline (typography, color, composition, hierarchy, spacing)
4. For each finding, explain:
   - **What**: the specific issue
   - **Why it matters**: the design principle being violated
   - **How to fix it**: a concrete, actionable suggestion
5. Rate overall design quality on a 1-10 scale with a one-sentence justification

Critique is honest but constructive. The goal is to improve the work, not to enumerate every imperfection. Prioritize findings by visual impact -- address the three things that would improve the design most, not twenty micro-issues.

#### Critique for non-visual inputs

When asked to critique a file that is not an image or screenshot (an HTML file, a LaTeX document, slide markup, a React component), first render or screenshot it if browser or rendering tools are available. If no rendering is possible, analyze the structural and typographic choices from the source and note that a visual review was not performed.

## What This Skill Is Not

- Not a CSS framework or implementation guide -- it describes what good design is, not how to code it
- Not a brand guidelines generator -- it provides universal principles, not project-specific tokens
- Not a replacement for a designer's judgment on subjective taste -- it covers the craft fundamentals that are broadly agreed upon

## Relationship to Other Skills

- **frontend-design**: Web-specific implementation skill. Design-foundations provides the underlying principles; frontend-design handles CSS, component libraries, and web-specific patterns.
- **design-iterator**: Iterative screenshot-improve loops. Can load design-foundations for its evaluation criteria.
- **design-implementation-reviewer, figma-design-sync**: Figma fidelity tools. Complementary -- they check "does it match the design file," this checks "is the design itself good."
- **proof**: Analogous skill for prose. Proof catches bad writing patterns; design-foundations catches bad visual patterns.
