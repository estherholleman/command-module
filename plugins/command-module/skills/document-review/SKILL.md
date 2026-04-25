---
name: document-review
description: Review requirements or plan documents using parallel persona agents that surface role-specific issues. Use when a requirements document or plan document exists and the user wants to improve it.
---

# Document Review

Review requirements or plan documents through multi-persona analysis. Dispatches specialized reviewer agents in parallel, auto-fixes quality issues, and presents strategic questions for user decision.

## Phase 1: Get and Analyze Document

**If a document path is provided:** Read it, then proceed.

**If no document is specified:** Ask which document to review, or find the most recent in `docs/brainstorms/` or `docs/plans/` using a file-search/glob tool (e.g., Glob in Claude Code).

### Classify Document Type

After reading, classify the document:
- **requirements** -- from `docs/brainstorms/`, focuses on what to build and why
- **plan** -- from `docs/plans/`, focuses on how to build it with implementation details

### Select Conditional Personas

Analyze the document content to determine which conditional personas to activate. Check for these signals:

**product-lens** -- activate when the document contains:
- User-facing features, user stories, or customer-focused language
- Market claims, competitive positioning, or business justification
- Scope decisions, prioritization language, or priority tiers with feature assignments
- Requirements with user/customer/business outcome focus

**design-lens** -- activate when the document contains:
- UI/UX references, frontend components, or visual design language
- User flows, wireframes, screen/page/view mentions
- Interaction descriptions (forms, buttons, navigation, modals)
- References to responsive behavior or accessibility

**security-lens** -- activate when the document contains:
- Auth/authorization mentions, login flows, session management
- API endpoints exposed to external clients
- Data handling, PII, payments, tokens, credentials, encryption
- Third-party integrations with trust boundary implications

**scope-guardian** -- activate when the document contains:
- Multiple priority tiers (P0/P1/P2, must-have/should-have/nice-to-have)
- Large requirement count (>8 distinct requirements or implementation units)
- Stretch goals, nice-to-haves, or "future work" sections
- Scope boundary language that seems misaligned with stated goals
- Goals that don't clearly connect to requirements

**adversarial** -- activate when the document contains:
- More than 5 distinct requirements or implementation units
- Explicit architectural or scope decisions with stated rationale
- High-stakes domains (auth, payments, data migrations, external integrations)
- Proposals of new abstractions, frameworks, or significant architectural patterns

## Phase 2: Announce and Dispatch Personas

### Announce the Review Team

Tell the user which personas will review and why. For conditional personas, include the justification:

```
Reviewing with:
- coherence-reviewer (always-on)
- feasibility-reviewer (always-on)
- scope-guardian-reviewer -- plan has 12 requirements across 3 priority levels
- security-lens-reviewer -- plan adds API endpoints with auth flow
```

### Build Agent List

Always include:
- `command-module:document-review:coherence-reviewer`
- `command-module:document-review:feasibility-reviewer`

Add activated conditional personas:
- `command-module:document-review:product-lens-reviewer`
- `command-module:document-review:design-lens-reviewer`
- `command-module:document-review:security-lens-reviewer`
- `command-module:document-review:scope-guardian-reviewer`
- `command-module:document-review:adversarial-document-reviewer`

### Dispatch

Dispatch all agents in **parallel** using the platform's task/agent tool (e.g., Agent tool in Claude Code, spawn in Codex). Each agent receives the prompt built from the subagent template included below with these variables filled:

| Variable | Value |
|----------|-------|
| `{persona_file}` | Full content of the agent's markdown file |
| `{schema}` | Content of the findings schema included below |
| `{document_type}` | "requirements" or "plan" from Phase 1 classification |
| `{document_path}` | Path to the document |
| `{document_content}` | Full text of the document |

Pass each agent the **full document** -- do not split into sections.

**Error handling:** If an agent fails or times out, proceed with findings from agents that completed. Note the failed agent in the Coverage section. Do not block the entire review on a single agent failure.

**Dispatch limit:** Even at maximum (7 agents), use parallel dispatch. These are document reviewers with bounded scope reading a single document -- parallel is safe and fast.

## Phase 3: Synthesize Findings

Process findings from all agents through this pipeline. **Order matters** -- each step depends on the previous.

### 3.1 Validate

Check each agent's returned JSON against the findings schema included below:
- Drop findings missing any required field defined in the schema
- Drop findings with invalid enum values
- Note the agent name for any malformed output in the Coverage section

### 3.2 Confidence Gate

Suppress findings below 0.50 confidence. Store them as residual concerns for potential promotion in step 3.4.

### 3.3 Deduplicate

Fingerprint each finding using `normalize(section) + normalize(title)`. Normalization: lowercase, strip punctuation, collapse whitespace.

