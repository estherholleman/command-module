---
title: "feat: /here-or-there skill — transition decision point that routes to inline or /handoff"
type: feat
status: completed
date: 2026-04-28
origin: /Users/esther/prog/missioncontrol/tracking/command-module/tasks/T011.md
---

# /here-or-there Skill — Transition Decision Point

## Overview

Build `/here-or-there`, a small workflow-utility skill that answers a single binary question: **should this work continue in the current conversation, or transition to a fresh one?** The skill assesses the live transcript, names its rationale, and either (a) returns control to chat with a brief "stay here" note, or (b) **auto-invokes `/handoff`** with an inferred topic and next-action — no second confirmation.

This skill is the upstream "should I?" gate that `/handoff` already names. `/handoff` stays usable on its own when the user is already opinionated; `/here-or-there` is for the (much more common) case where the user is genuinely undecided about whether the new phase needs a fresh context.

## Problem Frame

At every workflow transition (brainstorm -> plan, plan -> work, strategy -> concept, etc.) the user faces a choice that has nothing to do with the work itself:

> *"Is this conversation still the right vessel for the next thing, or should I start fresh?"*

The current state of the world:
- `/handoff` writes a starter prompt assuming the answer is "fresh." If the user invokes it directly, they have already decided.
- Without `/here-or-there`, the only way to *get* that decision is the user reasoning through it themselves, often poorly (sticky confirmation bias toward "stay here" because spinning up a new conversation feels like effort).
- The /handoff skill's Phase 1.5 single-keystroke preview is a stopgap for direct invocations — `/here-or-there` is the real fix.

`/here-or-there` carries the assessment burden so the user does not have to. It runs the heuristics, makes the call, and routes — turning a recurring micro-decision into a single command.

**What `/here-or-there` does NOT solve:** the underlying causes of context degradation. If the source conversation is already badly bloated, the assessment runs against a degraded transcript and may itself be off — the same caveat `/handoff` carries.

## Requirements Trace

Origin doc T011 frames the work as one decision and three open implementation questions. This plan resolves them as:

- **R1.** Read current conversation, assess transition signals (context bloat, topic shift, natural break, fresh-conversation-would-help). Produce a binary recommendation: `here` or `there`. *Covered by Unit 1, Phase 1.*
- **R2.** When `here`: return control to chat with a brief rationale. *Covered by Unit 1, Phase 2 "here" branch.*
- **R3.** When `there`: automatically invoke `/handoff` with inferred `<topic>` and `<next-action>` — no second confirmation. *Covered by Unit 1, Phase 2 "there" branch + Phase 3.*
- **R4.** Use the contract `/handoff` already exposes for callers (positional args skip Phase 1.5). *Covered by Unit 1, Phase 3 invocation pattern.*
- **R5.** Standalone — invokable at any point in any conversation. *Covered by frontmatter and SKILL.md design.*
- **R6.** Register in plugin README under Workflow Utilities; bump skill count. *Covered by Unit 2.*
- **R7.** Plugin manifest consistency holds (`bun run release:validate`). *Covered by Unit 3.*

## Scope Boundaries

- **Not building:** automatic transition detection (the skill is invoked manually, like `/handoff`).
- **Not building:** any third recommendation state ("it depends", "wrap up first", "/wrap-up then /handoff"). Auto-routing requires a binary decision at the action layer; confidence is expressed in the rationale text, not as a separate state. Multi-destination routing is captured as a condition-triggered follow-up below.
- **Not building:** changes to `/handoff` itself. `/handoff`'s Phase 1.5 already gates on `$ARGUMENTS` presence, so the auto-invoke contract works without modification.
- **Not building:** integration with `/brainstorm`, `/implementation-plan`, `/ideate` handoff phases. Those callers stay manual for now (separate future work).
- **Not building:** programmatic context-window introspection. The agent works from what it can read in the transcript itself.
- **Not re-litigating:** whether `/here-or-there` and `/handoff` should be one skill. Resolved on 2026-04-28; rationale lives in T011.

## Context & Research

### Relevant Code and Patterns

