# Audience Research — Method Reference

The methodology backbone for `/audience-research`. Distilled from *The Customer-Driven Playbook* (Lowdermilk & Rich, O'Reilly 2017). The book's Hypothesis Progression Framework has four stages — Customer -> Problem -> Concept -> Feature — and audience research lives in the first two. This file captures those two stages' wisdom as reusable rules. Internalize these; do not dump them at the user as a checklist.

> Why this matters: the book's whole thesis is **don't fall in love with a solution and go hunting for a customer who wants it** (its Pontiac Aztek / Betamax failure cases). That is the same confirmation-bias trap audience research must avoid — and these are the tools for staying honest.

## 1. Separate "who they are" from "what problem they have"

Keep two things distinct:
- **Customer** = identity, motivation, and the job they are trying to do — independent of your product. Define the segment by who they **are**, not by "people who would buy our thing."
- **Problem** = the limitation getting in the way of that job.

A rich segment profile comes first; the frictions come second. Don't let the product define the audience.

## 2. Jobs-to-be-Done — segments hire things for a job

Christensen's Jobs Theory: *customers don't buy products, they hire them to do a job.* A person doesn't want a drill, they want a quarter-inch hole.

For any segment, ask: **what job do they hire a product/service/object to do?** Jobs are more stable and more revealing than demographics — two very different people can share a job. Frame the segment around its dominant jobs, then look for where current solutions do those jobs badly. That gap is the opportunity.

## 3. A great hypothesis (for the priors block)

Criteria for the priors handed to the researcher to test:
- **Focuses on the customer's limitation, not your own.** "Their context caps what they can do" (customer limitation), not "our product is good at X" (our feature).
- **Specific** — narrow enough to be wrong. Broad claims ("people want to save money") validate trivially and teach nothing.
- **Separates the person from the behavior** — define the segment by identity + motivation, then observe behavior; don't define them by the behavior you want (buying).
- **Testable and measurable** — name the signal that would confirm *or* break it.
- **An invalidated hypothesis is as valuable as a validated one.** Disproving a prior saves you from building the wrong thing. Reward disconfirmation; never reward-hack toward confirming a prior.

## 4. The single most useful test: is this a problem worth solving?

The book's sharpest lesson (the provider who said "I'll give you my wallet!" for a website he had never spent a cent trying to build): **a stated desire is not a problem worth solving.** People enthusiastically endorse ideas they would never pay for.

To tell a real pain from a nice-to-have, look for evidence they are **already investing** in solving it:
- **How do they get around it today?** (a real pain has workarounds)
- **How often** does it bite them?
- **How much time or money** have they already spent trying to solve it?

A pain with active, costly workarounds is real. A pain nobody has lifted a finger about is probably not worth building for, however loudly it is complained about.

## 5. Non-leading questions (and non-leading reading)

Most audience research mines existing public voice (forums, comments, reviews) rather than running interviews, but the same discipline governs how you read and, when you do reach out, ask:
- **Don't ask "what do you dislike about X?"** — it presumes dislike and manufactures complaints. Ask open: *"Tell me about the last time you [did the job]. What was that like?"*
- **The magic-wand question** (great for surfacing wants): *"If you could wave a magic wand and change anything about [the job] — possible or not — what would it be?"*
- Favor *"tell me about the last time..."* over *"do you usually..."* — concrete recent episodes beat generalized self-reports.

## 6. Sensemaking — what to DO with the quote bank

Collecting quotes is not insight. The loop is **tag -> cluster -> tension -> story**:
- **Tag** each quote: motivation / problem / job-to-be-done / workaround-tool / attribute.
- **Cluster** tags to find patterns and count frequency (*soft quant*: "8 of 11 independent sources mention X" is an actionable signal, even without statistical rigor).
- **Surface tensions** — e.g. wants high quality *and* low price *and* low effort. Two-by-two tension models communicate these well.
- **Tell the story** — a few verbatim quotes carry more weight with a decision-maker than a summary. *A direct customer quote can be worth ten thousand words.*

## 7. Saturation — when you have heard enough

Alvarez's rule: **you are done when sources stop surprising you** — when fresh posts/comments only repeat pains, motivations, and workarounds you have already captured. Use this as the stopping signal, not an arbitrary quote count. Don't pad to a quota; don't stop while new themes are still appearing.

---

## Quick map: book -> this skill

| Book stage / tool | Where it lives in `/audience-research` |
|---|---|
| Customer stage (identity, motivation, JTBD) | Section A of the brief; the segment profile |
| Problem stage (limitations, problems worth solving) | the pain + current-solutions + willingness-to-pay buckets |
| Hypothesis criteria | the priors / hypotheses-to-test block |
| Non-leading Discussion Guide | the neutral-discovery instruction |
| Sensemaking (tag/cluster/story) | the synthesis step of the deliverable |
| Concept and Feature stages | out of scope for audience research — relevant later when testing a specific product concept with a validated segment |
