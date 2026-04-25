---
title: "LLM writers hallucinate by interpolation -- prevention is hard, mechanical detection is cheap"
problem_type: best_practice
component: skills
root_cause: llm_writers_interpolate_general_knowledge_into_specific_claims
resolution_type: workflow_improvement
severity: medium
tags: [skill-design, implementation-plan, document-review, hallucination-prevention, llm-writing]
date: 2026-04-25
---

## Problem

LLM writers do not hallucinate by making things up from nothing. They hallucinate by *interpolating* from general knowledge into specific-sounding claims, without cross-referencing the specific context they are writing about.

A planner asked to write an implementation plan for "Bayesian forecast confidence intervals" pulls from its training: it knows PyMC, Stan, NumPyro are common Bayesian libraries; it knows the canonical pattern is "fit a model, sample posterior, summarize". Without grounding discipline, those become specifics in the plan: "extend the existing PyMC integration", "add a posterior sampler", "verify trace convergence". The general knowledge is correct. The specifics are fabricated -- the codebase actually uses `scipy.optimize.curve_fit` and has no Bayesian framework at all.

This is qualitatively different from the failure mode where an LLM invents a plausible-sounding library that doesn't exist. The libraries the planner names *do* exist; they are just not in *this codebase*. Because the names are real and the patterns are correct in general, the resulting prose reads convincingly. Reviewers and users often miss it on first read.

## Symptoms

- Plans that confidently name technologies, file paths, function names, or imports that aren't in the target codebase
- The interpolation is *adjacent* to truth: the named library is a sensible choice for the problem class, the file path follows project naming conventions, the function name reads like something the codebase would have
- Reviewer passes that miss the issue because the prose is internally coherent (the plan talks about PyMC consistently throughout, so a coherence reviewer sees no contradictions)
- Users discovering the mismatch only when they start implementing and the imports fail
- "Wait, do we even use PyMC?" moments mid-review
- The author re-reading their own plan after the fact and not being able to remember why a specific library was named -- because they didn't *choose* it, the LLM interpolated it from general knowledge

## What Didn't Work

**Just providing more context to the writer** -- having the planner read the repo before writing helps but doesn't fix the failure mode. The planner reads the repo, understands the broad shape, then writes the plan -- and during writing, the prose flows from general patterns more readily than from specific repo details. The repo context that was loaded doesn't always anchor every specific claim.

**Telling the writer "don't hallucinate"** -- the same suggestibility tax that affects reviewers (see companion doc on reviewer suggestibility) affects writers. A writer instructed to "be careful not to fabricate specifics" produces hedged prose ("we may extend the existing forecasting code") rather than concrete prose ("extend `src/forecast.py:fit_model`"). The plan becomes vaguer without becoming more accurate.

**Interleaved verification mid-write** -- prompting the writer to "verify each claim before writing it" produces stilted output. LLM writers are better at single-pass coherent prose than at interleaved write-verify loops. Verification mid-flow disrupts the writing model's ability to produce a coherent narrative, and the writer often verifies cosmetically (writing "I checked the codebase and..." without doing a real check) rather than substantively.

**Asking reviewers to catch it** -- works sometimes, but reviewers are also suggestible and tend to anchor on whatever the document says. Reviewer-side hallucination detection has a high false-positive rate (when prompted) or a high false-negative rate (when not prompted). It cannot be the only line of defense.

## Solution

Use a dual layer: a small prompt nudge during writing (cheap, partial prevention) plus mechanical verification after writing (cheap, reliable detection).

**Prompt nudge during writing:** When the writer is producing specific claims about external reality (technologies in use, file paths, function names, imports, existing patterns), instruct it to source those claims from what the repo-research phase actually surfaced -- not from general knowledge about similar problem domains. If the writer is tempted to write a claim it hasn't verified against read context, instruct it to either verify it or mark it explicitly as an assumption.

This is zero-token-cost in the sense that it lives in the skill prompt and applies to every invocation. It catches the easy cases -- the writer self-corrects when the discipline is salient. It doesn't catch every interpolation, because the writer's tendency to interpolate is a property of the model, not the prompt. But it shifts the distribution.

**Mechanical verification after writing:** A separate phase that extracts each specific code-level claim from the produced document and verifies it against the repo with deterministic search (grep, glob, file-read). The verification has no suggestibility surface -- it isn't asking an LLM "is this hallucinated", it's running grep and reporting matches.