- `plugins/command-module/skills/handoff/SKILL.md` (currently on `feat/handoff-skill`, commit `a51523a`, **not yet on `main`**) — the downstream skill. Critical contract:
  - Accepts positional `$ARGUMENTS` of the form `<topic> <next-action>` (first whitespace-separated token = topic, remainder = next-action).
  - When `$ARGUMENTS` is present, **Phase 1.5 confirmation is skipped** — `/handoff` writes the file directly.
  - Already documents `/here-or-there` as the upstream asker (Phase 1.5 hedge: *"until /here-or-there ships as the upstream asker"*) and the integration shape (final section: *"This is the integration shape for /here-or-there (T011)"*). No `/handoff` edits needed.
- `plugins/command-module/skills/whats-next/SKILL.md` — closest structural analog among shipped skills: also writes to `docs/prompts/`, also reads conversation context, uses Phase 0 ground / Phase 1 analyze / Phase 2 present pattern. Mirror the section structure.
- `plugins/command-module/skills/concept/SKILL.md`, `plugins/command-module/skills/strategy/SKILL.md`, `plugins/command-module/skills/explain-pipeline/SKILL.md` — recent (2026-Q1/Q2) skill conventions: frontmatter shape, phase-headed flow, cross-platform tool naming, semantic skill references.
- `plugins/command-module/AGENTS.md` Skill Compliance Checklist — load-bearing rules:
  - Frontmatter `description` value must be single- or double-quoted if it contains colons (the trigger list will contain colons → must quote).
  - Imperative writing style, no second person.
  - Cross-platform question tooling: name `AskUserQuestion` (Claude Code), `request_user_input` (Codex), `ask_user` (Gemini); fall back to numbered options.
  - When referring to another skill, use semantic wording ("load the `handoff` skill") rather than slash syntax — slash syntax only for actual published commands.
  - README counts must be updated; `bun run release:validate` must pass.
- `plugins/command-module/README.md:38` — the **Workflow Utilities** table is the registration target. README skill count is at line 9-10 (currently `43` on `main` after `/explain-pipeline`; will be `44` once `/handoff` merges; this skill bumps that by `1` again).

### Institutional Learnings

- `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md` — workflow skills with branching outcomes benefit from an explicit state-machine description so edge cases (weak signals, contradicting signals, inference failure) do not fall through. `/here-or-there`'s flow is small but inherently branching — apply this pattern in the SKILL.md.
- `docs/solutions/skill-design/beta-skills-framework.md` — skills with well-understood behavior ship as stable (no `-beta` suffix). The decision rule and signal set are simple enough to ship stable from day one.
- The /handoff plan (`docs/plans/2026-04-25-001-feat-handoff-skill-plan.md`, currently on `feat/handoff-skill`) is the most direct precedent. Its "Inline template earns its keep" deferred-MVP question is worth keeping in mind for /here-or-there: the heuristic set inlined in this skill is also speculative until dogfooded.

### External References

None. Local patterns and the /handoff contract cover the design surface entirely.

## Key Technical Decisions

- **Skill name and namespace.** `here-or-there` (kebab-case, ASCII identifiers per repo policy). Workflow utility — no `ce:` prefix (that prefix is reserved for the autonomous-engineering core skills `/brainstorm`, `/implementation-plan`, `/code-review`, `/work`, `/distill`).
- **Skill location.** `plugins/command-module/skills/here-or-there/SKILL.md`, registered in the README **Workflow Utilities** table.
- **Inputs.** No `$ARGUMENTS` required and none accepted in v1. The skill works entirely from transcript introspection. (If callers later want to seed the assessment, that is a future contract change — out of scope here.)
- **Recommendation cardinality: binary (`here` / `there`).** Auto-routing requires a single action-level call. A third state would either be cosmetic (still routes one of the two ways) or block on user input (defeats the no-second-confirmation design). Confidence is expressed in **rationale text**, not in a third recommendation. The skill always shows a 1-3 line rationale with both branches.
- **Default on weak or contradictory signals: `here`.** The conservative call. The user can always invoke `/handoff` directly if they disagree. Inverting this default would force fresh starts the user did not ask for.
- **Decision rule (intent, not formula).** Recommend `there` when **at least two** of the signals below point that way *with material strength*. Recommend `here` otherwise. The signals are descriptive, not weighted — the agent reasons about them, not arithmetic.
- **Signal set (resolves T011 Q1).** Five categories the agent introspects from the transcript:
  1. **Context accumulation.** Many turns, multiple long tool-result chunks, multi-step work that has visibly bulked the buffer.
  2. **Topic shift.** The user's current request is materially disjoint from the conversation's first 1-2 turns (e.g., opened on "refactor parser X", now asking to plan feature Y).
  3. **Workflow-phase completion.** A discrete unit just finished — a plan was written, a brainstorm closed, a review completed — and the next phase is named.
  4. **Explicit transition language.** *"ok now I want to..."*, *"next step is..."*, *"let's move on to..."*, *"fresh conversation"*, *"new chat"*, *"switch to..."*. Direct user signal — strong evidence on its own.
  5. **Carry-forward cost.** Most of what is loaded into the current conversation (file reads, plan content, tool outputs) is downstream context the next phase does not need; a fresh conversation pays a small re-grounding cost to shed substantial noise.
