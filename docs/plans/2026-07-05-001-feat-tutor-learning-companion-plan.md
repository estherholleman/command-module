---
title: "feat: Add tutor learning-companion skill"
type: feat
status: completed
date: 2026-07-05
origin: docs/brainstorms/2026-07-05-tutor-learning-companion-requirements.md
---

# feat: Add tutor learning-companion skill

## Overview

Add a new command-module plugin skill, `tutor`: a patient, expository, learner-steered companion for curiosity-driven learning of external topics. It pairs with the already-built `deep-research-panel` skill (its research tool) and reuses a personal, agent-neutral learner profile to teach in a way tuned to how this specific learner learns. The value is teaching *craft* + a reusable *profile*, not orchestration machinery — the skill stays lean.

## Problem Frame

Learning a new topic happens mostly through chained questions over a shared reference, not by reading a report (see origin, evidenced by the real EBM transcript at `/Users/esther/prog/systems-blog/research/conversation_on_EBMs.md`). Nothing in the plugin fills this: `concept` sharpens the user's *own* ideas; `explain-pipeline` explains *code*. `tutor` is a patient teacher for *external* topics that treats deep research as a deliberate, rare anchor.

## Requirements Trace

- R1. `tutor` invocation; expository + learner-steered persona; endless patience, no completion pressure. (see origin: R1)
- R2. Personal learner profile at a user-level path; bootstrap on first run; reused across repos and to sharpen research prompts. (see origin: R2)
- R3. Prime step scales to the learner's existing frame. (see origin: R3)
- R4. Draft research prompt from profile + sharpened questions; invoke `deep-research-panel`; always-ask before running. (see origin: R4)
- R5. Learning loop anchored on reports; codified teaching moves; honest about uncertainty. (see origin: R5)
- R6. Offer simple SVG visuals for spatial/relational ideas. (see origin: R6)
- R7. Targeted re-research on a trigger — flag and offer, never auto-run. (see origin: R7)
- R8. Lightweight living `notes.md` per topic, checkpointed at thread breaks. (see origin: R8)
- R9. Reuse `deep-research-panel`'s per-topic dir `research/<date>-<slug>/`. (see origin: R9)
- R10. Offer blog handoff to a writing skill with `notes.md` + reports as seed; writing out of scope. (see origin: R10)

## Scope Boundaries

- Not a blog-writing skill; not Socratic; does not auto-run research; does not build new research mechanisms; not a code-explanation tool. Lean by design. (see origin: Scope Boundaries)

## Context & Research

### Relevant Code and Patterns

- **`skills/advisor/SKILL.md` — the primary precedent.** Stores personal user data at an agent-neutral `~/.claude/advisor/` path (`plan.md`, `learnings.md`), bootstraps on first run when the file is absent or still contains template placeholders, copies a scaffold from `references/plan-template.md`, and reads-before-acting. `tutor` mirrors this structure for the learner profile.
- **`skills/deep-research-panel/SKILL.md` — the research tool + state layout.** Writes to `research/<date>-<slug>/` at repo root (`git rev-parse --show-toplevel`, `date +%F`, kebab slug). `tutor` reuses this exact per-topic dir and drops `notes.md` there.
- **Sibling-skill invocation convention.** Skills reference each other semantically: "invoke the `deep-research` skill", "Load the `document-review` skill", "Load the `proof` skill". `tutor` says "invoke the `deep-research-panel` skill" — never a slash command (per AGENTS.md cross-platform reference rules).
- **Plugin skill conventions (AGENTS.md):** frontmatter `name`+`description` (quote description if it contains a colon); references via backtick paths (`@`-inline only for small always-needed files <150 lines); imperative/infinitive voice, no second person; cross-platform question tool naming (`AskUserQuestion`/`request_user_input`/`ask_user`) + numbered fallback; scratch under `.context/command-module/<skill>/` (but `notes.md`/reports are durable → `research/`); ASCII identifiers; README table row + skills-count bump; `release:validate`.

### Institutional Learnings

- `docs/solutions/skill-design/` conventions and the `Upstream-Sourced Skills` / reference-inclusion rules in AGENTS.md.
- Project memory: `release:validate` fails on clean HEAD from pre-existing release-owned count drift — do **not** hand-bump manifests to make it pass.

### External References

- None. Well-patterned work with a same-repo precedent (`advisor`) and a sibling skill (`deep-research-panel`) just authored. External research skipped.

## Key Technical Decisions

