---
title: "feat: /handoff skill — generate self-contained prompts for fresh conversations"
type: feat
status: active
date: 2026-04-25
origin: docs/brainstorms/2026-04-06-handoff-skill-requirements.md
---

# /handoff Skill — Self-Contained Prompts for Fresh Conversations

## Deferred MVP Value Questions

> **For /work to surface before generating code.** These are "should we build this in its current form" questions, not implementer guidance. /work should pause here and ask the user to answer them before proceeding.

- **Snippet baseline (do-nothing alternative):** The cited quality-bar prompts in `docs/prompts/` were all written manually with no skill. A 3-line saved snippet ("write a handoff prompt for /<next-skill>, mirror docs/prompts/<reference>.md") would solve the choreography pain at near-zero cost. The plan does not quantify how often the friction loop fires per week, nor compare against the snippet baseline. Worth answering: **is the skill defended on measurable savings, or on aesthetics + future caller integration?** If the latter, reframe MVP as scaffolding for /here-or-there (T011) and the deferred /brainstorm/ideate integrations rather than as standalone value.
- **Inline template earns its keep:** The plan inlines a prompt-structure template designed against 4 in-vivo examples, with no second consumer to validate it. Textbook "one consumer = speculative abstraction." A truly minimal MVP could say "read 1-2 most recent docs/prompts/*.md files and mirror their structure." That dodges template-drift-vs-live-examples and defers the abstraction until /here-or-there or one of the deferred integrations stabilizes the contract. Worth answering: **inline template now, or imitate-from-examples until a second consumer forces stability?**

## Overview

Build a small, general-purpose workflow skill that generates a self-contained handoff prompt for starting a fresh conversation, writes it to `docs/prompts/`, and displays it in chat. The skill replaces the recurring manual choreography of "ok, write me a prompt for the next conversation" that happens at every workflow transition (brainstorm → plan, plan → work, strategy → concept, etc.).

## Problem Frame

Every workflow transition today has the same friction loop: the user prefers a fresh conversation for the next phase, has to explain that preference, then has to ask Claude to write a starter prompt that captures decisions, next action, and files to read. The manual prompts in `docs/prompts/` (e.g., `strategy-toolkit-plan-concept-skill.md`, `whats-next-skill-build.md`) show the quality bar — short, action-first, file-grounded. The skill encodes that pattern so the user can drop it into any session by typing `/handoff`.

**What /handoff can and cannot solve:** /handoff targets request-overhead and prompt-quality consistency — the choreography of asking for a starter prompt and the variance in what comes back. It explicitly does **not** solve context-bloat in the source conversation: a skill that runs *inside* a degraded conversation produces a prompt colored by exactly that degradation. When the source conversation is bloated, the prompt body is a downstream symptom, not the cause. If dogfooding shows that handoff prompts consistently feel "off," that is a signal the source conversation degraded earlier — not a /handoff bug.

## Requirements Trace

- R1. Assess current conversation context — covered by Phase 0 grounding (Unit 1). The "ask continue-or-handoff" half of R1 is intentionally **moved to /here-or-there** per the requirements doc for that skill (T011); /handoff is the prompt-generation half. See "Key Technical Decisions" below.
- R2. Generate a self-contained prompt that captures decisions, next action, files/docs to read, and relevant context — covered by Phase 1 prompt generation (Unit 1) plus the structure template (Unit 1).
- R3. Write to `docs/prompts/<file>.md` AND display in chat — covered by Phase 2 (Unit 1). Create `docs/prompts/` if missing.
- R4. Filename: `<topic>-<next-action>.md` — covered by Phase 2 filename derivation (Unit 1), with collision-handling rule.
- R5. Standalone — invokable at any point in any conversation, not just at skill transitions — covered by skill frontmatter and SKILL.md design (Unit 1).
- R6. Callable by other skills/agents at handoff phases (future, not MVP) — addressed by documenting the optional `$ARGUMENTS` shape in SKILL.md so callers can pass `topic`/`next-action` hints, but no caller integration in MVP.
- R7. When the user chooses "continue here," the skill gets out of the way — satisfied transitively: /here-or-there is the asker; if it routes to /handoff, the user already chose to hand off.

## Scope Boundaries

- **Not building:** /here-or-there integration (separate skill, T011)
- **Not building:** Automatic patching of /brainstorm, /implementation-plan, /ideate, etc. handoff phases to call /handoff
- **Not building:** Any mechanism to actually launch the new conversation
- **Not building:** A reference file with curated example prompts — inline a minimal template instead; existing files in `docs/prompts/` already serve as live examples