- **Auto-invoke contract with `/handoff` (resolves T011 binary-recommendation routing).** When the recommendation is `there`, the skill loads the `handoff` skill with positional arguments `<inferred-topic> <inferred-next-action>`. `/handoff` skips Phase 1.5 (its existing `$ARGUMENTS` gate) and writes the prompt file. No second confirmation. The user sees: rationale → "Invoking /handoff with topic=`<X>` next-action=`<Y>`" → /handoff's standard closing output (path + full prompt content). One continuous output.
- **Topic / next-action inference is owned by `/here-or-there`.** Even though `/handoff` can also infer these, when called from `/here-or-there` the inference happens upstream — the inferred values are passed in. This places inference at the layer that did the assessment (i.e., already loaded the relevant transcript context).
- **Other destinations (resolves T011 Q3): out of scope for v1.** No `/wrap-up first, then /handoff` routing; no multi-destination dispatch. Reasoning: scope creep risks turning the skill into a general workflow router. The user can invoke `/wrap-up` independently before or after. If dogfooding shows users frequently want to chain `/wrap-up` before handoff, revisit (captured under Deferred Work).
- **Cross-platform tooling.** This skill never *blocks* on user input (no `AskUserQuestion`, `request_user_input`, `ask_user`). It introspects, decides, and routes. The whole point is removing the question loop. The SKILL.md still names cross-platform tool equivalents only where transcript-reading or skill-loading have platform-specific names.
- **Beta vs stable.** Ship stable (no `-beta` suffix, no `disable-model-invocation`). The skill behavior and decision rule are well-understood enough on day one. The signal set may be tuned via dogfooding but the public contract is stable.
- **No reference files.** The skill is small. The signal set, decision rule, and routing contract all fit in the SKILL.md itself. No `references/` directory.

## Open Questions

### Resolved During Planning

- **Q1 (T011): What signals does `/here-or-there` use?** Resolved — five-category signal set above. Descriptive, not weighted; the agent reasons rather than scores.
- **Q2 (T011): 2-state or 3-state recommendation?** Resolved — binary (`here` / `there`). Auto-routing forces a binary action call; uncertainty lives in the rationale text.
- **Q3 (T011): Should the skill recommend other destinations like `/wrap-up first, then /handoff`?** Resolved for v1 — no. Single binary decision, single downstream call. Multi-destination routing captured as condition-triggered deferred work.
- **Default on weak/contradictory signals?** Resolved — default `here`. Conservative; the user can /handoff explicitly if they disagree.
- **Does the skill confirm before invoking /handoff?** Resolved — no. T011's "no second confirmation" is the hard contract. Rationale is shown, then the invocation runs immediately.

### Deferred to Implementation

- **Exact wording of the rationale output.** The shape (1-3 lines naming which signals fired) is set; the prose is something the implementer tunes against the SKILL.md instruction. Not pre-writeable in this plan without becoming implementation code.
- **Phrasing for the "invoking /handoff" line.** Single short line indicating the routing happened, with the inferred topic and next-action. Tunable during implementation.
- **Edge case: zero-or-one user turn.** If the conversation is too short to introspect meaningfully (no prior user request, or a single greeting), the skill should default to `here` with rationale "not enough context to assess." Handled in SKILL.md Phase 0 with the `/handoff` ask-vs-infer threshold as precedent.

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