When fingerprints match across personas:
- If the findings recommend **opposing actions** (e.g., one says cut, the other says keep), do not merge -- preserve both for contradiction resolution in 3.5
- Otherwise merge: keep the highest severity, keep the highest confidence, union all evidence arrays, note all agreeing reviewers (e.g., "coherence, feasibility")

### 3.4 Promote Residual Concerns

Scan the residual concerns (findings suppressed in 3.2) for:
- **Cross-persona corroboration**: A residual concern from Persona A overlaps with an above-threshold finding from Persona B. Promote at P2 with confidence 0.55-0.65. Inherit `finding_type` from the corroborating above-threshold finding.
- **Concrete blocking risks**: A residual concern describes a specific, concrete risk that would block implementation. Promote at P2 with confidence 0.55. Set `finding_type: omission` (blocking risks surfaced as residual concerns are inherently about something the document failed to address).

### 3.5 Resolve Contradictions

When personas disagree on the same section:
- Create a **combined finding** presenting both perspectives
- Set `autofix_class: present`
- Set `finding_type: error` (contradictions are by definition about conflicting things the document says, not things it omits)
- Frame as a tradeoff, not a verdict

Specific conflict patterns:
- Coherence says "keep for consistency" + scope-guardian says "cut for simplicity" -> combined finding, let user decide
- Feasibility says "this is impossible" + product-lens says "this is essential" -> P1 finding framed as a tradeoff
- Multiple personas flag the same issue -> merge into single finding, note consensus, increase confidence

### 3.6 Route by Autofix Class

| Autofix Class | Route |
|---------------|-------|
| `auto` | Apply automatically -- local deterministic fix (terminology, formatting, cross-references, completeness corrections where the correct value is verifiable from the document itself) |
| `batch_confirm` | Group for single batch approval -- obvious fixes that touch meaning but have one clear correct answer |
| `present` | Present individually for user judgment |

Demote any `auto` finding that lacks a `suggested_fix` to `batch_confirm`. Demote any `batch_confirm` finding that lacks a `suggested_fix` to `present`.

**Completeness corrections eligible for `auto`:** A finding qualifies when the correct fix is deterministically derivable from other content in the document. Examples: a count says "6 units" but the document lists 7, a summary omits an item that appears in the detailed list, a cross-reference points to a renamed section. If the fix requires judgment about *what* to add (not just *that* something is missing), it belongs in `batch_confirm` or `present`.

### 3.7 Sort

Sort findings for presentation: P0 -> P1 -> P2 -> P3, then by finding type (errors before omissions), then by confidence (descending), then by document order (section position).

### 3.8 Synthesize Decision Summary

After sorting, synthesize the findings into a decision-oriented summary. This is an interpretive layer over the sorted findings -- the goal is to translate the raw output into "here is what you actually need to decide" so the user can act fast and only drill into the detailed tables when something looks off.

This synthesis runs in the orchestrator, not a sub-agent. All findings are already in context from the previous steps.

Skip this step entirely if there are zero findings of any class (auto, batch_confirm, present) and zero residual concerns. With nothing to synthesize, jump straight to Phase 4 with the standard "no issues found" output.

#### Bundle findings into decisions

Group findings that collapse into a single underlying decision. Multiple findings often arise from the same tension and should be presented as one decision rather than three separate items the user has to mentally merge.

Bundling signals:
- Two or more findings target the same section and recommend related changes
- Findings reference the same architectural choice, scope tier, or design tradeoff from different angles (e.g., feasibility flags it as risky, scope-guardian flags it as out-of-scope)
- A residual concern reinforces an above-threshold finding on the same topic
- A contradiction (combined finding from step 3.5) is by definition already a decision -- preserve it as one

Do not bundle findings that touch unrelated sections or address genuinely different concerns just because they have similar severity.

#### Separate real decisions from mechanical fixes

A **real decision** is one where reasonable people could disagree. Real decisions get full treatment: plain-English framing, options with tradeoffs, recommendation, citation back to source findings.

A **mechanical fix** has one obvious right answer and only needs user awareness or batch approval (e.g., "fix typo in Section 4", "update count from 6 to 7", "add missing cross-reference"). All `auto` and `batch_confirm` findings are mechanical by routing. A `present` finding can also be mechanical if reading it makes the right answer obvious.

Mechanical fixes appear as a single one-line-each list under "Mechanical fixes" -- do not generate options/tradeoffs/recommendations for them.

#### Translate jargon to plain English

Frame each decision the way the user would explain it to a non-expert stakeholder. Drop technical shorthand, internal naming, and persona labels. The detailed findings table preserves the technical specifics; the decision summary is the human-readable lens.

Example translation:
- Raw finding: "P1 error: Auth middleware CSRF token regeneration conflicts with Phase 2 SSO session handoff (feasibility, security-lens, conf 0.88)"
- Decision framing: "How should single sign-on coexist with the existing CSRF protection? They both want control of the session at different points, and the current plan does not say which wins."

#### Generate options with tradeoffs