This catches the cases the prompt nudge missed. Because it runs after writing is complete, it doesn't disrupt the writer's coherent prose. Because it's mechanical, it has near-zero false-positive rate on the categories it can verify (file paths, library names, function names, imports). The categories it cannot verify (abstract claims about patterns) get marked inconclusive rather than reported as findings.

**In `command-module`:** the planning skill (`implementation-plan`) carries the prompt nudge during plan-writing. The review skill (`document-review`) runs the `grounding-check` agent on plan documents in Phase 2, mechanically verifying code-level claims and surfacing ungrounded ones before persona reviewers anchor on them.

## Why detection is often cheaper than prevention for LLM writers

LLMs are good at single-pass coherent writing. They are less good at interleaved verification mid-flow. Interleaved verification produces three problems: stilted prose, cosmetic-only verification (writing "I checked..." without checking), and disruption of the writing model's coherence.

Mechanical verification *after* writing avoids all three. The writer produces coherent prose in a single pass; the verifier takes the finished prose and mechanically checks the parts that can be checked. The cost of the verifier is small (one extra agent run, no token cost on the writer side), and the writer's output quality stays high.

Prevention is still worth doing for the partial reduction it provides -- the prompt nudge is cheap and shifts the distribution. But the verifier is where the reliable signal comes from.

This is the inverse of the usual "prevention is cheaper than cure" intuition, and it holds specifically because LLM writers have a well-behaved single-pass mode and a poorly-behaved interleaved mode. The verifier separates the writing concern from the grounding concern, which lets each be optimized independently.

## Why interpolation is the right mental model

Calling this "hallucination" loses information. Hallucination suggests the writer is making things up -- but the writer isn't inventing PyMC, PyMC exists. The failure is interpolation: filling in a specific blank from a generic pattern, without confirming the specific value matches the specific context.

Recognizing it as interpolation has design implications:

- The wrong specifics tend to be *plausible* specifics, not absurd ones. They follow from the problem class. This is why reviewers miss them on first read -- the prose is coherent and the specifics fit the domain.
- The fix is not "make the writer more careful" but "verify the specifics that interpolation could have filled in". Mechanical verification targets exactly the slots interpolation tends to fill: library names, file paths, function names, imports.
- The writer's job and the verifier's job are different. The writer produces fluent prose. The verifier checks that the specific anchors are real. Asking one model to do both interleaved produces both worse prose and worse verification.

## Prevention

For any skill where an LLM produces specific claims about external reality (code, data, systems, configurations):

1. **Add a prompt nudge during writing** -- when producing specific claims, source from read context, not general knowledge. Mark uncertain claims explicitly. This is partial prevention and that is fine.
2. **Add a mechanical verification phase after writing** -- extract specific claims, verify with deterministic search, surface ungrounded claims to the user before downstream consumers anchor on them.
3. **Don't ask the writer to interleave verification mid-flow** -- it produces worse prose and cosmetic-only verification.
4. **Don't ask the reviewer to catch hallucinations** -- reviewers are suggestible (see companion doc); pull verification out of the LLM judgement layer entirely.
5. **Treat interpolation slots as a design surface** -- the categories that interpolation tends to fabricate (library names, file paths, function names, imports, configuration keys, command names, API surfaces) are also the categories that can be verified mechanically. The same list defines the verifier's scope.

## Status

v1 -- pattern extracted from the revintel T029 plan incident (PyMC named in a scipy-only codebase, 2026-04-19) and the resulting `grounding-check` agent design (command-module 2026-04-25). The dual-layer approach (prompt nudge + mechanical verification) is the most distinctive piece. Iterate as the pattern is applied to other LLM-writer skills (brainstorm, code-generation, documentation generation).

## Related

- `docs/solutions/skill-design/reviewers-are-suggestible-keep-instructions-mechanical-2026-04-25.md` -- companion piece on the *reviewer* side; the same principle (move verification out of LLM judgement) applied to a different layer of the pipeline
- `plugins/command-module/agents/document-review/grounding-check.md` -- the agent that implements mechanical verification of code-level claims for plan documents
- `plugins/command-module/skills/implementation-plan/SKILL.md` -- the planning skill where the prompt nudge during plan-writing belongs (a future extension; the nudge has been described here but not yet wired into the skill itself)
- `plugins/command-module/agents/research/repo-research-analyst.md` -- the upstream agent whose output the planner is supposed to draw specifics from; the prompt nudge tells the writer to source from this output rather than from general knowledge
