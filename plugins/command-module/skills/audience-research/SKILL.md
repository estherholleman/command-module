---
name: audience-research
description: "Deep, citable research on a customer/audience segment for a product or startup idea -- who they are, the job they hire things to do, where they congregate online, what they buy and where, their pains in their own words, and willingness to pay. Use when the user says 'research this audience', 'audience research', 'who is the customer for X', 'profile this segment', 'find where these people hang out', 'validate this target market', or wants buyer-voice quotes with real sources. Produces a cited report and harvests it into a living audiences doc."
argument-hint: "[segment to research, e.g. 'tiny house community']"
---

# Audience Research

A deep-dive on one audience segment that comes back knowing them well enough to **find them, talk to them in their own words, and sell to them**. The output is a cited report (channel map, purchase behavior, a traceable buyer-voice quote bank, and an honest hypothesis scorecard) plus an update to the project's living `docs/strategy/audiences.md`.

> **STATUS: v0 (draft).** This skill's *scaffolding and reference files are stable*, but its execution flow has not yet been hardened against a live run. Treat the flow below as a strong first draft. After the first real run, revisit the **Open questions** at the bottom. (Skills are living — update freely.)

## Core Principles

1. **Traceability is pass/fail.** Every buyer quote gets its own direct, clickable deep link to the exact comment/post/timestamp, verified live. Never fabricate or paraphrase-as-quote. Verify the verbatim text against the **raw page** -- extractor tools (WebFetch, reader proxies) interpose a small model that can reword or stitch fragments, so their output is a lead, not proof. This is the single most important constraint -- see `references/brief-template.md`.
2. **Discover neutrally, then test priors.** Run the discovery buckets blind first; only afterward score the hypotheses against what was independently found, actively seeking disconfirming evidence. Never hunt to confirm a prior. A disproved prior is a win.
3. **Define by identity + job, not by "who'd buy."** Frame the segment around who they *are* and the job they hire things to do (Jobs-to-be-Done), not around the product.
4. **Desire is not a problem worth solving.** Trust pains people already spend time or money on, not ones they merely endorse.
5. **One segment per run, kept separate.** Per-segment *reports* stay separate (don't blend narratives); cross-segment overlap is its own later step.
6. **Persist to the database, not just the report.** Every verified quote is appended (with its `segment`) to the project-wide `docs/strategy/research/audiences/quotes.jsonl` -- the durable, queryable, append-only store across all segments. The prose report is the read; the database is the record. (This pooled-but-segment-tagged store is what *enables* the cross-segment overlap pass.)

## Support Files

Read on-demand at the step that needs them; do not bulk-load at skill start. When running the research via subagents, pass the relevant file contents into the task prompt.

- `references/brief-template.md` -- the constant research-brief scaffolding (sourcing standard, four FILL-IN blocks, Sections A-E, deliverable). The skill fills this.
- `references/research-method.md` -- the methodology backbone (Jobs-to-be-Done, problems-worth-solving test, hypothesis criteria, non-leading questions, sensemaking, saturation), distilled from *The Customer-Driven Playbook*. Internalize it; do not dump it as a checklist.

## Execution Flow

### Phase 0: Ground

**Load project context (for FILL-IN 1):**
- If `docs/strategy/audiences.md` exists, read it -- the segment may already be listed (often as a `hypothesis`) with priors worth pre-filling.
- If `docs/strategy/context.md` or a vision/strategy doc exists, skim it for the company/product context that fills FILL-IN 1.

**Gather the four inputs** (the only per-segment variation). Pre-fill from the docs above where possible and ask the user to confirm/extend, using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini; otherwise ask in chat and wait):
1. **Segment** -- who, identity-level (use the argument if provided).
2. **What we'd sell them** -- the offering/cluster context.
3. **Hypotheses to test** -- our priors (specific, testable, customer-limitation-focused; see `research-method.md` §3). Flag the least-tested / most product-flattering one to scrutinize hardest.
4. **Founder priors / domain knowledge** (optional) -- lived insight to verify, not assume.