## Context & Research

### Relevant Code and Patterns

- `plugins/command-module/skills/whats-next/SKILL.md` — closest pattern: also writes to `docs/prompts/`, has an inlined prompt template in Phase 3, uses Phase 0 ground / Phase 1 analyze / Phase 2 present / Phase 3 execute structure. Mirror this skill's structure and template.
- `plugins/command-module/skills/concept/SKILL.md` and `strategy/SKILL.md` — recent strategy toolkit skills, current convention for SKILL.md layout, frontmatter, and phase headings
- `plugins/command-module/skills/brainstorm/SKILL.md` Phase 4 — current ad-hoc handoff pattern that /handoff will eventually replace (out of MVP scope)
- `docs/prompts/strategy-toolkit-plan-concept-skill.md`, `whats-next-skill-plan.md`, `whats-next-skill-build.md`, `here-or-there-skill-plan.md` — manually-written prompts demonstrating quality bar
- `plugins/command-module/AGENTS.md` — Skill Compliance Checklist: YAML frontmatter rules, references inclusion (`@` vs backtick), cross-platform question/task tooling, native tools over shell, README counts must match
- `plugins/command-module/README.md` lines 7-105 — Workflow Utilities table is the registration target; component count at line 9-10 must be incremented

### Institutional Learnings

- `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md` — workflow skills benefit from an explicit state-machine description rather than prose, so edge cases (missing context, empty `docs/prompts/`, collision) don't fall through. /handoff's flow is small but should still call out states explicitly.
- `docs/solutions/skill-design/beta-skills-framework.md` — /handoff is small and high-confidence; ship as a stable skill (no `-beta` suffix) per the framework's "ready when behavior is well-understood" bar.
- AGENTS.md "Pre-Commit Checklist" — README counts and tables must be updated together; `bun run release:validate` must pass.

### External References

None. Local patterns and the existing manual prompts cover everything needed.

## Key Technical Decisions

- **Skill name and namespace:** `handoff` (not `ce-handoff`). Workflow utilities and the strategy toolkit skip the `ce:` prefix; only the autonomous-engineering core skills (`/brainstorm`, `/implementation-plan`, `/code-review`, `/work`, `/distill`) carry it.
- **Skill location and category:** `plugins/command-module/skills/handoff/SKILL.md`, listed under **Workflow Utilities** in the README. Not under Strategy — it's general-purpose, not strategy-specific.
- **Output directory:** `docs/prompts/` in the current working directory's repo root. Create it if missing. Same convention used by `/whats-next` and the manual prompts.
- **Filename format:** `<topic>-<next-action>.md`, kebab-case. Matches existing files. Collisions resolve by appending `-2`, `-3`, …. No timestamps in the filename — they make the listing harder to scan.
- **R1 scope split:** R1 of the requirements doc says /handoff "asks whether to continue here or hand off." That decision was subsequently split into the /here-or-there skill (T011, see `docs/brainstorms/2026-04-06-next-skill-requirements.md` Key Decisions). /handoff therefore goes straight to prompt generation — invocation itself is the user's choice to hand off.
- **Display order:** Generate → **one-line confirmation** ("Writing `<path>` for `/<next-skill>` — proceed? [Y/n/keep going here]") → write file → display path + full prompt content in chat. The single-keystroke confirmation closes the R1/R7 gap window for direct standalone invocations (until /here-or-there ships and becomes the upstream asker), and surfaces inferred topic/next-action *before* a misleadingly-named file lands on disk. The user can edit the inference inline. Once /here-or-there is the routine caller, this confirmation becomes redundant — at that point, consider gating it on `$ARGUMENTS` presence (skip when caller passed explicit args).
- **Inputs:** No `$ARGUMENTS` required. When the user provides arguments, treat the first segment as a topic hint and the rest as a next-action hint (e.g., `/handoff handoff-skill build` → `handoff-skill-build.md`). When arguments are absent, infer both from conversation context and confirm only if ambiguous.
- **Template strategy:** Inline the prompt-structure template directly in SKILL.md Phase 1 (no `references/` file). The template is short, the skill is small, and the existing files in `docs/prompts/` serve as live reference examples. Adding a references file would add carrying cost without a clear benefit.

## Open Questions

### Resolved During Planning

