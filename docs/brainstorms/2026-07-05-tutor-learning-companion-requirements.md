---
date: 2026-07-05
topic: tutor-learning-companion
---

# Tutor: a patient learning-companion skill

## Problem Frame

Curiosity-driven learning of external topics (e.g. Energy-Based Models heard on a podcast) happens mostly through *chained questions* over a shared reference, not through reading a report. The user (PhD computational neuroscientist, visual learner, loves academic density, learns by asking one sharp question after another, wants honest complications) currently does this ad hoc in a chat window after manually running deep research. There is no skill that codifies the teaching craft, reuses what it knows about *this* learner, and treats deep research as a deliberate anchor rather than the main event.

The `concept` skill sharpens the user's *own* ideas; `explain-pipeline` explains *code*. Nothing is a patient tutor for *external* topics. This skill fills that gap and pairs with the already-built `deep-research-panel` skill as its research tool.

## Requirements

- **R1.** Invoked as `tutor` (e.g. "tutor me on X" / `/tutor <topic>`). A patient, **expository and learner-steered** companion — not Socratic. No completion pressure; the point is learning, with endless patience.
- **R2.** On first use (or when no profile is found), bootstrap a **personal learner profile** at a user-level path (default `~/.claude/learner-profile.md`) by briefly interviewing the user and optionally ingesting a prior learning transcript. On later uses, load it. The profile captures who the learner is and how they learn (background, density preference, visual-learner tendency, question-chaining style, appetite for honest complications). The profile is reused across all repos and also available to sharpen `deep-research-panel` prompts.
- **R3.** **Prime step scales to existing frame.** The tutor judges whether the learner already has a frame — if so, a couple of clarifying questions then straight to a research prompt; if cold, a real orientation from the tutor's own knowledge first — then helps sharpen the question set.
- **R4.** The tutor drafts a deep-research prompt (informed by the profile + sharpened questions) and invokes `deep-research-panel` as a tool to produce the report(s). Running research is **always-ask**: the tutor proposes and the user confirms before spending.
- **R5.** **Learning loop:** expository, learner-steered Q&A anchored on the report(s). The tutor references the reports explicitly, teaches from its own knowledge otherwise, and is honest when neither covers something. It applies codified **teaching moves**: name concepts ("give it the vocabulary it deserves"), use analogy, connect to the learner's frame, surface the honest complication, follow the learner's nose, and end substantive turns with a short **steering menu** of next directions.
- **R6.** **Visuals by default:** when a spatial or relational idea arises, offer a simple SVG illustration (ideas-illustrated quality, handable to another model), matching the learner's visual style.
- **R7.** **Targeted re-research on a trigger:** when a question genuinely exceeds the tutor's knowledge + existing reports (open / current / needs sources), flag the edge and offer a narrow scoped research query — never auto-run.
- **R8.** **Notes:** maintain a lightweight living `notes.md` per topic, updated **at thread breaks** (steering-menu / direction switches), holding current understanding + open threads. This is the resume mechanism for fresh conversations and the seed for a future blog post.
- **R9.** **State layout:** per-topic directory (reusing the `deep-research-panel` output location, `research/<topic>/`) holds the panel reports + `notes.md`.
- **R10.** **Blog handoff:** at a natural stopping point, offer to hand off to a writing skill, passing `notes.md` + reports as the seed. Writing itself is out of scope.

## Success Criteria

- Reproduces the feel of the EBM transcript: dense, analogical, honest, learner-steered, with steering menus and on-demand visuals.
- A whole topic costs ≈ one broad panel + occasional targeted re-research; the conversational loop adds ≈ no research cost.
- A fresh conversation resumes a topic from `notes.md` without re-explaining.
- The learner profile, once built, measurably improves both tutor sessions and `deep-research-panel` prompts, and is reused across repos.

## Scope Boundaries

- Not a blog-writing skill (separate; `notes.md` is the seed).
- Not Socratic — expository + learner-steered by default.
- Does not auto-run deep research; always-ask.
- Does not build new research mechanisms — reuses `deep-research-panel` as-is.
- Not a code-explanation tool (`explain-pipeline` covers code).
- Lean by design: teaching craft + profile are the product, not orchestration/state machinery.

## Key Decisions

- **Altitude — lean, craft-first:** value is the teaching moves + learner profile; minimal machinery.
- **Learner profile — user-level file, discovered + bootstrapped on first run;** reused everywhere including research prompts.
- **Notes — checkpoint at thread breaks** (not per-turn, not on-request-only).
- **Style — expository + learner-steered;** visuals on by default; re-research always-ask.
- **Prime depth — judgment call** scaled to the learner's existing frame.
- **Name — `tutor`** (a persona, not a task).

## Dependencies / Assumptions

- Depends on the `deep-research-panel` skill (already built) as its research tool.
- Assumes a stable user-level path for the profile; must be expressed cross-platform (Claude Code `~/.claude`; other platforms per their conventions) per plugin skill rules.
- Must follow plugin skill conventions: frontmatter, references via backtick paths, cross-platform question-tool naming with a fallback, README table + skill-count update, `release:validate`.

## Outstanding Questions

### Resolve Before Planning
- (none — all remaining questions are technical/planning)

### Deferred to Planning
- [Affects R2][Technical] Exact profile discovery path + order per platform (Claude Code vs Codex vs Gemini) and the bootstrap-interview flow.
- [Affects R4/R7][Technical] How the tutor invokes `deep-research-panel` as a tool across platforms (skill invocation vs agent dispatch), how it passes the drafted prompt, and how it receives report paths.
- [Affects R6][Technical] SVG generation approach (inline in chat vs file written into the topic dir).
- [Affects R8][Technical] The minimal `notes.md` structure (keep it lean).
- [Affects R10][Technical] Which writing skill to hand off to (`proof` / `writing-foundations`) and the exact handoff payload.

## Next Steps
→ `/implementation-plan` for structured implementation planning