- **Learner profile path: `~/.claude/tutor/learner-profile.md`** (namespaced under the skill, agent-neutral), refining the origin's `~/.claude/learner-profile.md` to match the `advisor` precedent exactly. Rationale: consistency with the established `~/.claude/<skill>/` convention already in this plugin; keeps per-skill personal state tidy and relocatable.
- **Bootstrap mirrors `advisor` onboarding:** if the profile is missing or still has template placeholders, copy `references/learner-profile-template.md`, run a short interview (3-5 focused questions), and optionally ingest a prior learning transcript the user points at (e.g. the EBM conversation) to infer style. Otherwise load it.
- **Profile is the craft input, not machinery:** it is read at session start and fed both to the tutor persona and into the drafted research prompt (R2/R4).
- **Teaching moves live in a `references/teaching-moves.md` playbook** (backtick path, loaded on demand) with a tight essence-summary inline in `SKILL.md`, so the core is always in context while depth/examples stay on-demand. Rationale: keeps `SKILL.md` scannable without losing the craft that is the whole point.
- **SVGs inline by default,** saved into the topic dir only on request (`research/<date>-<slug>/`), matching the learner's "hand it to another model" use.
- **Re-research = always-ask,** offering a *narrow scoped* `deep-research-panel` (or single focused query), never auto-run.
- **Blog handoff is a pointer, not a pipeline:** at a natural stop, suggest a fresh conversation seeded by `notes.md` + reports using the writing skills (`writing-foundations` then `proof`).

## Open Questions

### Resolved During Planning

- **Profile location/discovery** → `~/.claude/tutor/learner-profile.md`, agent-neutral, per the `advisor` precedent; bootstrap when absent/placeholder.
- **How `tutor` calls `deep-research-panel`** → semantic skill invocation ("invoke the `deep-research-panel` skill") with the drafted prompt; it writes to `research/<date>-<slug>/` and returns report paths, which `tutor` then reads as anchors.
- **SVG approach** → inline by default; save to topic dir on request.
- **`notes.md` structure** → minimal: `Understanding so far`, `Open threads / questions`, and an optional `Steering log`, with a header noting date + source report paths.
- **Which writing skill for handoff** → `writing-foundations` (craft) + `proof` (polish); tutor only points to them.

### Deferred to Implementation