- **What makes a good handoff prompt?** Resolved by inspecting `docs/prompts/strategy-toolkit-plan-concept-skill.md` and the other manual prompts. Pattern: H1 title naming the next action; one-line "Run /xxx with this context"; "What to plan/do" (1-3 lines); "Requirements doc" or origin pointer with full path; "Key context" bullets with file paths and reasoning; optional "Existing skills/files to reference"; explicit non-goals when scope could drift. The template in Unit 1 encodes this.
- **Interface for callers (R6) — what to pass vs. infer?** Resolved as: optional positional arguments `<topic> <next-action>` only. Anything else (decisions made, files touched, next steps) is inferred from the conversation transcript by the model. Callers don't need a richer interface for MVP because the model has the same conversation context they do.
- **Filename collision behavior?** Resolved: increment numeric suffix (`-2`, `-3`, …). Surface the chosen final path in the closing summary so the user is not surprised.

### Deferred to Implementation

- Exact wording of the inline template — phrasing iteration during implementation, not a structural decision
- Whether the skill should warn or auto-append a tag when the inferred topic looks weak (e.g., "general-handoff-1.md") — only address if it surfaces in dogfooding
- **README skill-count drift:** README table shows 42 skills; disk has 48. Decide at implementation time whether the /handoff PR also reconciles the 6-skill drift or whether reconciliation goes to a separate cleanup PR. Either choice is fine; the decision affects the size of Unit 2 only.

## Implementation Units

- [ ] **Unit 1: Author `plugins/command-module/skills/handoff/SKILL.md`**

**Goal:** Create the standalone /handoff skill end-to-end — frontmatter, phase structure, prompt template, file write, chat display.

**Requirements:** R1 (assess only — asking moved to /here-or-there), R2, R3, R4, R5, R6 (callable shape only)

**Dependencies:** None

**Files:**
- Create: `plugins/command-module/skills/handoff/SKILL.md`

**Approach:**
- Frontmatter: `name: handoff`, single-quoted `description:` describing what + when (per AGENTS.md compliance), `argument-hint: "[optional: topic next-action]"`
- Phase 0 — Ground: read the live conversation context. Identify (a) what was just decided or finished, (b) the natural next action, (c) files/docs the next conversation must read. If the user passed arguments, treat first token as topic and remaining tokens as next-action; otherwise infer both.
  - **Ask-vs-infer threshold (concrete rule):** Ask via the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini; chat fallback otherwise) when **any** of the following hold: (1) fewer than 2 prior user turns in the conversation; (2) zero file paths visible in the transcript that the inferred topic could anchor to; (3) the inferred topic and next-action together total fewer than 4 non-stopword tokens. Otherwise infer.
- Phase 1 — Generate prompt: assemble the markdown body using the inline template (see "Technical design" below). Pull file paths verbatim from the conversation (no invented paths).
- Phase 1.5 — Confirm before write: show the user a single-line preview ("Writing `docs/prompts/<topic>-<next-action>.md` for `/<next-skill>` — proceed? [Y/n/edit/keep going here]") via the platform's blocking question tool. `Y` writes; `n`/`keep going here` aborts cleanly (R7 gap closure for standalone invocations); `edit` accepts a corrected topic/next-action and re-renders the preview. Skip this step when `$ARGUMENTS` was provided (the caller already chose the names).
- Phase 2 — Write and display:
  - **Resolve target directory:** start from `git rev-parse --show-toplevel` (one-shot bash command, simple, no chaining). On success, write to `<repo-root>/docs/prompts/`. On failure (not a git repo, command unavailable), fall back to the current working directory and **explicitly state the fallback in the closing summary** so the user knows where the file landed.
  - Create the target `docs/prompts/` if missing.
  - Derive filename `<topic>-<next-action>.md`; if it exists, append `-2`, `-3`, … until free.
  - Write the file. On write failure (permission denied, disk full), surface the error verbatim and the resolved target path so the user can act; do not silently swallow.
  - Print path + full content in chat in a closing summary.
- Make explicit "what /handoff does NOT do" inline (R7 transitivity): if the user wanted to be asked first, point them at /here-or-there.

**Patterns to follow:**
- `plugins/command-module/skills/whats-next/SKILL.md` Phase 3 — inline template with prompt-file conventions
- `plugins/command-module/skills/concept/SKILL.md` — Phase 0 grounding pattern, frontmatter style, closing summary block
- `plugins/command-module/skills/strategy/SKILL.md` — explicit state listing in phases (mini state-machine per the git-workflow-skills learning)

**Technical design:** *(directional guidance — final wording iterates during implementation)*

