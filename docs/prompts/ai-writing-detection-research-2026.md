# External research: what AI writing looks like now, and what detectors look for

You are running a research task in `/Users/esther/prog/command-module`. Work autonomously. This is research and analysis only, with one optional measurement pass; do not edit the reference files.

## Why this exists

The writing-style references were built in March 2026 and refreshed on 2026-08-27. That refresh was deliberately internal: it mined the user's own correction corpus (memory files, agent transcripts, git history) and used external sources only to corroborate what the corpus had already surfaced. The prior work is in `docs/research/2026-08-27-ai-writing-patterns-refresh.md` and `docs/brainstorms/writing-style-refresh-2026.md` on branch `feat/writing-style-refresh-2026`. **Read both before starting.** They tell you what is already covered so you do not spend the run rediscovering it.

The external leg was ten lookups, all model-agnostic and all corroborative. Nothing in the references comes from studying AI writing from the outside. This run fills that gap.

## What this is not

Not a banned-word hunt. The vocabulary lists in sections 1 of both reference files are the lowest-yield part of the whole system: a proof pass over six of the user's documents returned zero hits against them. Another list of words to avoid is worth nothing here. If a source's main contribution is a word list, note it and move on.

The interest is **sentence constructions and habits**: what shapes AI reaches for, what it does at the joints between clauses and between paragraphs, what rhythms it falls into, and what it does when told not to do something.

## Leg 1: what AI-detection algorithms actually look for

This is the leg with the most new information in it, because it uses a completely different taxonomy from any style guide.

Cover at minimum:

- **Perplexity-based detection.** How it works, what text properties drive it, and which of those a writer can act on.
- **Burstiness.** Variance in sentence length and in per-sentence predictability. Get the actual definitions used in the literature, not the blog-post version. This is the most directly actionable family, because it is a structural measure and the references already gesture at it ("vary sentence length deliberately") without ever making it concrete.
- **Curvature and sampling-discrepancy methods**: DetectGPT, Fast-DetectGPT, Binoculars, and whatever has superseded them. What text property are they exploiting, in plain terms?
- **Stylometric and n-gram features**: function-word distributions, POS-sequence patterns, punctuation ratios, sentence-opening variety.
- **Commercial detectors** (GPTZero, Originality.ai, Turnitin, Pangram, and any newer ones): what they publish about their feature sets, and where independent evaluations say they succeed and fail.
- **Watermarking**, briefly, and whether it is in play for any provider the user actually uses. Likely a footnote, but confirm rather than assume.

**The translation is the deliverable, not the survey.** For each detector-side feature, answer: what does a writer or an editing agent actually *do* differently because of it? A feature that cannot be turned into an instruction is worth one line. A feature that can is worth a worked example in both English and Dutch.

Be careful about one framing trap. The goal is not evading detection; it is that the properties detectors measure and the properties that make prose bad to read overlap heavily, and the detector literature has quantified that overlap in a way style guides have not. Where they diverge, say so plainly: some detector signals are artefacts of how sampling works and carry no writing-quality information at all. Those belong in the report as explicitly *not* actionable, so a later agent does not try to write around them.

## Leg 2: what has changed since roughly March 2026

Not "what do the newest models do" specifically. The question is what has shifted in the six months since the references were written, in either direction:

- Which March-era tells have been trained out, and is there evidence or just assertion?
- Which constructions have appeared or intensified? The user's own corpus shows one clearly: a deictic evaluative tail ("..., en daar zit het probleem", "..., and that's the point") rising from 0.015-0.065 to 0.346 per 1,000 words between May and late August 2026. Does anyone outside describe this?
- Has anything the references currently ban stopped being a real signal? A rule that is no longer earning its place is as useful a finding as a new rule.

Sources worth reaching for beyond general search: the tropes.fyi pattern directory (already partly mined, so look for what was missed), editors and copywriters who work with AI drafts daily, the AI-detection vendor blogs, academic work on LLM stylistic fingerprints, and anywhere people compare model families side by side on prose. Follow the sources those cite.

## Leg 3: the hypothesis worth testing

**Does suppressing one construction displace the impulse to another, and is fragmentation a response to burstiness pressure?**

The prior work established the first half within the user's own corpus: em-dash density in her documents fell 58% at the moment the rule was hardened to "never" on 2026-07-13, while over the following six weeks the evaluative tail rose five to eightfold, colon density rose 27%, and semicolon use collapsed. Freeburg, *The Last Fingerprint* (arXiv:2603.27006, 2026), reports the mechanism generally: suppressing a markdown device redirects the impulse rather than removing it.

The second half is untested. If models are being tuned toward higher burstiness because flat rhythm is the detector's main signal, then short punchy fragments are the cheapest available way to raise sentence-length variance. That would predict exactly the fragment-plus-stub pattern the user keeps catching, and it would mean the fragmentation is not laziness but an overcorrection with a traceable cause.

