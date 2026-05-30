# Audience Research Brief — Template

The constant scaffolding for an audience deep-dive. The skill fills the four `<<FILL-IN>>` blocks from the user's inputs and emits (or runs) the result. Everything outside the FILL-IN blocks is segment-agnostic and should stay intact run-to-run. Pairs with `research-method.md` (the methodology backbone).

---

You are a market & audience researcher. Go wide, then deep — real depth, not a surface scan. The goal is to know this community well enough to **find them, talk to them in their own words, and sell to them**. Find real communities, real products they actually buy, real places they shop, and real people in their own words. Flag where evidence is solid vs. thin. Where you state a number (audience size, price, spend), source it.

> **Method.** Follow the Customer-Driven Playbook's *Customer* and *Problem* stages (see `research-method.md`). Three rules govern everything: (1) define the segment by **who they are and the job they hire things to do**, not by "people who would buy our thing"; (2) a stated desire is **not** a problem worth solving — trust pains people already spend **time or money** on, not ones they merely endorse; (3) run discovery **neutrally**, then test priors against it (never hunt to confirm them).

> **Source discovery FIRST (before hunting quotes).** Work out *where this segment's voice actually concentrates* — it varies enormously by audience. Some communities live on YouTube and its comment sections; some on niche forums or Facebook groups; some on Reddit or Discord; some in magazines, blog comment sections, marketplace/product reviews, or podcasts. Do a quick scout (overlaps with the Section B channel map — do it early), **rank the sources by how much real, quotable voice they hold for *this* segment**, and weight the buyer-voice safari toward the richest ones you can actually access. **Reddit is one candidate among many — sometimes central, often not.** Don't default to it; don't treat any single platform as the whole game. (Veins that tend to pay off: *first-person blogs* and *problem-topic* YouTube comment sections — regrets/cost/"shouldn't buy" — plus competitor/pricing pages for WTP. Glossy tour videos and magazine/news pieces tend to be low-yield for real buyer voice.)