```markdown
---
name: handoff
description: '<what + when, single-quoted, includes trigger phrases like "/handoff", "hand off to a new conversation", "write me a starter prompt", "set up a fresh conversation">'
argument-hint: "[optional: topic next-action]"
---

# /handoff — Generate a Starter Prompt for a Fresh Conversation

[1-2 line orientation: what this skill does, and when NOT to use it (point at /here-or-there for the assess-and-ask flow)]

## Phase 0 — Ground
- Read $ARGUMENTS. If present: first token = topic, remainder = next-action.
- If absent: infer topic and next-action from the conversation.
- Identify what was decided / what to do next / files to read.
- If the conversation lacks signal, ask topic + next-action via the platform's blocking question tool (...).

## Phase 1 — Generate
Assemble using this structure:

  # <Title naming the next action>

  Run `/<skill-name>` with this context: (or "What to do" header for non-skill handoffs)

  ## What to <plan|build|review|...>
  <1-3 lines>

  ## Origin / requirements doc
  - <path>  (only when one exists)

  ## Key context
  - <bullet with file path>
  - <bullet with strategic reasoning>
  - ...

  ## Out of scope (optional)
  - <non-goals when scope could drift>

## Phase 2 — Write and display
- Ensure docs/prompts/ exists.
- filename = "<topic>-<next-action>.md"; if exists, suffix -2, -3, …
- Write file. Display path + full content.

## Closing
Prompt written to docs/prompts/<file>.md
[full prompt content]
Paste into a fresh conversation when ready.
```

**Test scenarios:**
- Standalone after a brainstorm session that produced `docs/brainstorms/2026-04-25-foo-requirements.md` → confirmation step shows inferred names → produces `foo-plan.md` pointing at the requirements doc and naming `/implementation-plan` as the next action
- Standalone after an implementation-plan session → produces `<topic>-build.md` pointing at the plan path and naming `/work`
- Invoked with arguments `handoff dogfood-test` → confirmation step is **skipped** (caller passed names) → produces `handoff-dogfood-test.md` regardless of conversation content
- Invoked when `docs/prompts/handoff-dogfood-test.md` already exists → produces `handoff-dogfood-test-2.md`
- Invoked at the very start of a fresh session (fewer than 2 prior user turns) → asks topic + next-action via the platform question tool, then runs the confirmation step
- User answers "n" / "keep going here" at the confirmation step → no file written; chat says "no handoff written — staying in this conversation"
- Invoked in a repo where `docs/prompts/` does not exist → directory is created at `<repo-root>/docs/prompts/`, then file written
- Invoked from a non-git directory (no repo root resolvable) → falls back to cwd, closing summary explicitly states the fallback location
- File-write fails (e.g., read-only filesystem) → error and resolved target path surfaced verbatim, no silent failure

**Verification:**
- A fresh conversation could pick up the generated prompt and start productively without needing to be told anything else
- The generated file appears in `docs/prompts/` and the same content is visible in chat
- `bun test tests/frontmatter.test.ts` passes (frontmatter parses cleanly)
- Skill description follows the AGENTS.md format (what + when, single-quoted)

---

- [ ] **Unit 2: Register the skill in README and verify metadata**

**Goal:** Make the new skill visible in the plugin's README and ensure release validation continues to pass.

**Requirements:** Plugin maintenance compliance (AGENTS.md "Pre-Commit Checklist")

**Dependencies:** Unit 1

**Files:**
- Modify: `plugins/command-module/README.md` — add `/handoff` row to the Workflow Utilities table; bump the Skills count in the Component table
- Modify: `plugins/command-module/.claude-plugin/plugin.json` — only if the description references a count that changes (per AGENTS.md, do not hand-bump version)

**Approach:**
- Add row under `### Workflow Utilities`: `` | `/handoff` | Generate a self-contained prompt for starting a fresh conversation at workflow transition points | ``
- Increment the Skills count in the top component-count table. The on-disk count is **48 SKILL.md files** (verified 2026-04-25); the README table currently shows **42** — pre-existing drift unrelated to this plan. Whether to reconcile the 42-vs-48 gap in this PR or defer it to a separate cleanup PR is a scope decision left to the implementer (see Deferred to Implementation below).
- Do not touch version fields in `plugin.json` or `marketplace.json` (release-owned)
- Do not add a CHANGELOG entry (release-owned)

**Patterns to follow:**
- README structure unchanged from prior skill additions (e.g., the `/onboarding` and `/changelog` rows in Workflow Utilities)
- AGENTS.md "Pre-Commit Checklist" verbatim

**Test scenarios:**
- README table renders cleanly with the new row
- `bun run release:validate` passes (metadata consistency)
- Skills count in README matches the actual directory count under `plugins/command-module/skills/`