Look for external evidence either way. If it holds, it changes what the references should say: the fix is not "vary your sentence length" (which is the instruction that produces the problem) but something more specific about *where* variance is legitimate.

## Leg 4 (optional, run it if legs 1-3 leave room)

The user has roughly 200,000 words of dated Claude output in `~/.claude/projects/-Users-esther-prog-portfoliostrategyframework/`, plus the documents that output became in that repo's git history. That makes several of the Leg 1 features directly measurable rather than merely described. The obvious candidate is sentence-length variance, bucketed by month, so the trend has the same shape as the em-dash and evaluative-tail measurements in the prior research.

**A measurement needs a baseline, and choosing it badly makes the whole leg worthless.** Three things it must match: language, register, and human authorship.

**Do not use the user's chat messages as the baseline.** They are transcribed thinking rather than prose: fast, run-on, often ungrammatical, written to get a thought out. Their sentence-length variance would come out very high, which is what human writing looks like statistically, so the number would not be obviously wrong while measuring entirely the wrong thing. The disqualifier is register, not correctness.

**Primary baseline: publicly available human prose from before 2020**, matched on language and register. GPT-3 was released in mid-2020, so anything published before then is safely free of model output. Genre matching matters as much as the date, because burstiness differs sharply between literary essays and policy memos; comparing Dutch strategy documents against English journalism produces a meaningless figure. Candidates to check for bulk accessibility, in rough order of fit:

- Rijksoverheid publications and Kamerstukken from before 2020. Free, bulk-downloadable, and close to the register of the documents being measured.
- Dutch annual reports from before 2020, ideally from port, logistics or infrastructure companies, which is nearly the exact domain.
- SoNaR, the 500-million-word Dutch reference corpus held by the Instituut voor de Nederlandse Taal. A proper linguistic corpus, though it may require a licence; check before planning around it.

For English, prefer the burstiness figures already published in the detection literature over building a corpus, since English is the language where the metric is already characterised. Report which figures you used and on what genre they were computed.

**Secondary baseline: the user's own written prose**, which is scarcer but exactly matched on voice. Two known seams: the manual edits to the framework document between v0.50 and v0.51, which `user_writing_voice.md` in the orphaned `-Users-esther-prog-porfoliostrategyframework` memory directory was derived from, and a document she rewrote herself and pasted back in session `d059affc` on 2026-07-23 with the words "dit is wat ik tot nu toe heb herschreven". There may be more; look for passages she authored rather than edited.

The two baselines answer different questions. The public corpus answers "does this read as human writing in this genre", which is what the references need, since they serve agents writing for many audiences. Her own documents answer "does this read like Esther", which is a narrower and secondary check. Report them separately and do not average them.

**A prior attempt at this failed** and the reason is worth avoiding: line-joining artefacts in the git diff extraction inflated one period's mean sentence length to 61 words. Strip tables, code blocks, bullets, headings and front matter before splitting sentences, and sanity-check the distribution before reporting anything. If the extraction proves unreliable again, say so and drop the leg rather than reporting noisy figures.

## Standing research preferences

Comprehensive and detailed. No length or time caps. Do not impose a taxonomy in advance; if you find yourself assuming a structure, make it an open question instead. Find-all over top-N. Cite everything, with links. Where sources disagree, report the disagreement rather than picking a winner.

Both languages matter. Most of what you will find is English-language research about English text; check explicitly whether each finding is language-independent or an artefact of English, and flag anything that would need separate Dutch grounding.

## Output

One document: `docs/research/2026-XX-XX-ai-detection-and-construction-patterns.md`, dated the day it is written.

Structure it around what a writing agent should do differently, not around the sources. Sections roughly matching the legs above, plus:

- **A candidate rule list.** For each proposed rule: the construction, the evidence, whether it is language-independent, whether it is already covered by an existing rule in `skills/proof/references/writing-style-{en,nl}.md` (give the section number), and what the diagnostic test would be. The prior refresh established that a rule without a test does not survive contact with a new surface form, so a rule with no proposed test should be marked as such.
- **A "no longer earning its place" list**, if any rule in the current references has stopped being supported.
- **What you could not establish**, kept honest and specific.

Do not edit the reference files. Recommendations only. A follow-up session decides what to apply.

## Constraints

Repo conventions are in `AGENTS.md`. Never hard-wrap prose in markdown, one paragraph is one line. No `Co-Authored-By` lines. Work on a branch off `main`, not on `feat/prompt-research-skills`.

Note the irony risk and take it seriously: this document is itself prose the user will read. Run the revised references over your own output before finishing. No em dashes, and no evaluative tails.