### Phase 1: Assemble the brief

Read `references/brief-template.md` and fill the four `<<FILL-IN>>` blocks from Phase 0. Read `references/research-method.md` and internalize the method. The result is a complete, segment-specific brief.

**Choose run mode** (ask the user):
- **(a) Run now, in this agent** -- *recommended when the agent can fetch web pages and hit Reddit JSON endpoints* (e.g. Claude Code). Local fetch verifies per-quote links and catches fabrication far better than a web deep-research agent, which is weakest at exactly the traceability this brief demands.
- **(b) Emit only** -- write the filled brief to `docs/prompts/YYYY-MM-DD-audience-research-<segment-slug>.md` and hand the user a short starter prompt to run it in a fresh conversation (or paste into a web deep-research tool). Then stop.

### Phase 2: Run the research (if mode (a))

Execute the brief with discipline:
- **Source discovery first.** Before hunting quotes, work out where *this* segment's voice actually concentrates (YouTube, niche forums, FB groups, Reddit, Discord, magazines, blog comments, marketplace reviews...) and rank sources by quotable voice for this segment. Weight the safari toward the richest ones you can access. **No single source is load-bearing** -- if one platform is blocked or thin, note it and route to the others; only the verification standard is non-negotiable, not any one platform (a blocked Reddit is not a blocked report).
- **Neutral discovery** (Sections A-D). Mine the real communities. For each buyer quote, fetch the exact page and **verify the link is live** (platform-agnostic; for Reddit, appending `.json` to the permalink is one tactic). Apply the saturation stopping rule.
- Keep the four discovery buckets (pain · wants · current solutions · willingness to pay) neutral -- do not steer toward the priors.
- **Then** score the FILL-IN 3 hypotheses against what discovery independently surfaced, seeking disconfirming evidence.
- For wide sweeps (channel map, sizing), web search/fetch is fine; for buyer voice, exact-page fetch + verification is mandatory.

### Phase 3: Synthesize & file

Don't just dump the quote bank -- make sense of it (`research-method.md` §6): tag -> cluster -> count frequency (soft quant) -> surface tensions -> for each significant pain give a **problem-worth-solving verdict**. Assemble the full cited report per the brief's "Deliver as" section. Write it to `docs/strategy/research/audiences/<segment-slug>/` (create dirs as needed).

**Also persist the data:** append every verified quote (with its `segment`) as a JSONL row to `docs/strategy/research/audiences/quotes.jsonl` per the schema in `references/brief-template.md` -- append-only, never rewrite existing lines. This is the durable cross-segment record; the report is the read.

### Phase 4: Harvest into the living audiences doc

Offer to update `docs/strategy/audiences.md`:
- If it exists, propose specific edits to the segment's entry -- promote its confidence tag (`hypothesis` -> `validated`) where evidence supports, **downgrade any prior the research disproved**, and add the sharpest pains/channels/WTP findings.
- If it doesn't exist, offer to create it with this segment as the first entry.
- Present proposed changes; write only after the user approves.

### Closing

Summarize: which hypotheses held up vs. were disconfirmed, the sharpest real pains (with verdicts), the top 3-5 go-to-market channels, an honest fit read, and the report path. Note any segments worth researching next (for a future cross-segment overlap pass).

## Open questions (resolve after the first live run)

- **Run vs. emit default** -- does running in-agent reliably produce verified per-quote links at scale, or is emit-then-run-with-discipline the safer default?
- **Quote volume per bucket** -- what's the realistic saturation point before diminishing returns?
- **Subagent fan-out** -- should Sections A-E be split across parallel subagents (channel map / purchase / buyer-voice), or run single-threaded for quote-link discipline?
- **audiences.md schema** -- does the harvest step need a fixed per-segment template, or is prose fine?
