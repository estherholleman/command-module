---
title: "Reviewers are suggestible -- keep their instructions mechanical, do verification outside them"
problem_type: best_practice
component: skills
root_cause: instruction_shape_biases_llm_outputs
resolution_type: workflow_improvement
severity: medium
tags: [skill-design, document-review, reviewers, hallucination-prevention, persona-agents]
date: 2026-04-25
---

## Problem

LLM reviewers are suggestible. The shape of the instruction biases the shape of the output. Telling a reviewer to "look for hallucinations" produces hallucination-shaped findings whether or not the document actually hallucinates. Telling a reviewer to "challenge every assumption" produces challenge-shaped findings whether or not the assumptions deserve challenging. The reviewer is competent and well-calibrated within its frame, but the frame the prompt establishes is what produces the output distribution.

This becomes a real cost when reviewer instructions slip from "evaluate this specific class of issue" toward "be skeptical / find problems / look for X failure mode". Outputs trend toward the requested failure mode and away from a calibrated read of what the document actually says.

## Symptoms

- Reviewer findings that the user has to spend energy rebutting before realizing the underlying issue isn't real
- Reviewers flagging unusual-but-correct patterns as "likely bugs" because the prompt invited skepticism
- Adding a generic "watch for hallucinations" instruction to a persona and seeing its findings shift toward speculative phrasing ("the plan might assume X", "this seems to imply Y") rather than concrete document quotes
- Two reviewers given the same plan but different framings ("look for problems" vs "evaluate against your specific check list") producing very different finding rates and severity distributions
- The user re-reading the document after a reviewer pass to confirm the finding was actually grounded -- a sign of trust loss

## What Didn't Work

**Asking reviewers to self-police for hallucinations** -- adding lines like "before reporting a finding, verify the underlying claim is grounded" or "watch for fabricated specifics" to existing persona prompts. Two failure modes:

1. The reviewer isn't actually verifying anything mechanical; it's just adjusting its prose to *sound* like it verified. Findings come back with verification language but the same suggestibility surface underneath.
2. The verification instruction primes the reviewer to find hallucinations, so it surfaces speculative concerns it would otherwise have suppressed. False-positive rate goes up, not down.

**Generic "be more critical" / "challenge everything" wrappers** -- same root cause. The shape of the instruction shapes the output, regardless of the document's actual quality.

**Having a reviewer review another reviewer's findings for hallucinations** -- moves the suggestibility one layer up but doesn't solve it. The meta-reviewer is still an LLM with the same tendency to find what its prompt asks it to find.

## Solution

Keep persona reviewer instructions narrow and concrete. Do verification *outside* the reviewer, as a separate mechanical pass.

**Persona prompt rules:**

- Tell the reviewer the specific class of issue it owns, with concrete examples and confidence calibration. Do not tell it to "watch for problems" generically.
- Include a "What you don't flag" section that explicitly lists adjacent failure modes belonging to other reviewers. This narrows the frame and reduces drift.
- Keep severity / confidence floors visible -- they are the natural way to suppress speculative findings without inviting the reviewer to second-guess every claim.
- Do not add anti-hallucination, anti-fabrication, or be-skeptical clauses. They are suggestible amplifiers.

**Mechanical verification rules:**

- Run alongside persona reviewers but with separate downstream handling. Mechanical verification has no suggestibility surface -- it's deterministic search, not LLM judgement -- so it does not need (and should not get) the persona pipeline's deduplication, confidence-gating, or auto-fix routing.
- Surface its findings to the user as a distinct section, ahead of persona findings in the output. The document can then be corrected (or claims acknowledged) without persona findings dragging in fabricated anchors.
- Output structured "claim X was checked, found Y" results, not interpretive prose. The mechanical layer should look more like a test report than a review.

**In `command-module/document-review`:** the persona reviewers (coherence, feasibility, scope-guardian, etc.) each own a specific failure class. None of them are asked to look for hallucinations. The `grounding-check` agent dispatches in parallel with the personas (plan documents only) and does mechanical verification of code-level claims (file paths, function names, libraries, imports) using grep/glob/read. Its findings bypass the persona synthesis pipeline -- they are held aside and presented in their own "Grounding (mechanical)" section above the persona findings, so a "this file does not exist" verdict and a "this section is unclear" judgement are not collapsed together.

## Why This Works

Suggestibility is a property of the instruction shape, not the reviewer's competence. A well-calibrated reviewer with a narrow concrete prompt produces fewer false positives than the same model with a generic skepticism prompt. You don't fix suggestibility by adding more instructions to the same reviewer; you fix it by either narrowing the instruction or moving the work out of the LLM entirely.

Mechanical verification has no suggestibility surface because it isn't asking an LLM "is this hallucinated?" -- it's running grep and reporting matches. There is no prompt the search can over-respond to.

Doing verification *before* persona dispatch matters because the personas anchor on what they read. If a plan says "extend the existing PyMC integration" and PyMC isn't in the codebase, every downstream reviewer will silently treat PyMC as real and produce findings around it (feasibility flags integration risk; scope-guardian flags unnecessary abstraction over PyMC; coherence checks if the PyMC sections are consistent with each other). All of those findings are wasted work that the user has to wade through to find the real signal. Pulling the unverified claim out before reviewers see it removes the false anchor.

## Prevention

When designing or auditing a reviewer prompt:

1. **Read the verbs.** "Find", "look for", "check whether", "watch for" -- if the verb is generic and applies to a category instead of a concrete artifact, the prompt is suggestible. Replace with verbs that bind to specific outputs ("quote two contradicting passages", "list each priority tier and its size").
2. **Reject anti-hallucination clauses.** If the temptation is to add "verify each code claim before reporting", that is a signal the verification belongs in a separate mechanical pass, not inside the reviewer prompt.
3. **Test by inverting the document.** If a reviewer produces similar finding rates on two documents -- one carefully grounded, one with deliberately inserted hallucinations -- the reviewer is responding to its prompt shape, not the document. The fix is sharper prompt scope or external verification, not more reviewer cleverness.
4. **Layer mechanical checks before LLM judgement** when there is anything in the document that can be verified by deterministic search (file existence, symbol presence, library use, configuration keys, command names). Mechanical first, judgement second.
5. **Include "What you don't flag" sections** in persona prompts as a structural way to keep scope narrow. Listing what belongs to other reviewers anchors the reviewer in its own lane.

## Status

v1 -- pattern extracted from one project (T018 grounding-check design, command-module 2026-04-25). The principle generalizes to any review pipeline that combines mechanical verification with LLM judgement; the specific application here is plan-side hallucinations. Iterate as the pattern is applied to other review surfaces (code review, security review, etc).

## Related

- `docs/solutions/skill-design/llm-writers-hallucinate-by-interpolation-2026-04-25.md` -- companion piece on the *writer* side of the same problem; explains why LLM writers produce hallucination-shaped specifics and why post-hoc detection is often cheaper than mid-flow prevention
- `plugins/command-module/agents/document-review/grounding-check.md` -- the agent that implements mechanical verification for the document-review skill
- `plugins/command-module/skills/document-review/SKILL.md` -- adds grounding-check to the plan-only agent list; Phase 3 carves it out of synthesis; Phase 4 surfaces its findings under a separate Grounding (mechanical) heading
- `plugins/command-module/skills/document-review/references/subagent-template.md` -- persona dispatch template; note that it does not include any anti-hallucination clauses, which is intentional