- Exact interview question set for the bootstrap (keep to 3-5; derive from the EBM transcript's revealed dimensions: background, density preference, visual tendency, question-chaining, appetite for honest complications).
- Whether the bootstrap should offer to read an existing `~/.claude/advisor/plan.md` to pre-fill background (same person) — nice synergy, but keep optional to avoid coupling the two skills.
- Precise essence-summary vs full-playbook split between `SKILL.md` and `references/teaching-moves.md` (settle while writing so `SKILL.md` stays lean).

## Implementation Units

- [x] **Unit 1: Learner profile store + bootstrap**

**Goal:** Define the agent-neutral learner profile and the first-run bootstrap that creates it, so every later session (and research prompt) can load a rich picture of how this learner learns.

**Requirements:** R2

**Dependencies:** None

**Files:**
- Create: `plugins/command-module/skills/tutor/references/learner-profile-template.md`
- (Bootstrap logic authored as a section of `SKILL.md` in Unit 2)

**Approach:**
- Mirror `advisor`'s store exactly: profile at `~/.claude/tutor/learner-profile.md`; template scaffold under `references/`; treat missing/placeholder content as "not set up".
- Template sections: who the learner is (background, domains of fluency), how they learn (density preference, visual tendency, question-chaining, Socratic vs expository), standing interests, and a dated Updates log.
- Bootstrap: short interview (3-5 questions) + optional transcript ingestion; write the filled profile; confirm before continuing to the topic.

**Patterns to follow:**
- `skills/advisor/SKILL.md` steps 1-3 and `references/plan-template.md` (store, placeholder detection, onboarding).

**Test scenarios:**
- Fresh machine (no `~/.claude/tutor/`) → bootstrap runs, writes a valid profile, then proceeds.
- Existing valid profile → loaded silently, no re-onboarding.
- Template-placeholder profile → treated as not set up.

**Verification:**
- The template renders as a clear, fillable scaffold; the bootstrap description unambiguously creates and later loads `~/.claude/tutor/learner-profile.md`.

- [x] **Unit 2: Tutor SKILL.md core (persona + session flow)**

**Goal:** The heart of the skill — persona, the frame-scaled prime, research handoff, the learning loop, notes checkpointing, the re-research trigger, and the blog-handoff pointer.

**Requirements:** R1, R3, R4, R5, R7, R8, R9, R10

**Dependencies:** Unit 1 (profile), Unit 3 (teaching-moves reference)

**Files:**
- Create: `plugins/command-module/skills/tutor/SKILL.md`

**Approach:**
- Frontmatter: `name: tutor`; `description` covering what + when (mention Claude/Gemini/ChatGPT-agnostic learning, pairing with deep research), quoted if it contains a colon.
- Flow: (1) load profile (Unit 1) → (2) prime scaled to existing frame (judge: light clarify-then-research vs full orientation) → (3) draft research prompt from profile + sharpened questions, **always-ask**, then "invoke the `deep-research-panel` skill" → (4) read returned reports as anchors → (5) expository, learner-steered Q&A with the essence of the teaching moves inline and a pointer to `references/teaching-moves.md` → (6) checkpoint `notes.md` at thread breaks → (7) on a knowledge edge, flag + offer scoped re-research (never auto) → (8) at a natural stop, offer blog handoff pointer.
- `notes.md` minimal structure documented inline; SVG-on-request behavior documented inline.
- Cross-platform question tool + numbered fallback where the flow asks the user anything (prime questions, always-ask research, steering menu confirmations).

**Patterns to follow:**
- `skills/deep-research-panel/SKILL.md` (topic-dir resolution, invocation-as-tool tone); `skills/explain-pipeline/SKILL.md` (loads `proof` as a downstream skill — same handoff idiom).

**Test scenarios:**
- Learner arrives with a strong frame → 1-2 clarifying questions, then always-ask research offer.
- Learner arrives cold → orientation-first before any research.
- Mid-session knowledge edge → tutor flags and offers scoped re-research; declining continues the loop.
- Direction switch / steering menu → `notes.md` updated at that break.

**Verification:**
- A cold read of `SKILL.md` reproduces the EBM-transcript feel (naming, analogy, honest complications, steering menus, visuals) and never auto-spends on research.

- [x] **Unit 3: Teaching-moves playbook reference**

**Goal:** Codify the craft that made the EBM conversation great, in depth, loaded on demand.

**Requirements:** R5, R6

**Dependencies:** None (can be authored in parallel with Unit 2)

**Files:**
- Create: `plugins/command-module/skills/tutor/references/teaching-moves.md`

**Approach:**
- Derive moves from the EBM exemplar: name concepts ("give it the vocabulary it deserves"), reach for analogy (jazz/music), connect to the learner's frame, surface the honest complication, follow the learner's nose, end substantive turns with a short steering menu, calibrate density to the profile, and offer simple ideas-illustrated SVGs for spatial/relational ideas.
- Include 1-2 short worked snippets (paraphrased from the EBM transcript) showing a good analogy + a good steering menu.

**Patterns to follow:**
- Backtick-path reference convention; keep each move actionable, imperative voice.

**Test scenarios:**
- Each move is concrete enough to apply without further explanation; the SVG guidance yields hand-off-able output.

**Verification:**
- `SKILL.md`'s inline essence-summary and this playbook agree and do not contradict; no second-person voice.

- [x] **Unit 4: Plugin integration (docs + validation)**

**Goal:** Register the skill in the plugin surface without hand-bumping release-owned metadata.

**Requirements:** R1 (discoverability)

**Dependencies:** Units 1-3

**Files:**
- Modify: `plugins/command-module/README.md` (add a `tutor` row under a suitable section — e.g. Strategy or a learning-oriented group — and bump the Skills count)
- Verify: `plugins/command-module/.claude-plugin/plugin.json` description (no manual count/version bump)

**Approach:**
- Add the README row + count bump only (stage by explicit path to avoid entangling concurrent work on this branch).
- Run `bun test tests/frontmatter.test.ts` (must pass) and `bun run release:validate` (expected to report pre-existing drift; confirm no *new* drift attributable to this skill, do not hand-fix manifests).

**Patterns to follow:**
- The `deep-research-panel` README addition + count bump just landed on this branch.

**Test scenarios:**
- `bun test tests/frontmatter.test.ts` passes (valid YAML, description present).
- `release:validate` shows only pre-existing drift, nothing new introduced by `tutor` beyond the expected count delta.

**Verification:**
- README table lists `tutor`; frontmatter test green; no manifest version/count edits committed.

## System-Wide Impact

- **Interaction graph:** `tutor` → invokes `deep-research-panel` (existing), reads `~/.claude/tutor/learner-profile.md` (new, shared with future research-prompt use), writes `research/<date>-<slug>/notes.md`. Optional read of `~/.claude/advisor/plan.md` is deferred/optional.
- **Error propagation:** if `deep-research-panel` fails a leg, `tutor` still teaches from model knowledge + whatever reports exist (graceful, matches always-ask/anchor design).
- **State lifecycle:** `notes.md` is the resume + blog seed; profile is durable personal state; both are user-owned files, never committed by the skill.
- **API surface parity:** none — no code contracts; pure skill (Markdown) that converts to other platforms via existing pipeline (semantic references stay valid).

## Risks & Dependencies

- **Concurrent branch churn:** the `advisor` skill is being built in a parallel session and shares the `~/.claude/<skill>/` convention. Keep `tutor` decoupled (its own namespace); only *optionally* read advisor's plan. Stage README by explicit path (per project memory on concurrent-swarm git).
- **Over-building risk:** the main risk is machinery creep. Hold the line on lean — 3 content files (SKILL + 2 references) + a README row.
- **Dependency:** requires `deep-research-panel` (present on this branch, not yet merged) — sequence the tutor merge after it, or land together.

## Documentation / Operational Notes

- README table + skills count are the only doc surface. No manifest edits. No CHANGELOG entry (release-owned).

## Sources & References

- **Origin document:** [docs/brainstorms/2026-07-05-tutor-learning-companion-requirements.md](docs/brainstorms/2026-07-05-tutor-learning-companion-requirements.md)
- Precedent skills: `plugins/command-module/skills/advisor/SKILL.md`, `plugins/command-module/skills/deep-research-panel/SKILL.md`, `plugins/command-module/skills/explain-pipeline/SKILL.md`
- Exemplar transcript: `/Users/esther/prog/systems-blog/research/conversation_on_EBMs.md`
- Conventions: `plugins/command-module/AGENTS.md` (skill compliance checklist)
