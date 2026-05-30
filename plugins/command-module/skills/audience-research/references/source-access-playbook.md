# Source-Access Playbook — how to actually reach & verify buyer voice

Read this **before the safari**. It's the operational layer beneath the brief: which tool reaches which platform, how to get a stable deep link, how to byte-verify a quote, and what to never bother trying. Distilled from real audience-research runs (first: tiny-house, 2026-05-30) and filtered to `[universal]` findings; `[env-specific]` items are flagged as cautions, not rules.

> The project keeps a per-run **field-notes log** (`docs/strategy/research/audiences/SOURCE-ACCESS-FIELD-NOTES.md`) — append a dated section there each run so observations compound. This file is the distilled, stable guide.

## The fetch-&-verify ladder (default order)

1. **WebSearch — discovery only.** Build the URL list: first-person blogs, *problem-topic* videos, forums, competitor/pricing pages, festival/creator lists. **Never quote a WebSearch summary** — it will confidently fabricate an unsourced "key theme." It finds pages; it does not supply quotes.
2. **WebFetch — static blogs / articles / forums.** Fast and faithful for prose, *but* its output is a **small-model summary = a lead, not proof.** Prompt it strictly: "copy exact strings only; if you can't copy it exactly, skip it; say NONE if nothing." Produces candidate quotes.
3. **agent-browser (Chromium) — verify + mine JS pages.** `get text body` is ground truth: confirm every candidate quote is an **exact substring** of the raw page before it's trusted. Also the only way into JS-rendered content (YouTube comments, Disqus, WordPress comments) and the only source of stable comment **anchors**.
4. **Competitor pricing + marketplace reviews** (WebFetch) — the strongest *money-actually-spent* WTP evidence.
5. **Reddit LAST, and only if reachable** — via logged-in Chrome (`agent-browser --auto-connect`), a VPN/mobile IP, or the OAuth API. One probe; skip on block. Do **not** burn a long access odyssey here (see dead ends).

## Tool verdicts

- **WebFetch** — right tool for static article/blog/forum/competitor prose; fast, faithful. Fails: host-refuses `reddit.com`/`old.reddit.com`; 403s some Cloudflare/WAF sites (per-site). Output is a summary → always raw-verify before quoting.
- **agent-browser / Chromium** — the workhorse. Use whenever you need rendered DOM, JS content, byte-verification, or deep-link anchors. Headed/logged-in (`--auto-connect` to the user's Chrome) unlocks auth-walled sources. Fails: hard IP blocks, Cloudflare JS challenges, login walls.
- **curl + headers** — mostly useless for walled HTML (datacenter IPs + curl-ish UAs are widely blocked — even ordinary blogs 403 it while WebFetch succeeds). Fine only for a clean JSON/API endpoint.
- **Reader proxies (e.g. r.jina.ai), redlib/safereddit mirrors** — unreliable; the Reddit-mirror ecosystem is effectively dead (403/404/Cloudflare). Don't lean on them.

## Mini-recipes (the veins that work)

**Static blog/article quote** (cheapest, highest yield):
1. WebSearch the topic → URL. 2. WebFetch with the strict-verbatim prompt → candidates. 3. `agent-browser open <url> && wait --load networkidle && get text body`. 4. Confirm the quote is an **exact substring** of the raw body; to locate across apostrophe/whitespace drift, normalize *to find* (`'→' "→" –—→- \xa0→space`), then **store the byte-exact raw slice**. 5. Deep link = the article URL.

**YouTube comment quote** (rich for pains/WTP — pick *problem-topic* videos, not glossy tours):
1. `open watch?v=…` → `wait --load networkidle`. 2. `eval "document.querySelector('#comments').scrollIntoView({block:'start'})"` → `wait 3500` → loop `scroll down 1300; wait 1500` ~8×. 3. `eval` per `ytd-comment-thread-renderer`: author `#author-text`, text `#content-text`, permalink **`a[href*="lc="]`** (NOT `#published-time-text` — that's a span with empty href). 4. The eval return is a JSON-encoded string — **`json.loads` it twice**. 5. Deep link = `watch?v=…&lc=<id>`; raw DOM text is already verified.

**WordPress blog/forum comment**: browser `eval` over `li[id^="comment-"]` → grab `id` → deep link `url#comment-<id>`; verify by substring of `get text body`.

## Where the voice actually is (yield)

- **First-person blogs** ("one year later", "X sucks", "my furniture journey") = the cheap, high-yield vein. Lead here.
- **Problem-topic YouTube comments** (regrets / cost / "shouldn't buy") ≫ **tour-video comments** (near-all generic praise, ~zero pain/WTP signal). Don't mine tours.
- **Competitor / pricing / marketplace-review pages** = best hard WTP evidence (real money).
- **Magazines / news** = low yield for *dweller* voice (survey stats + journalist voice, not buyers).
- **Houzz / Reddit / Facebook / Discord / Instagram / TikTok** = walled (bot-wall, login, or IP). Expect to skip unless authed/unblocked.

## Gotchas

- **WebFetch returns a summary, not the page** — a lead, not proof. Byte-verify before quoting.
- **YouTube comments need `scrollIntoView('#comments')` to hydrate** — blind big scrolls overshoot the lazy-load trigger and yield 0 comments.
- **`agent-browser eval` double-encodes** its return as a JSON string — `json.loads` twice.
- **Exact-match must tolerate then preserve source quirks**: curly vs straight quotes, en/em dashes, non-breaking spaces (`\xa0`), double spaces. Normalize to *locate*, store the *byte-exact* slice so the saved quote equals the page.
- **Comment timestamps are relative + locale-bound** (e.g. "5 years ago", localized to the exit IP) → store `date: null` and note relative age.

## Dead ends — don't repeat

- curl / WebFetch / Jina / redlib mirrors against Reddit → all dead. One browser probe, then skip.
- WebFetch → `reddit.com`/`old.reddit.com` → host-refused (universal).
- Blind browser scroll for YouTube comments → 0 loaded (must `scrollIntoView('#comments')`).
- Quoting a WebSearch/WebFetch *summary* → fabrication hazard. Only raw-verified slices.
- Glossy tour-video comments → generic praise, no signal.

## `[env-specific]` cautions (verify per machine/network — do NOT treat as permanent)

- **Reddit was fully IP-blocked on the first run's machine** (curl, WebFetch, Jina, mirrors, *and* a real browser → "You've been blocked by network security"). That is a property of that IP, **not** a permanent truth about Reddit. On an unblocked/logged-in path Reddit is a rich source — try it (last) before assuming it's gone.
- Per-site WAF 403s (e.g. some Cloudflare blogs) and transient 500s are site/time-specific, not universal.

## Recommended future helper scripts (not yet built)

- A **self-verifying `quotes.jsonl` writer**: rejects any row whose `quote` isn't an exact substring of the cited raw source (makes `verbatim_verified` mechanical, not trust-based).
- A **reusable YouTube-comment extractor** (the `scrollIntoView` + `a[href*="lc="]` + double-`json.loads` recipe) as an `assets/` script.