```
                +--------------------------+
                | /here-or-there invoked   |
                +-----------+--------------+
                            |
                            v
                +--------------------------+
                | Phase 0: Ground          |
                |  - read transcript       |
                |  - check minimum context |
                |    threshold (>= 2 prior |
                |    user turns, some tool |
                |    result, or topic-name |
                |    inferable)            |
                +-----------+--------------+
                            |
                  too thin? |  no
                +-----------+--------------+
                |                          |
                v                          v
       +--------+--------+        +-----------------------+
       | Output: "stay   |        | Phase 1: Assess       |
       |  here, not      |        |  Walk the 5 signals:  |
       |  enough context |        |   1. context accum.   |
       |  to assess"     |        |   2. topic shift      |
       | DONE            |        |   3. phase completion |
       +-----------------+        |   4. explicit lang.   |
                                  |   5. carry-fwd cost   |
                                  | Score: directional    |
                                  | (>=2 strong -> there) |
                                  +-----------+-----------+
                                              |
                                  +-----------+-----------+
                                  |                       |
                              "here"                  "there"
                                  |                       |
                                  v                       v
                       +-----------------+      +----------------------+
                       | Phase 2a: Stay  |      | Phase 2b: Route      |
                       |  - 1-3 line     |      |  - 1-3 line rationale|
                       |    rationale    |      |  - infer <topic>     |
                       |  - return       |      |    and <next-action> |
                       |    control to   |      |    from transcript   |
                       |    chat         |      |  - state inferences  |
                       | DONE            |      |    in chat output    |
                       +-----------------+      +----------+-----------+
                                                           |
                                                           v
                                                +--------------------------+
                                                | Phase 3: Auto-invoke     |
                                                |  load `handoff` skill    |
                                                |  with $ARGUMENTS =       |
                                                |    "<topic> <next-act>"  |
                                                |                          |
                                                |  /handoff sees args      |
                                                |  -> skips Phase 1.5      |
                                                |  -> writes file +        |
                                                |     displays prompt      |
                                                | DONE                     |
                                                +--------------------------+
```

The state machine is small but has three terminal states (too-thin → here, signals → here, signals → there → /handoff). The SKILL.md should make all three explicit so the implementer does not invent a fourth path.

## Implementation Units