> **Fetch & verify ladder.** **WebSearch = discovery only — never quote its summaries** (it will fabricate an unsourced "key theme"); use it to find URLs. Then **WebFetch** static prose for candidate quotes (its output is a summarizing model's paraphrase — a lead, not proof). Then **a real browser** (raw page text = ground truth) to byte-verify every quote and to mine JS-rendered content (YouTube/WordPress comments). Reddit, if used, comes last and needs a logged-in browser / VPN / OAuth — not curl. A blocked platform is a coverage note, not a stall.

> ## NON-NEGOTIABLE sourcing standard (read first)
>
> Traceability is a pass/fail bar on the whole report, not a nice-to-have.
>
> 1. **Every single quote gets its own direct deep link** — a URL that opens the *exact* page where that quote lives, so the reader can click it and read the surrounding context. Not the platform, not the board, not the thread root — the specific item. This rule is **platform-agnostic**: it applies wherever the voice lives; only the verification *tactic* varies by platform:
>    - **Forums / blogs / magazine & news sites / marketplace reviews:** deep link to the specific post or comment anchor (`#post12345`), not the index page.
>    - **YouTube:** link to the video, plus — for a spoken quote — a timestamped URL (`&t=412s`); for a comment, the comment permalink if retrievable.
>    - **Reddit / Facebook / Discord / Instagram / TikTok:** permalink to the exact comment/post (for Reddit, the `…/comments/<thread>/<slug>/<comment_id>/` form; appending `.json` to verify liveness is one handy tactic). Reddit is **just one source among many — not the centre of gravity.**
> 2. **No single source is load-bearing.** If a platform is unreachable (bot-blocked, IP-blocked, paywalled, host-refused) or simply isn't where this segment talks, that's a *coverage note*, not a reason to stall — say so, and route to the sources you *can* verify. What's non-negotiable is the **verification**, not any one platform.
> 3. **No quote without a working link.** If you cannot produce a direct, openable URL, do not include the quote — or, if it is too good to drop, list it in a clearly separated `UNLINKED — do not rely` bucket. Never let an unlinked quote sit in the main quote bank.
> 4. **Never fabricate, paraphrase-as-quote, or reconstruct from memory.** Every quote must be a verbatim string that actually exists at the URL given. If synthesizing a theme rather than quoting, say "paraphrase" explicitly.
> 5. **Verify verbatim against the RAW page — extractors paraphrase and stitch.** WebFetch and reader proxies interpose a small summarizing model that can silently reword a quote or splice two fragments into one (watch ellipsis-joined or multi-clause quotes especially). Their output is a *lead, not proof*. Before any quote enters the bank or the database, confirm a distinctive substring of it appears in the **raw page text** (a real browser / raw HTML is the truth source), and confirm it is a single contiguous utterance unless you explicitly mark it as joined. Set `verbatim_verified: true` only after this check.
> 6. **Each quote carries metadata:** verbatim text · `verbatim_verified` · handle/username · community/platform · **direct URL** · date (if available) · one line of context. (These map 1:1 to the quote-database row schema below.)

---

## <<FILL-IN 1 — What we make / sell (constant context for this project)>>
A short description of the company/product cluster, its principles, materials, and business model. (What we might offer this segment.)

## <<FILL-IN 2 — The segment under study>>
Who this audience is, in one crisp paragraph. Identity-level, not "people who would buy our thing."

## <<FILL-IN 3 — Hypotheses to test (priors — NOT findings to hunt for)>>
> **Method guard against confirmation bias.** These are things *we* currently believe. They are listed here, separately, so they do **not** leak into the neutral discovery in Sections B–D. **Run the discovery blind first**, then assess each hypothesis against what was independently found. For each, **actively look for evidence against it**, report which way the balance falls, and flag if it is only true of a loud subset. A disproved prior is as valuable as a confirmed one.

List the priors as numbered, specific, testable, customer-limitation-focused statements (see `research-method.md` §3). Mark any that are the least-tested / most product-flattering as "scrutinize hardest."

## <<FILL-IN 4 — Founder priors / domain knowledge (optional)>>
Any lived/insider knowledge of the segment to draw on — flagged as *context to verify with citable sources*, not as fact.

---

## Research questions

### A. Who they are (segment definition & sizing)
1. Define the segment crisply. What sub-tribes exist? Which are real buyers vs. dreamers?
2. **Size it.** How many, in the strongest markets? Growth trend? Cite estimates and flag rigor.
3. Demographics & psychographics: age, income, life stage, values, why they are in this segment. Distinct income/spend tiers?
4. **Jobs-to-be-done.** Forget our product: what *jobs* does this segment hire products/services/objects to do? State the dominant jobs in their terms — more stable and revealing than demographics, and where we later check whether existing solutions do the job badly.

### B. Where they congregate (the channel map — gold for marketing)
5. **Map every meaningful watering hole**, with links and a sense of size/activity: subreddits, Facebook groups, Discord, forums; YouTube channels & creators with real pull (names, subscriber counts, whether they do brand features); Instagram/TikTok/Pinterest hashtags & accounts; blogs, magazines, podcasts; offline events/expos/associations.
6. Which accept advertising, sponsorship, product placement, or affiliate deals? Which creators do paid features? (Concrete go-to-market surfaces.)
7. Who are the **influencers / tastemakers** whose endorsement moves this community, and how do they partner with brands?

### C. What they buy & where they shop (purchase behavior)
8. What do they actually *spend on* in the relevant category? Typical budget?
9. **Where do they shop?** Name the actual stores, sites, marketplaces. Where do they look *first* for a solution?
10. What brands already serve them? How do those price and position? What is missing or ugly in that market?
11. **Willingness to pay:** evidence of what they pay a premium for vs. where they are frugal. Distinct budget tiers? Quote real spending decisions.
12. Do they buy DIY/flat-pack/kit forms? How do they talk about effort/assembly?

### D. Their voice & their pains — the "audience safari"
A dedicated buyer-voice hunt for **this one segment only**. Apply the sourcing standard to **every** quote. These buckets are deliberately **neutral** — they ask *what is there*, not *find evidence of X*. Don't go in looking for a conclusion (priors are tested separately, after). Organize into four buckets; do **not** merge with any other segment's quotes:

13. **Pain points** — frustrations in their own words. Let pains surface on their own; don't lead. Report what is actually loud.
14. **Wants & desires** — what they wish existed, "I'd love a…", "if only someone made…".
15. **Current solutions & workarounds** — what they buy, DIY, or hack *today*, and the failure modes they admit. This is where competitive gaps surface — and where you separate real pains from nice-to-haves. **The problem-worth-solving test:** for each pain, how do they get around it today, how often does it bite, and how much **time or money** have they already spent solving it? Active, costly workarounds = real pain.
16. **Willingness to pay** — them talking about *money*: what they spend, frugal vs. splurge, reactions to prices, budget tiers. Weight evidence toward money actually spent, not enthusiasm expressed.

For each bucket return a **quote bank**: every entry = verbatim quote · handle · platform · **direct URL** · date · one-line context. **Traceability beats volume** — ten clickable quotes beat thirty unverifiable ones. **Stopping rule (saturation):** keep digging until new sources stop surprising you; don't pad to a quota, don't stop while new themes still appear.

17. **Native vocabulary & phrases** the community uses (for copy): the words *they* use, and words that mark a brand as an outsider. Tie each to at least one linked quote.
18. **Aesthetic / style preferences** (if relevant to the product): what dominates, and whether our style would land, clash, or intrigue. Be honest about mismatch; link examples.

### E. Fit, risks & go-to-market
19. **Best beachhead within the segment** — which sub-tribe first, and why.
20. **Product-fit read:** which offering has the sharpest need here? Any idea the research surfaces that we have not considered?
21. **Risks / reasons this segment underperforms:** small market? price sensitivity? style mismatch? "they just DIY it"? Name the real threats.
22. **Concrete go-to-market moves:** the 3–5 highest-leverage ways to reach and seed this community, ranked.

---

## Deliver as

A structured, cited report:
- **Segment profile** — who they are, sub-tribes, size estimate, demographics/psychographics, dominant jobs-to-be-done.
- **Channel map** — a table of communities/creators/events with links, size, and whether each is an ad/sponsorship/partnership surface. (The most actionable deliverable — make it rich.)
- **Purchase behavior** — what they buy, where they shop, what they pay, existing brands and the gaps.
- **Buyer-voice quote bank** — the four buckets from Section D, each as a table/list where **every row carries: verbatim quote · handle · platform · direct clickable URL · date · one-line context.** Anything not individually clickable goes in the `UNLINKED` bucket. Keep self-contained; don't blend segments.
- **Sensemaking synthesis** — cluster the quotes, count frequency (soft quant), surface tensions, and for each significant pain give a **problem-worth-solving verdict** (real / nice-to-have / unclear) grounded in time-and-money evidence.
- **Product-fit & beachhead recommendation** — which sub-tribe and which offering first.
- **Hypothesis scorecard** — for each prior in FILL-IN 3, a verdict (**confirmed / mixed / disconfirmed / insufficient evidence**) based on what the *neutral* discovery independently surfaced, with supporting and contradicting linked evidence. Be willing to mark a prior disconfirmed.
- **Risks** and **go-to-market moves** (ranked, specific).
- **Open questions** for the next pass.

Cite sources with links throughout. Quote real people. Be explicit about confidence (solid vs. thin) for each major claim; flag where a claim rests on a single source.

---

## Output & filing

Produce **both** — the report is the *read*, the database is the *record*:

1. **Prose report** — filed under `docs/strategy/research/audiences/<segment-slug>/`. Quote banks stay **per-segment** here; don't blend segments' narratives.
2. **Quote database (the durable store)** — append every **verified** quote as one JSON object per line to the project-wide `docs/strategy/research/audiences/quotes.jsonl` (create it if absent). This single file pools all segments, keyed by a `segment` field, so the raw data survives in structured form — far less is lost than in a prose distillation, and it's directly queryable for later analyses (cross-segment overlap, copy mining, WTP patterns).

**JSONL row schema** — one object per quote, **append-only** (never rewrite or reorder existing lines):

```json
{"segment":"<slug>","bucket":"pain|want|current_solution|willingness_to_pay|vocabulary|other","quote":"<verbatim>","verbatim_verified":true,"speaker":"<handle/name or anon>","platform":"<youtube-transcript|youtube-comment|forum|blog-post|blog-comment|reddit|facebook|review|magazine|...>","community":"<specific site/channel/subreddit>","url":"<direct deep link>","date":"<YYYY-MM-DD or null>","context":"<one line: what they were responding to>","captured":"<run date YYYY-MM-DD>","tags":[],"notes":"<caveats, e.g. 'single sentence, not stitched'>"}
```

- Only rows with `verbatim_verified: true` are trusted data. If you must store an unverified one, set it `false` and explain in `notes` (mirrors the `UNLINKED` bucket).
- The `segment` field is the cross-segment key — it is what later makes the pooled overlap analysis possible. Per-segment *reports* stay separate; the *database* is the one deliberately-pooled, segment-tagged store.

Then harvest the headline findings back into `docs/strategy/audiences.md` (the living segment reference), promoting the segment's confidence tag where evidence supports it — and downgrading any prior the research disproves.
