# Document Review Output Template

Use this **exact format** when presenting synthesized review findings. Findings are grouped by severity, not by reviewer.

The output has two layers: a **Decision Summary** at the top (synthesized, decision-oriented) and **Detailed Findings** below (the tables, ground truth). The summary is the action layer; the tables are the verification layer. Always include both unless there are zero findings.

**IMPORTANT:** Use pipe-delimited markdown tables (`| col | col |`). Do NOT use ASCII box-drawing characters.

## Example

```markdown
## Document Review Results

**Document:** docs/plans/2026-03-15-feat-user-auth-plan.md
**Type:** plan
**Reviewers:** coherence, feasibility, security-lens, scope-guardian
- security-lens -- plan adds public API endpoint with auth flow
- scope-guardian -- plan has 15 requirements across 3 priority levels

Applied 3 auto-fixes. Batched 2 fixes for approval. 4 findings to consider (2 errors, 2 omissions).

### Decision Summary

**Decision A -- How should single sign-on coexist with the existing CSRF protection?**

The plan introduces SSO in Phase 2 but does not address the CSRF token regeneration that the auth middleware already performs. They both want control of the session at different points.

- **Option A1:** Have SSO bypass CSRF on the handoff endpoint only. Tradeoff: simpler implementation, but creates one endpoint with weaker protection.
- **Option A2:** Regenerate the CSRF token immediately after SSO handoff. Tradeoff: keeps protection uniform, but adds a round-trip and complicates the success state.
- **My recommendation:** Option A2 -- the security-lens and feasibility findings agree that bypassing CSRF on any public endpoint is hard to walk back later, and the round-trip cost is small.

*Drawn from: P0 #1, P1 #3*

**Decision B -- Should the plan keep the offline-support goal or drop it?**

Goal states "offline support" but the technical approach assumes persistent connectivity. The two cannot both be true.

- **Option B1:** Drop the offline-support goal. Tradeoff: scope shrinks, but advertised feature goes away.
- **Option B2:** Keep the goal and add a sync-and-replay design to the plan. Tradeoff: meets the original promise, but adds at least one new implementation unit and probably pushes the timeline.
- **My recommendation:** Option B1 -- coherence flagged this as P0 because the conflict is foundational, and no other section of the plan has the offline-support work scoped. Adding it now would be scope creep mid-plan.

*Drawn from: P0 #1 (coherence)*

**Mechanical fixes (no decisions needed, will apply if approved):**

- Add "update API rate-limit config" step to Unit 4 -- implied by Unit 3's rate-limit introduction
- Add auth token refresh to test scenarios -- required by Unit 2's token expiry handling

**What I need from you:**

1. Decide A: bypass CSRF on the SSO handoff endpoint or regenerate the token after handoff
2. Decide B: drop the offline-support goal or add a sync-and-replay design unit
3. Approve the 2 batched mechanical fixes (yes/no/select)
4. Pick a webhook rate-limit value (current plan does not specify -- see P2 #4)

*If anything in the decision summary seems off, the detailed findings below are the source of truth -- check them.*

---

### Detailed Findings

### Auto-fixes Applied

- Standardized "pipeline"/"workflow" terminology to "pipeline" throughout (coherence)
- Fixed cross-reference: Section 4 referenced "Section 3.2" which is actually "Section 3.1" (coherence)
- Updated unit count from "6 units" to "7 units" to match listed units (coherence)

### Batch Confirm

These fixes have one clear correct answer but touch document meaning. Apply all?

| # | Section | Fix | Reviewer |
|---|---------|-----|----------|
| 1 | Unit 4 | Add "update API rate-limit config" step -- implied by Unit 3's rate-limit introduction | feasibility |
| 2 | Verification | Add auth token refresh to test scenarios -- required by Unit 2's token expiry handling | security-lens |

### P0 -- Must Fix

#### Errors

| # | Section | Issue | Reviewer | Confidence |
|---|---------|-------|----------|------------|
| 1 | Requirements Trace | Goal states "offline support" but technical approach assumes persistent connectivity | coherence | 0.92 |

### P1 -- Should Fix

#### Errors

| # | Section | Issue | Reviewer | Confidence |
|---|---------|-------|----------|------------|
| 2 | Scope Boundaries | 8 of 12 units build admin infrastructure; only 2 touch stated goal | scope-guardian | 0.80 |

#### Omissions

| # | Section | Issue | Reviewer | Confidence |
|---|---------|-------|----------|------------|
| 3 | Implementation Unit 3 | Plan proposes custom auth but does not mention existing Devise setup or migration path | feasibility | 0.85 |

### P2 -- Consider Fixing

#### Omissions

| # | Section | Issue | Reviewer | Confidence |
|---|---------|-------|----------|------------|
| 4 | API Design | Public webhook endpoint has no rate limiting mentioned | security-lens | 0.75 |

### Residual Concerns

| # | Concern | Source |
|---|---------|--------|
| 1 | Migration rollback strategy not addressed for Phase 2 data changes | feasibility |

### Deferred Questions

| # | Question | Source |
|---|---------|--------|
| 1 | Should the API use versioned endpoints from launch? | feasibility, security-lens |

### Coverage

| Persona | Status | Findings | Auto | Batch | Present | Residual |
|---------|--------|----------|------|-------|---------|----------|
| coherence | completed | 3 | 2 | 0 | 1 | 0 |
| feasibility | completed | 2 | 0 | 1 | 1 | 1 |
| security-lens | completed | 2 | 0 | 1 | 1 | 0 |
| scope-guardian | completed | 1 | 0 | 0 | 1 | 0 |
| product-lens | not activated | -- | -- | -- | -- | -- |
| design-lens | not activated | -- | -- | -- | -- | -- |
```

## Section Rules

- **Summary line**: Always present after the reviewer list. Format: "Applied N auto-fixes. Batched M fixes for approval. K findings to consider (X errors, Y omissions)." Omit any zero clause.
- **Decision Summary**: Sits above Detailed Findings. Always include unless there are zero findings of any class. Contains, in order: one or more `**Decision X -- ...**` blocks (plain-English framing, options with tradeoffs, recommendation, source citation), a `**Mechanical fixes**` list (one line per item), a `**What I need from you**` numbered list, and the closing disclaimer pointing to the detailed findings as ground truth. See SKILL.md Phase 3.8 for synthesis rules. Omit individual sub-blocks that are empty (e.g., if there are no real decisions, omit the `Decision X` blocks but keep mechanical fixes and the user-actions list).
- **Detailed Findings**: A `### Detailed Findings` heading separates the synthesized layer above from the ground-truth tables below. The sections below are the existing tables, in order:
- **Auto-fixes Applied**: List fixes that were applied automatically (auto class). Omit section if none.
- **Batch Confirm**: Group `batch_confirm` findings for a single yes/no/select approval. Omit section if none.
- **P0-P3 sections**: Only include sections that have findings. Omit empty severity levels. Within each severity, separate into **Errors** and **Omissions** sub-headers. Omit a sub-header if that severity has none of that type.
- **Residual Concerns**: Findings below confidence threshold that were promoted by cross-persona corroboration, plus unpromoted residual risks. Omit if none.
- **Deferred Questions**: Questions for later workflow stages. Omit if none.
- **Coverage**: Always include. Shows which personas ran and their output counts broken down by route (Auto, Batch, Present).
