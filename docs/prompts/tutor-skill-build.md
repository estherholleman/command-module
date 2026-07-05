# Build: `tutor` learning-companion skill

Run `/work` with this context (the plan below carries the full detail — read it first).

## What to build

A new lean plugin skill at `plugins/command-module/skills/tutor/` — a patient, **expository + learner-steered** (not Socratic) companion for curiosity-driven learning of external topics. It invokes the already-built `deep-research-panel` skill as a tool (always-ask before spending), reuses an agent-neutral personal learner profile, and teaches in a way tuned to how this learner learns. 4 implementation units, all in the plan.

## Origin / plan docs

- Plan (all detail — units, decisions, file paths): `docs/plans/2026-07-05-001-feat-tutor-learning-companion-plan.md`
- Requirements: `docs/brainstorms/2026-07-05-tutor-learning-companion-requirements.md`

## Key context

- **Precedent to mirror closely:** `plugins/command-module/skills/advisor/SKILL.md` — the `~/.claude/<skill>/` personal-file store + first-run bootstrap from a `references/` template + placeholder detection. The learner profile goes at `~/.claude/tutor/learner-profile.md`.
- **Research tool + state layout:** `plugins/command-module/skills/deep-research-panel/SKILL.md` — writes to `research/<date>-<slug>/`; `tutor` reuses that topic dir for `notes.md` (checkpointed at thread breaks).
- **Teaching-quality bar (the whole point):** `/Users/esther/prog/systems-blog/research/conversation_on_EBMs.md` — reproduce its feel: name concepts, analogy, connect to the learner's frame (PhD comp-neuro, visual learner, loves density, chains questions, wants honest complications), surface the honest complication, follow the learner's nose, end substantive turns with a steering menu, offer simple SVGs.
- **Lean ethos:** craft (teaching moves + profile) is the product, NOT machinery. ~3 content files (SKILL.md + `references/teaching-moves.md` + `references/learner-profile-template.md`) + a README row. Resist schemas, phase state, auto-triggers.
- **Plugin conventions:** frontmatter name+description (quote if it has a colon); backtick-path references; imperative voice, no second person; cross-platform question tool naming + numbered fallback; sibling-skill refs semantic ("invoke the `deep-research-panel` skill"), never slash; ASCII identifiers. Update README table + skills count; run `bun test tests/frontmatter.test.ts` (must pass) and `bun run release:validate` (expected to already fail on pre-existing metadata drift — do NOT hand-bump manifests).

## Critical git/branch context

The current branch `advisor-skill` has 3 stacked features (deep-research-panel `5d61468`, advisor `f94ab4e` — a parallel session's, **do not touch**, tutor planning docs `e04519f`) and a parallel advisor session may still be live. **Cut a fresh branch** (e.g. `feat/tutor-skill`) off current HEAD before implementing. NEVER use bare `git stash`; stage by explicit path only; back up untracked deliverables; commit only tutor files. No `Co-Authored-By` lines.

## Out of scope

- Blog writing (tutor only offers a handoff pointer to `writing-foundations`/`proof`, seeded by `notes.md` + reports).
- Auto-running deep research; new research mechanisms; Socratic style.