**Verification:**
- `bun run release:validate` exits 0
- Manual scan of README confirms the row is in the Workflow Utilities section, not Strategy

---

- [ ] **Unit 3: Smoke-test conversion to other targets**

**Goal:** Confirm the new skill survives the converter pipeline so OpenCode/Codex/Gemini installs do not regress.

**Requirements:** Plugin compliance (skill format must round-trip)

**Dependencies:** Unit 1

**Files:**
- Test: `tests/frontmatter.test.ts` (existing — should already cover the new skill via glob)
- Test: existing converter tests under `tests/` (existing — should pick up the new skill automatically)

**Approach:**
- Run `bun test` and confirm all tests still pass
- If any test references an explicit list of skills, add `/handoff` there

**Patterns to follow:**
- Prior skill additions (e.g., `/whats-next`, `/strategy`) did not require new tests; the existing glob-based suites covered them. Expect the same here.

**Test scenarios:**
- `bun test tests/frontmatter.test.ts` passes
- `bun test` (full suite) passes
- No new converter writer code needed

**Verification:**
- All bun tests pass
- If any test hard-codes a skill list and now needs an entry, that's the only change required

## System-Wide Impact

- **Plugin surface:** `plugins/command-module/skills/` gains one directory; README table and component count are the only adjacent files that must move with it.
- **Converter pipeline:** The skill should round-trip through the existing OpenCode / Codex / Gemini / Cursor / Copilot / Windsurf writers without target-specific changes — frontmatter and content are plain markdown with standard conventions.
- **Other skills:** No /brainstorm, /implementation-plan, or /ideate changes in MVP. Future integration is a deliberate follow-up (see Deferred Work below).
- **/here-or-there (T011):** Direct upstream consumer once T011 lands. /handoff's argument shape (`<topic> <next-action>`) and standalone behavior are designed to make that integration trivial.

## Risks & Dependencies

- **Risk:** The skill writes to `docs/prompts/`. **Mitigation (now in MVP, not deferred):** Phase 2 resolves the target via `git rev-parse --show-toplevel` and falls back to cwd with explicit user notice. Test scenarios cover both paths.
- **Risk:** Inferred topic/next-action might be wrong when the conversation has multiple competing threads. **Mitigation:** the user can always pass arguments explicitly; the closing summary surfaces the chosen filename so mistakes are visible immediately.
- **Risk:** Description-string trigger phrases might not catch all the natural ways the user invokes this. **Mitigation:** ship a generous list of trigger phrases ("hand off", "starter prompt", "fresh conversation", "/handoff"), iterate based on dogfooding.
- **Dependency:** None blocking. /here-or-there (T011) depends on /handoff, not the other way around.

## Documentation / Operational Notes

- README update is the user-facing surface (covered in Unit 2). No additional docs needed.
- No rollout, monitoring, or migration concerns — additive skill, no behavior change to existing skills.

## Deferred Work (Cross-Repo and Follow-Up)

Per the deferring-work-three-flavors pattern:

- **Same-repo, condition-triggered:** When T011 (`/here-or-there`) is built, verify `/handoff` integrates cleanly. Already tracked in T011's task entry; no extra marker needed.
- **Same-repo, condition-triggered:** When dogfooding reveals concrete pain (wrong inferences, weird filenames, missing context capture), distill into `docs/solutions/skill-design/` and iterate the skill. No marker needed — surfaces naturally.
- **Same-repo, opt-in future work:** Replace the ad-hoc handoff phases in `/brainstorm` Phase 4, `/implementation-plan` Phase 5.4, and `/ideate` with a call to /handoff. **Not creating a task for this in MVP** — defer until /here-or-there lands and the integration shape is proven; otherwise we'd retrofit the wrong contract.

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-06-handoff-skill-requirements.md](docs/brainstorms/2026-04-06-handoff-skill-requirements.md)
- **Sister skill (T011):** [docs/brainstorms/2026-04-06-next-skill-requirements.md](docs/brainstorms/2026-04-06-next-skill-requirements.md) — clarifies the R1 scope split
- **Quality reference prompts:** [docs/prompts/strategy-toolkit-plan-concept-skill.md](docs/prompts/strategy-toolkit-plan-concept-skill.md), [docs/prompts/whats-next-skill-build.md](docs/prompts/whats-next-skill-build.md)
- **Closest pattern skill:** [plugins/command-module/skills/whats-next/SKILL.md](plugins/command-module/skills/whats-next/SKILL.md)
- **Skill compliance:** [plugins/command-module/AGENTS.md](plugins/command-module/AGENTS.md)
- **Related learning:** [docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md](docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md)