For each real decision, list 2-3 options. Each option is a one-line description plus the tradeoff it accepts. Do not invent options the findings do not support -- stick to alternatives the reviewers raised or that follow directly from the document. If the findings only suggest one viable path, frame it as "do this, accepting tradeoff X" with one option rather than fabricating a contrast.

#### Recommend with one-sentence why

Pick one option (or an explicit hybrid) per decision. The recommendation must be backed by one sentence of reasoning grounded in the findings -- typically citing severity, confidence, cross-persona corroboration, or evidence weight. If no option clearly leads, say so explicitly: "No clear recommendation -- both options have legitimate tradeoffs. Lean Option X if Y matters more; lean Option Y otherwise."

#### Cite source findings

After each decision's recommendation, add a one-line citation pointing back to the detailed findings: `*Drawn from: P1 #2, P1 #3, P2 #5, residual #1*`. This lets the user verify quickly when a synthesized framing looks off.

#### Compose "what I need from you"

End the summary with a numbered list of explicit, concrete user actions:
- One item per real decision: "Decide A: keep admin work or cut Units 5-9"
- Plus any explicit user inputs the findings ask for (e.g., "Pick a webhook rate-limit value")
- If there are `batch_confirm` findings, include "Approve the M batched mechanical fixes (yes/no/select)" as an item -- this previews the batch_confirm prompt that runs in Phase 4

#### Disclaimer

Always close the Decision Summary with: `*If anything in the decision summary seems off, the detailed findings below are the source of truth -- check them.*`

This is non-optional. Synthesis is interpretive and can be wrong (miss findings, over-bundle, give a bad recommendation). The disclaimer keeps the user oriented to ground truth.

## Phase 4: Apply and Present

### Apply Auto-fixes

Apply all `auto` findings to the document in a **single pass**:
- Edit the document inline using the platform's edit tool
- Track what was changed for the "Auto-fixes Applied" section
- Do not ask for approval -- these are unambiguously correct

### Batch Confirm

If any `batch_confirm` findings exist, present them as a group for a single approval:
- List the proposed fixes in a numbered table
- Use the platform's blocking question tool (AskUserQuestion in Claude Code, request_user_input in Codex, ask_user in Gemini) to ask: "Apply these N fixes? (yes/no/select)". If no blocking question tool is available, present the table with numbered options and wait for the user's reply before proceeding.
- If approved, apply all in a single pass
- If "select", let the user pick which to apply
- If rejected, demote remaining to the `present` findings list

This turns N obvious-but-meaning-touching fixes into 1 interaction instead of N.

### Present Remaining Findings

Compose a single output block in this order:

1. **Brief summary line:** "Applied N auto-fixes. Batched M fixes for approval. K findings to consider (X errors, Y omissions)."
2. **Decision Summary** (from Phase 3.8) -- the synthesized decisions, mechanical fixes list, and "what I need from you" block. Skip this section only if Phase 3.8 was skipped (zero findings).
3. **Detailed Findings** -- the existing P0-P3 tables, separated within each severity by type:
   - **Errors** (design tensions, contradictions, incorrect statements) first -- these need resolution
   - **Omissions** (missing steps, absent details, forgotten entries) second -- these need additions
4. **Coverage table, auto-fixes applied, residual concerns, deferred questions.**

The Decision Summary sits above the Detailed Findings on purpose -- the user reads the synthesized layer to act, then drills into the tables only when something looks off. The detailed tables are not redundant -- they are the ground truth the synthesis is verified against.

Use the review output template included below for the full structure and exact section ordering.

### Protected Artifacts

During synthesis, discard any finding that recommends deleting or removing files in:
- `docs/brainstorms/`
- `docs/plans/`
- `docs/solutions/`

These are pipeline artifacts and must not be flagged for removal.

## Phase 5: Next Action

Use the platform's blocking question tool when available (AskUserQuestion in Claude Code, request_user_input in Codex, ask_user in Gemini). Otherwise present numbered options and wait for the user's reply.

Offer:

1. **Refine again** -- another review pass
2. **Review complete** -- document is ready

After 2 refinement passes, recommend completion -- diminishing returns are likely. But if the user wants to continue, allow it.

Return "Review complete" as the terminal signal for callers.

## What NOT to Do

- Do not rewrite the entire document
- Do not add new sections or requirements the user didn't discuss
- Do not over-engineer or add complexity
- Do not create separate review files or add metadata sections
- Do not modify any of the 2 caller skills (ce-brainstorm, ce-plan)

## Iteration Guidance

On subsequent passes, re-dispatch personas and re-synthesize. The auto-fix mechanism and confidence gating prevent the same findings from recurring once fixed. If findings are repetitive across passes, recommend completion.

---

## Included References

### Subagent Template

@./references/subagent-template.md

### Findings Schema

@./references/findings-schema.json

### Review Output Template

@./references/review-output-template.md