- [ ] **Unit 1: Author `plugins/command-module/skills/here-or-there/SKILL.md`**

  **Goal:** Produce the skill file containing frontmatter, the three-phase flow (Ground / Assess / Route), the five-signal set, the binary decision rule, and the auto-invoke contract with `/handoff`.

  **Requirements:** R1, R2, R3, R4, R5.

  **Dependencies:**
  - `/handoff` skill must be on `main`. Currently on branch `feat/handoff-skill` (commit `a51523a`). **Hard sequencing prerequisite** — see Risks & Dependencies. Do not begin Unit 1 until `/handoff` merges.
  - No code dependencies inside this plan.

  **Files:**
  - Create: `plugins/command-module/skills/here-or-there/SKILL.md`

  **Approach:**
  - Frontmatter:
    - `name: here-or-there`
    - `description:` single-quoted (contains colons in the trigger list); imperative form; describes what + when; includes triggers like *"/here-or-there"*, *"here or there"*, *"should I keep going here"*, *"should I hand off"*, *"continue here or new conversation"*.
    - No `argument-hint` — the skill takes no arguments in v1.
  - Three phases, each with a clear heading:
    - **Phase 0 — Ground.** Read the transcript. Apply the minimum-context threshold (precedent: /handoff's ask-vs-infer threshold; mirror its structure with adapted criteria). On too-thin transcripts, jump straight to Phase 2a with rationale "not enough context to assess — staying here."
    - **Phase 1 — Assess.** Walk the five signals one by one. For each, name what was observed in the transcript. Apply the directional rule (>= 2 signals materially pointing to `there` -> recommend `there`; otherwise `here`).
    - **Phase 2 — Route.**
      - **2a (here):** Output a 1-3 line rationale naming the strongest signal(s) for staying. Return control to chat. Done.
      - **2b (there):** Output a 1-3 line rationale naming the firing signals. Infer `<topic>` and `<next-action>` from the transcript using the same inference grammar `/handoff` documents (topic = subject matter, next-action = verb / next skill). State the inferred values in chat. Then load the `handoff` skill with positional arguments `<topic> <next-action>`. `/handoff` will skip Phase 1.5 (because args are present) and write the file.
  - Cross-platform contract for skill loading: instruct loading the `handoff` skill semantically — "load the `handoff` skill with positional arguments `<topic> <next-action>`" — not slash syntax inside the SKILL.md (per AGENTS.md cross-platform reference rules; `/handoff` is fine in user-facing prose because it is a published skill, but instructions to the agent should be semantic).
  - Tone: imperative ("Read", "Walk", "Recommend"), not second person.
  - Inline state machine in prose form mirroring the diagram above so edge cases are explicit (per the git-workflow-skills institutional learning).
  - Closing section names the relationship to `/handoff` and the resolved design decisions (one short paragraph, not a re-litigation).

  **Patterns to follow:**
  - Phase structure and section headings: `plugins/command-module/skills/whats-next/SKILL.md`.
  - Frontmatter shape, trigger listing, and "When NOT to use this skill" carve-out: `plugins/command-module/skills/handoff/SKILL.md` (this skill is the symmetric partner; the carve-out should mirror /handoff's, e.g., "When NOT to use this skill: if the user has already decided to hand off, load `handoff` directly to skip the assessment").
  - Cross-platform tool naming and semantic skill references: `plugins/command-module/AGENTS.md` Skill Compliance Checklist.

  **Test scenarios** (informal — these are what the SKILL.md instructions must produce when applied by an agent to a live transcript; no automated test):
  - **Long planning conversation that just finished a plan, user asks "now build it":** signals 2 (topic shift small), 3 (phase completion), 4 (explicit transition), 5 (carry-forward cost) all fire → `there` → /handoff invoked with topic ≈ `<plan-name>` next-action = `build`.
  - **Short conversation, 2 turns, user asks "should I keep going":** Phase 0 too-thin guard fires → `here` with "not enough context" rationale.
  - **Mid-task user asks "should I keep going here":** signals 1 and 2 weak, no other firing → `here` with "current context still load-bearing for this work" rationale.
  - **User explicitly says "I want a fresh conversation":** signal 4 strongest → `there` → /handoff invoked. (Edge: explicit user preference outranks weak counter-signals.)
  - **Topic-shifted conversation but still small:** signals 2 and 5 fire weakly, signal 1 does not → `here` (>= 2 strong rule not met) with rationale acknowledging the shift but flagging that fresh-start cost outweighs benefit at current size.
  - **Inference failure for topic/next-action despite "there" recommendation:** the SKILL.md should instruct: if either `<topic>` or `<next-action>` cannot be inferred with even minimal confidence, fall back to `here` with rationale "leaning fresh start but cannot infer the next phase — invoke /handoff directly with your own topic/next-action if you want to proceed." This avoids passing garbage args to /handoff.

  **Verification:**
  - The SKILL.md exists at the expected path with valid YAML frontmatter (no unquoted colons in `description`).
  - Following the SKILL.md instructions on the six scenarios above produces the expected outcomes.
  - The auto-invoke step references the `handoff` skill semantically and passes positional args in the form /handoff's contract documents.
  - No platform-specific tool names appear without their cross-platform equivalents, except where intentional (the load-skill mechanism itself is platform-specific and named appropriately).

- [ ] **Unit 2: Register the skill in the plugin README**

  **Goal:** Add the skill to the Workflow Utilities table and bump the skill count so README + manifest stay consistent.

  **Requirements:** R6.

  **Dependencies:** Unit 1 complete (the SKILL.md exists).

  **Files:**
  - Modify: `plugins/command-module/README.md`

  **Approach:**
  - Add a new row to the **Workflow Utilities** table (table starts at line 38):
    `| /here-or-there | Decide whether to continue inline or hand off; auto-routes to /handoff when a fresh conversation will help |`
  - Place the row near `/handoff` once /handoff lands (the natural pairing). If `/handoff` is already in the table by merge time, place /here-or-there immediately after.
  - Bump the **Skills** count in the Components table (line 9-10) by 1. **Do not hardcode the new value in this plan** — main is currently at 43, will be 44 once /handoff merges, and this skill bumps that by 1 to 45. The implementer should read the current count at merge time, not trust a stale arithmetic in this plan.
  - Do not modify `plugin.json` or `marketplace.json` (release-owned per AGENTS.md and plugin-level AGENTS.md).

  **Patterns to follow:**
  - The /handoff PR (commit `a51523a`) registered itself the same way: one new row, count bump, no manifest changes.

  **Test scenarios:**
  - The new row renders correctly as a markdown table cell (no broken pipe alignment).
  - The Skills count in the Components table matches the actual number of skills under `plugins/command-module/skills/` after this change.

  **Verification:**
  - README diff is exactly: one new row in Workflow Utilities + one numeric bump in the Components table. No other lines touched.

- [ ] **Unit 3: Validate plugin manifest consistency**

  **Goal:** Confirm README, plugin.json description, and marketplace.json remain consistent after the additions.

  **Requirements:** R7.

  **Dependencies:** Units 1 and 2 complete.

  **Files:**
  - Touch: none. This is a validation step.

  **Approach:**
  - Run the repo's release validation entry point (per repo-root AGENTS.md "Plugin Maintenance"): `bun run release:validate`.
  - If validation flags discrepancies (e.g., a count mismatch the README bump didn't catch, or a description that needs updating), fix the discrepancy in the appropriate file. Do not paper over by hand-editing release-owned fields — if release validation surfaces a release-owned field issue, that's a separate fix path.

  **Verification:**
  - `bun run release:validate` exits clean.
  - `cat plugins/command-module/.claude-plugin/plugin.json | jq .` and `cat .claude-plugin/marketplace.json | jq .` both parse cleanly.

## System-Wide Impact

- **Interaction graph:** `/here-or-there` is a leaf-shaped consumer with one downstream callee — `/handoff` — invoked only on the `there` branch. No callers (it's a manual user-facing skill in v1). Future callers (per /handoff plan: `/brainstorm`, `/implementation-plan`, `/ideate` handoff phases) are out of scope.
- **Error propagation:** Two failure surfaces:
  1. **Inference failure (cannot derive topic/next-action despite `there` recommendation).** Handled at the skill layer: fall back to `here` with rationale, do NOT invoke /handoff with garbage args.
  2. **`/handoff` invocation failure (write error, missing repo root, etc.).** /handoff already surfaces these (per its SKILL.md Phase 2 error handling). /here-or-there does nothing extra — the user sees /handoff's error verbatim.
- **State lifecycle risks:** None — the skill is stateless. No files written in the `here` branch. The `there` branch writes one file via /handoff (which already handles its own write semantics, including filename collisions).
- **API surface parity:** None affected. /here-or-there does not change /handoff's contract. /handoff already gates Phase 1.5 on `$ARGUMENTS` presence — that's the integration point.
- **Integration coverage:** The /here-or-there → /handoff handoff is the one cross-skill path. No automated integration test (the repo's test suite covers converters/writers, not skill behavior). Manual verification via the six scenarios in Unit 1.

## Risks & Dependencies

- **HARD DEPENDENCY: `/handoff` must be on `main` before this plan executes.** /handoff is currently on the unmerged `feat/handoff-skill` branch (commit `a51523a`). Building /here-or-there before /handoff merges would either:
  - Land /here-or-there with a dangling reference to a non-existent skill, or
  - Force /here-or-there to wait in its own branch until /handoff merges.
  - **Mitigation:** Confirm /handoff is on `main` before starting Unit 1. If /handoff is delayed, this plan stays parked.
- **/handoff's contract may change before merge.** /handoff is on a feature branch and may receive review-driven edits — particularly to the Phase 1.5 gate logic or the `$ARGUMENTS` parsing rules. /here-or-there's auto-invoke contract relies on those exact behaviors.
  - **Mitigation:** When starting Unit 1, re-read /handoff's SKILL.md from `main` (not from cached memory of `feat/handoff-skill`) and re-confirm: (a) Phase 1.5 still gates on `$ARGUMENTS` presence; (b) the positional-args contract is `<topic> <rest-as-next-action>`; (c) the closing section still references /here-or-there as the canonical caller. If any of these have shifted, update Unit 1 before writing the SKILL.md.
- **Heuristic drift risk.** The five-signal set is informed reasoning, not measurement. Real conversations may show that one signal dominates the others (most likely #4, explicit transition language) and the others are noise. This is not a v1 blocker — the skill works directionally — but will need dogfooding pressure to tune.
  - **Mitigation:** None at the plan level. Captured as condition-triggered deferred work below.
- **Inference quality for topic/next-action.** /here-or-there inherits /handoff's inference reliability: garbage-in / garbage-out. /handoff's plan flagged this same concern. The fallback (decline to route on inference failure) keeps it bounded.
- **No automated tests for skill behavior.** The repo's test suite covers parsers/converters/writers; SKILL.md authoring is verified by manual scenario walk-through. This is consistent with how /handoff and /explain-pipeline shipped, but means regressions can land silently if the SKILL.md is later edited without re-running the scenarios.

## Documentation / Operational Notes

- No separate docs entry. The SKILL.md description (read by Claude Code, OpenCode, Codex, etc.) is the primary surface.
- README registration (Unit 2) is the only documentation update.
- No rollout plan, monitoring, or feature flag — this is an opt-in slash command. No existing user is affected unless they invoke it.

## Deferred Work

Captured per the planning workflow's three-flavor classification (Phase 3.7). Both items below are **same-repo, condition-triggered**:

- **Multi-destination routing (`/wrap-up` chain, etc.).** If dogfooding shows users frequently want `/wrap-up` before `/handoff`, or some other multi-step transition, expand the route Phase to support a small set of named chains. **Trigger condition:** three or more dogfooding observations or feature requests for multi-destination routing. **Where it lives:** capture as a follow-up task in the missioncontrol task tracker referencing this plan and T011.
- **Signal weighting / threshold tuning.** Once the skill has run on many real conversations, the five signals' relative strength will be learnable. The current "any 2 strong" rule is a starting point. **Trigger condition:** dogfooding evidence that the rule mis-recommends in either direction (false `there` for ongoing work, false `here` for clearly-bloated transitions). **Where it lives:** capture as a follow-up task in the missioncontrol task tracker, citing the specific mis-recommendations as evidence.

Both deferred items are surfaced here so the user can see them tracked. Neither blocks v1.

## Sources & References

- **Origin document:** `/Users/esther/prog/missioncontrol/tracking/command-module/tasks/T011.md` (full design decision, 2026-04-28 conversation, the three open implementation questions)
- **Direct precedent plan:** `docs/plans/2026-04-25-001-feat-handoff-skill-plan.md` (currently on `feat/handoff-skill`) — the symmetric partner skill
- **Downstream contract:** `plugins/command-module/skills/handoff/SKILL.md` (currently on `feat/handoff-skill`) — `$ARGUMENTS` contract, Phase 1.5 gate
- **Structural precedent:** `plugins/command-module/skills/whats-next/SKILL.md` (Phase 0/1/2 layout, transcript reading)
- **Plugin standards:** `plugins/command-module/AGENTS.md` Skill Compliance Checklist
- **Repo root standards:** `AGENTS.md` (commit conventions, scope labeling — this plan's commit will be `feat(here-or-there): ...`)
- **Institutional learnings:** `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`; `docs/solutions/skill-design/beta-skills-framework.md`
- **Related brainstorm (background, R1-R6 split context):** `docs/brainstorms/2026-04-06-next-skill-requirements.md`, `docs/brainstorms/2026-04-06-handoff-skill-requirements.md`
- **Related task entries:** T010 (/handoff, shipped on branch), T011 (this skill)
