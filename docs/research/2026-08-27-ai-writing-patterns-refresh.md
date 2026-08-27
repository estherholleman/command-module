# AI writing patterns: 2026 refresh research

**Date:** 2026-08-27
**Scope:** the four writing-guidance surfaces in `plugins/command-module/` (proof EN/NL references, writing-foundations, the writing-style-editor agent), English and Dutch equally.
**Companion:** the proposal and the distribution recommendation live in `docs/brainstorms/writing-style-refresh-2026.md`.

## What this was looking for

The Dutch reference has been amended eight times since it was created on 2026-03-28. Five of those amendments patch one underlying defect: a clause that asks the reader to supply a verb, a subject, or an unpacked noun. Each was written against the one surface form that had most recently annoyed the user. In August a sixth surface form got through anyway.

The question was therefore not "which words are missing from the lists" but "why is enumeration not converging, and what is the corpus actually full of."

---

## Leg A: the user's own correction corpus

### Extraction method, so a later pass can repeat it

**A0 (memory corpus).** `find /Users/esther/.claude/projects -path "*/memory/*.md"` returned 137 files across 12 project directories, 69 of them `type: feedback`. Every file's `description:` line was listed in one pass, the prose-relevant ones read in full. No tooling needed.

**A1 (transcripts).** 630MB of JSONL cannot be read into context, so extraction was scripted. The script is preserved at `/private/tmp/claude-501/.../scratchpad/legA/extract.py` and works as follows:

1. Stream each `*.jsonl` line by line; keep only records with `type` of `user` or `assistant`.
2. Reconstruct human-authored turns: `message.content` as a string, or the concatenated `text` blocks of a list. Drop anything with `isMeta` or `isSidechain`, and anything opening with a hook-feedback banner, `<command-name>`, `<system-reminder>`, `<task-notification>`, or a tool-result envelope. This filter matters: without the task-notification exclusion, 45 of 103 first-pass "hits" were agent output masquerading as user turns.
3. Match user turns against 58 correction markers (Dutch: `graag niet`, `graag weg`, `liever`, `opgebroken`, `spreektaal`, `niemand kent`, `steno`, `vermijd`, `herschrijf`, `schrijf dan eerder`, and others; English: `don't write`, `avoid`, `rewrite`, `reads like`, `too formal`, `nobody says`, `drop the`, `reword`, and others), then gate on a prose-domain regex so that corrections about code or process fall out.
4. Also match on *shape*: a user turn under 500 characters, following an assistant turn over 400 characters, containing a quotation mark. Anchor 1 has exactly this shape and no marker word.
5. Emit the matched user turn in full plus a window of the preceding and following assistant turns, so before/after pairs stay intact.

`pull.py` in the same directory retrieves one named turn with 2,200 characters of assistant text on either side.

**A2 (git).** Two measurements over `portfoliostrategyframework`, both on *added* lines only (`git log -p` filtered to `^+`), bucketed by period, normalised per 1,000 added words. Deletions are ignored, so these are flow approximations. Scripts at `/tmp/flow.py` and `/tmp/sent.py`.

### What the seams actually yielded

| seam | reviewed | usable | notes |
|------|----------|--------|-------|
| A0 memory | 137 files (69 feedback) | 24 prose rules | Highest precision per unit of effort. A prior pass at this exact task, done incrementally and never consolidated. |
| A1 transcripts | 476 human user turns across 41 PSF sessions | 21 correction messages | 58 marker hits, 21 survived reading. |
| A1 secondary | 36 portbase + 4 systems-blog + 5 command-module turns | 3 | See the availability problem below. |
| A2 git | 6 periods, ~2.4M added words | 4 measurements | Used for the em-dash verdict, not for rules. |

**Total: 46 extracted rules and before/after pairs. EN/NL split: 6 EN, 40 NL.**

That split is a property of the archive, not of the user. Only `portfoliostrategyframework` (630MB, 41 sessions) and `portbase` (59MB, 7 sessions) still hold substantial transcripts. The `revintel` and `europeansleeper` project directories the task named as secondary sources contain **only** memory files now, 44KB and 64KB respectively, with zero `.jsonl` files. Their transcripts have been pruned. Since revintel holds the explainers written for Norbert and Wolter, the single richest vein of externally-facing English-adjacent prose corrections is gone. English correction markers were searched with the same 29-marker list and the same effort as Dutch; they returned almost nothing because the sessions that would have contained them no longer exist. `systems-blog` was searched despite the task's instruction to skip it, precisely because it is the one remaining English prose repo; it holds 3 sessions and yielded one usable item.

Report the 6/40 split as an archive artefact. Do not read it as evidence that the Dutch rules matter more.

### Extracted rules, grouped by the defect they correct

Families are named here for the first time; nothing in the references used these groupings before.

#### Family 1 — elliptical (reader must supply a word)

| # | lang | source | correction | caught by an existing rule? |
|---|------|--------|-----------|------------------------------|
| 1 | NL | anchor 1, A1 b951d942 2026-08-27 | "Bepalen waar de bron van waarheid ... hoort te liggen ... Dat is de vraag." -> "de vraag is waar ..." | **Miss.** NL 6.5 required a comma plus `wat`/`wanneer`/`indien`. NL 6.6 fired on the infinitive head but prescribed "conjugate the verb, give it a subject", which yields "We bepalen waar..." — the wrong claim. A rule that flags the right sentence and prescribes the wrong rewrite is a miss. |
| 2 | NL | anchor 3, same session | "en dat is de ernstigste" (elided head noun) | **Miss.** No rule covered ellipsis of a head noun. |
| 3 | NL | A1 40469bc6 2026-07-31 | "uitwerkstatus (zonder streepje graag)" | Hit, NL 6.5 pattern b. |
| 4 | NL | A1 f4f38aad 2026-07-21 | "Alles of bijna alles:" — empty run-up, "dat zegt niks" | **Miss.** Covered on the generative side only (`writing-principles.md`, "introductory clause + colon + bare label"), never in the proof references. |
| 5 | EN | A1 b951d942 2026-08-27 | "Er staan drie soorten deck, niet twee" — appended-correction negation | Partial. EN 2.1 covered "not X but Y", not the tail form. |

#### Family 2 — empty evaluative tail

| # | lang | source | correction | caught? |
|---|------|--------|-----------|---------|
| 6 | NL | anchor 2, A1 b951d942 2026-08-27 | "onbekend, en daar zit het probleem" | **Miss.** Grepping all four reference files for `daar zit`, `dat is het punt`, `that's the point`, `therein lies`, `which is exactly` returned **zero hits**. Not a rule that nearly fired: a family nobody had described. EN/NL 3.3 bans the signposted conclusion, which is a cousin at paragraph scale and does not reach the sentence-level tail. |
| 7 | NL | anchor 3 | "en dat is de ernstigste" (ranking sub-form) | Miss, same. |
| 8 | NL | anchor 1 | "Dat is de vraag." (standalone stub form) | Miss, same. |

#### Family 3 — audience: who is this sentence addressed to

The largest family by source count, and the one with no prior representation anywhere in the references.

| # | lang | source | correction | caught? |
|---|------|--------|-----------|---------|
| 9 | NL | anchor batch item 8, 2026-08-27 | "Eerst iets rechtzetten dat het gesprek makkelijker maakt: de velden bestaan al." -> "De service strategie en doelgroep strategie templates bevatten de vragen/velden die nodig zijn." | Miss. |
| 10 | NL | A1 2c4ca391 2026-08-02 | "dingen zoals 'besluit 2 augustus' eruit graag, ook alle gespreksnotities ... ze weten niks van afspraken tussen ons, of van het process, en dat hoeven ze ook niet te weten" | Miss. |
| 11 | NL | A0 `feedback_clean_slate_toolteksten` 2026-08-04, ext. 08-18 | organisation-facing tool text is a clean slate: no process references, version comparisons, or truncated source fragments | Miss. |
| 12 | NL | A0 `feedback_meeneem_docs_zelfstandig` 2026-08-21 | documents she carries to work must be readable standalone; never point at another document; explain every point in place; exact slide numbers per point | Miss. |
| 13 | NL | A0 `feedback_bevindingen_altijd_uitleggen` 2026-08-25 | every finding gets its own explanation, four elements per point; "vermijd steno dat alleen voor mij betekenis heeft" | Miss. |
| 14 | NL | A0 `feedback_task_references` 2026-08-14 | never a bare `T154`; the plain-language description is the name | Miss. |
| 15 | NL | anchor batch item 7 + A1 40469bc6 2026-07-31 | "Vraag C" / "Vraag 1, 2, 3" as headings -> promote the actual question | Miss. Corrected on 07-31 and again on 08-27. |
| 16 | NL | A1 b3ca2628 2026-08-27 | column headings "G" and "A": "ik heb geen idee wat dat betekent" | Miss. |
| 17 | NL | A1 40469bc6 2026-07-31 | "Waarom hebben we As 1 en As 2 (zou het niet zo noemen)?" | Miss. |
| 18 | NL | anchor batch item 4 | "waarom wel" / "waarom niet" -> "voordelen" / "nadelen" | Miss. |
| 19 | NL | anchor batch item 6, plus A1 8300ef2c 2026-08-23, plus A0 `feedback_framework_lay_vocabulary` (three separate corrections) | "deck" -> presentaties/PowerPoints, "niemand kent het woord deck" | Only as one abstract line in `writing-principles.md`. |
| 20 | NL | A0 `feedback_standalone_tools_viewport` 2026-07-21 | "klep" and "vloer"/"vloer-actie" mean nothing to readers | Miss. |
| 21 | NL | A1 7e3983d0 2026-07-17 | "niemand weet wat we met 'witte vlek' bedoelen" | Miss. |
| 22 | NL | A1 40469bc6 2026-08-04 | "ik vermoed dat niemand de term Shunting kent en toch wordt het steeds gebruikt" | Miss. |
| 23 | NL | A1 197d9a5d 2026-07-31 | "ipv navraag punt 27, gewoon in spreektaal de daadwerkelijke vraag (verwijs niet naar andere documenten, niemand kent die)" | Miss. |
| 24 | NL | A1 91543a5a 2026-08-10 | "veel verwijzingen naar de inhoud van de onderzoeken zonder uit te leggen wat er precies in zit ... niet het 'steno' gevoel" | Miss. |
| 25 | NL | A0 `feedback_framework_lay_vocabulary` GRENS 2026-08-25 | **counter-rule:** the jargon rule does not apply to model element names; "capabilities" renamed to "vakmanschap" was reverted; vague is worse than unfamiliar | Miss, and its absence is the more dangerous one. |
| 26 | EN | A1 8300ef2c 2026-08-18 | "I'm not sure we should call the IAMconnected Service provider, that's like saying 'MCA Service' instead of just MCA" | Miss. |
| 27 | NL | A0 `feedback_clickable_file_links` 2026-08-02 | a deliverable's link text must be the full path, never a short label | Miss (out of scope for prose rules; noted, not added). |

#### Family 4 — register

| # | lang | source | correction | caught? |
|---|------|--------|-----------|---------|
| 28 | NL | A1 d059affc 2026-07-23 | "Er werd een misgelopen omzet genoemd van ..." -> "omzet van een of twee ton", first person, "alsof ron het zelf gewoon zegt" | Miss. NL 2.2 covered "De onderzoekers suggereren dat", a cousin. |
| 29 | NL | same message | "De capaciteit van terminals wordt sterk vergroot" is "heel formeel"; "wordt fors groter" is fine | Miss. |
| 30 | NL | A1 40469bc6 2026-08-04 | "De notities klinken erg machine achtig ... ik snap nu zelf niet eens wat er soms bedoeld wordt omdat het zo kryptisch opgeschreven is" | Partial. NL 6.3 named the problem and prescribed nothing. |
| 31 | NL | A1 5c0c3967 2026-08-12 + A0 `feedback_doelgroepen_dossier_stijl` | "alles voluit uitgeschreven in makkelijk te begrijpen taal ... het mag daardoor best langer worden (zo lang als nodig) als het maar makkelijk leesbaar is" | Partial, same. |
| 32 | NL | anchor batch item 3 | "herschrijven als normale zinnen in spreektaal" | Partial, same. |

#### Family 5 — punctuation, already covered, confirmed by the corpus

| # | lang | source | correction | caught? |
|---|------|--------|-----------|---------|
| 33 | NL/EN | A0 `feedback_no_em_dashes` (revintel), `feedback_avoid_em_dashes` (europeansleeper), `feedback_writing_tell_emdash` (missioncontrol), `feedback_doelgroepen_dossier_stijl` + `feedback_standalone_tools_viewport` (psf) | never an em dash, headings included | Hit. **Recorded independently in five memories across four projects** — the clearest cross-project duplication in the corpus, and the strongest evidence that a hard zero is correct. |
| 34 | NL | A1 2c4ca391 2026-08-06 | "geen ; gebruiken, gewoon normale zinnen met punten en komma's" | Hit, NL 4.5. |
| 35 | NL/EN | A1 d059affc 2026-07-19, A1 9c420241 2026-07-26 (EN) | no "eerlijk"/"honest" | Hit. |
| 36 | EN | A1 9c420241 2026-07-26 | no "load bearing", no "it's this not that" | Hit. |

#### Family 6 — preferences, not AI tics

These generalise to this user only. Both belong in the references, labelled as preferences.

| # | source | preference |
|---|--------|-----------|
| 37 | A0 `feedback_bold_bullets_sometimes_ok` | bold-first bullets are genuinely useful for scanning; flag but always offer keep-as-is |
| 38 | commit `0abae83`, 2026-08-27 | Oxford commas in Dutch are deliberate; do not flag |
| 39 | A0 `feedback_no_dun_for_data` | never "dun" for a small amount of data |
| 40 | A0 `user_writing_voice` | first person, "wij"/"jullie", editorial asides welcome, no self-congratulatory preambles, "de kunst" not "de strategische kunst" |
| 41 | A0 `feedback_no_anthropomorphizing_models` | models do not "think" or "know" |
| 42 | A0 `feedback_preserve_versions`, `feedback_mobile_html`, `feedback_framework_doc_edits` | process preferences, out of scope here |

#### Rules 43-46

| # | lang | source | rule |
|---|------|--------|------|
| 43 | NL | A1 f4f38aad 2026-07-21 | **the counterweight:** "soms wordt er dus met weinig woorden te weinig gezegd ... maar nu was het weer bijna 3 regels die eigenlijk precies hetzelfde zeiden. We moeten wel specifiek zijn maar niet langdradig" |
| 44 | NL | A0 `project_doelgroepstrategie_getrouwheid`, A1 40469bc6 2026-07-31 | use the source's own words; evidence text is verbatim, never paraphrased |
| 45 | NL | A0 `feedback_doelgroepen_dossier_stijl` | direct labels over metaphors in headings; metaphors allowed once in running text, with explanation |
| 46 | NL/EN | A0 `feedback_writing_tell_emdash` 2026-07-11 | a banned-word grep over six of her documents returned **zero hits**; the tells are structural and punctuational; her drafts need thinning, not rewriting |

### The three findings that shaped the refresh

**1. The dominant tic is family 2, and the references' emphasis was inverted.** Five commits hardened family 1; nothing anywhere addressed family 2. Yet the evaluative tail appears in all three anchor cases, and the elliptical defect appears in two, both times stacked on top of a tail. Anchor 3 stacks both inside a single clause. A merged rule cannot handle this: the completion test clears a grammatically-complete tail, and the subtraction test clears a fragment that carries real information. Two rules, two tests.

**2. Family 3 is the largest family and had no rule at all.** Nineteen corpus items, recorded across six memory files in four project directories, plus the most damaging item in the anchor batch. It is also the family that makes a deliverable unusable rather than merely clumsy, which is why it went in as a first-class section rather than a note under tone.

**3. The memory system reproduced the same enumeration failure.** `feedback_task_references` says never to use a bare T-number without its description. It was given on 2026-08-12, corrected again on 08-14 because the rule "te zacht was geformuleerd", and item 15 above — strip "Vraag C", promote the question — is the same defect in a new surface form on 08-27. `feedback_framework_lay_vocabulary` records the word "deck" being corrected three times, the third time escalating to a repo `CLAUDE.md` because "deze memory alleen bleek niet genoeg". Per-instance recording does not converge any better than per-instance rule-writing. That is the argument for family-level rules with a test, stated as evidence rather than as analogy.

---

## Leg B: external corroboration and mechanism

### The overcorrection signature is real and externally named

The 2023-24 tells (banned vocabulary, "delve", "tapestry") have largely been trained out, and the failure has moved toward over-compression. The tropes.fyi pattern directory names several of the constructions this corpus produced, independently of it:

- **"Comma-clipped trailing phrase"** — "short tail hung off a comma instead of landing the point directly". This is family 2's comma form, named by an outside observer.
- **"Short punchy fragments"** — "excessive standalone short sentences for manufactured emphasis", example "He published this. Openly. In a book." This is the standalone stub form.
- **"Reasoning leak"** — "narrating the text's own moves instead of just delivering content". This is family 3's meta-commentary form. The independent naming is worth noting: the audience error was the one the task flagged as "least like a style tic", and it turns out to be a catalogued AI pattern.
- **"Superficial analyses"**, **"never-ending conclusion"**, **"premise stacking"**, **"belaboring the unnecessary"**, **"self-echo"** — the first is already covered as participial tacking; the rest are candidates flagged in the proposal but not added.

Proofed's AI editing checklist and the AI-slop pattern guides converge on the same diagnostic the refresh adopted: "for each problematic sentence structure, ask what the sentence is actually saying and say that instead. These phrases are filler that creates the illusion of insight while restating the obvious."

### Dutch grounding

Two of the existing Dutch rules were using the wrong terms.

**Tangconstructie.** NL 2.2 was titled "De Angelsaksische tangconstructie" and its examples were "De onderzoekers suggereren dat..." and "Het is het vermelden waard dat...". Those are anglicised word order and a literal idiom translation. A tangconstructie is something else entirely: per the Onze Taal taalloket, "woorden of zinsdelen die bij elkaar horen, te ver uit elkaar staan", taxing working memory across the gap. The three canonical forms are article-noun, verb-complement, and subject-verb. The rule has been renamed and the real definition added alongside, with the standard repair (split into two sentences).

**Naamwoordstijl.** The §6.5 hyphen-noun-stack rule was an ad-hoc description of what Dutch style guidance already calls naamwoordstijl: "te veel zelfstandige naamwoorden op plaatsen waar ook een vervoegd werkwoord zou kunnen staan". Onze Taal's diagnostic (nominalised verbs with het/een, suffixes in -ing and -atie, chains of prepositions) and repair (restore the action verb with an explicit agent) are sharper than what the reference had, and are now cited in the register rule.

**Zinsfragment.** Scribbr's Dutch academic style guidance supplies the test the refresh adopted for family 1: turn the sentence into a question, and if the required verb or subject cannot be identified, it is a fragment. Its three categories (missing subject, missing verb form, missing article) are a superset of what NL 6.5-6.7 enumerated, which is a second argument for one test over N surface rules.

**Linksdislocatie** is the correct name for anchor 1's construction: the subject placed to the left with a resumptive `dat` in the actual sentence ("Een groot deel van de medewerkers, dat zijn senioren"). Grammatical Dutch joins the two halves with a comma; the anchor mis-punctuates them as two sentences. The term is not used in the reference — it would not help an agent apply the rule — but it confirms that the user's preferred fix (front the finite verb, avoid the dislocation entirely) is the better repair rather than merely a stylistic preference.

### Verdict on the em-dash hypothesis: partly supported, and it does not mean loosening the rule

The hypothesis was that hardening em dashes to "never" on 2026-07-13 without supplying a replacement joint pushed the model toward a full stop, producing fragment-plus-stub.

**The measurement.** Added lines in `portfoliostrategyframework/docs`, per 1,000 added words:

| period | added words | em dash / kw | NL evaluative tail / kw | fragment proxy / kw |
|--------|-------------|--------------|--------------------------|----------------------|
| 2026-05 | 162,213 | 17.46 | 0.049 | 0.055 |
| 2026-06 | 129,960 | 14.70 | 0.015 | 0.054 |
| 2026-07-01 to 07-13 (pre) | 290,924 | **21.97** | 0.065 | 0.027 |
| 2026-07-13 to 08-01 (post) | 769,809 | **9.27** | 0.040 | 0.056 |
| 2026-08-01 to 08-14 | 302,096 | 11.74 | **0.232** | 0.086 |
| 2026-08-14 to 08-28 | 754,519 | 9.53 | **0.346** | 0.105 |

**What holds.** The em-dash rule worked, and worked immediately: density in newly written prose fell 58% at the hardening date and stayed at 9-12 per 1,000 words. Over the following six weeks the Dutch evaluative tail rose from a stable 0.015-0.065 baseline to 0.346, a factor of five to eight, and the fragment proxy roughly quadrupled. Colon density over the same window rose 27% (27.66 to 35.71 per 1,000 words) while semicolons fell from 14.49 to 4.78, which is the July semicolon ban working and the pressure moving to the one glue mark still permitted.

**What does not hold.** The tail rise is not a step at 2026-07-13. It lagged by roughly three weeks: the fortnight straight after the hardening had a *lower* tail rate (0.040) than the fortnight before it (0.065). The August work also shifted toward argumentative Dutch prose (the organisation-model rebuild, the AI dossiers), which independently invites evaluative endings. And an equivalent measurement over agent chat turns, which the reference files do not govern, shows em-dash density essentially flat (18.81 to 16.92 per 1,000 words) while the same tail rise appears — so the tail rose in a surface where no em-dash suppression was in force.

**The mechanism has independent support.** Freeburg, *The Last Fingerprint: How Markdown Training Shapes LLM Prose* (arXiv:2603.27006, 2026) argues that em-dash use is markdown structure leaking into prose, and reports that suppressing a specific markdown device does not remove the underlying structural impulse but redirects it: "suppression instruction causes the model to redirect the formatting tendency to alternative syntactic locations", specifically naming em-dash suppression surfacing as "alternative dash usage or syntactic restructuring".

**The conclusion drawn.** Displacement is real and measurable in this corpus, but the em-dash rule is not the thing to loosen. It is doing its job, it is the single most-confirmed preference in the corpus (five memories, four projects, an explicit "for this user it is a hard zero"), and weakening it would trade a solved problem for an unsolved one. What was missing is the instruction about *where the replacement goes*. The rule listed substitutes but never warned that swapping an em dash for a full stop leaves a fragment, or that swapping it for a colon breaks the next rule along. That warning is now attached to the em-dash rule itself, to the general principles, and to the editor agent's checklist, in both languages. The same audit was applied to the other absolute prohibitions: the colon rule already carried a list of legitimate uses in Dutch and now does in English too; the semicolon ban is confirmed by the corpus and left as is; the inline-emphasis ban has no observable displacement effect in the data.

---

## Leg D: validation against a held-out set

Nine items, roughly 20% of the 46-item corpus, fixed in writing before any rule was drafted (`scratchpad/legA/HOLDOUT.md`). The three anchor cases were excluded as the calibration set.

**A contamination that had to be corrected first.** Six of the nine held-out sentences were used verbatim as worked examples while drafting the new register, elliptical and wrong-reader rules. That would have made the hit rate meaningless. All six were replaced with equivalent examples drawn from the anchor set or written fresh, in commit `609d221`, before validation ran. The rules themselves did not change; only the illustrations moved. Flagging this rather than quietly re-picking the holdout: the leak happened because the holdout was recorded but not then treated as off-limits while writing, which is a process gap worth naming.

| id | lang | flagged? | prescription matches? | notes |
|----|------|----------|-----------------------|-------|
| H1 | NL | yes, 5.8 | yes | "Er werd ..." is a named trigger in the impersonal-reportage list; prescription "name the speaker, or just say it" yields the user's rewrite. |
| H2 | NL | yes, 5.8 + 4.5 | yes | Judgement-call hit rather than a mechanical one: "wordt sterk vergroot" is a formal passive with an intensifier, caught by the read-aloud test and by the parallel example, not by a literal string. |
| H3 | NL | **no** | n/a | **Miss.** The bare-label form needs the colon to end the line; the colon-as-glue rule explicitly permits a colon whose left side is not a standalone sentence. "Alles of bijna alles:" fell between them. |
| H4 | NL | yes, 5.9 | yes | The rule's own example is "Vraag C" from the anchor set; H4 is the separate "Vraag 1/2/3" instance from five weeks earlier, so this tests generalisation across instances of a known pattern rather than discovery of a new one. |
| H5 | NL | yes, 5.9 | yes | "vloer-actie" is not named in the rule after de-leaking; the jargon test ("does this word appear in the source document the reader does know?") catches it anyway. |
| H6 | NL | yes, 5.9 + 5.8 | yes | Both halves: the pointer to another document, and the request for spoken register. |
| H7 | EN | yes, 1 + 2.1 + 5.3 | yes | Pre-existing rules. Validates that the refresh did not break them; adds no evidence for the new rules. |
| H8 | EN | **no** | n/a | **Miss.** "IAMconnected Service provider" is not an analytical coinage, so 5.5 does not reach it, and no other rule addresses a redundant classifier bolted onto a name. |
| H9 | NL | yes, 5.9 + 5.8 | yes | |

**First-pass hit rate: 7 of 9 (78%). Dutch 6 of 7 (86%), English 1 of 2 (50%).**

No mis-prescriptions: wherever a rule fired, its prescribed fix matched what the user actually did. H2 is the weakest hit and depends on the reviewer applying a judgement test rather than matching a string.

**On the English number.** One hit out of two is not a measurement. It is two data points, and the reason there are only two is the archive gap described in Leg A. The honest statement is that the English rules are untested against held-out English corrections, and the refresh's English coverage rests on mirroring rules validated in Dutch plus the external sources in Leg B. If revintel or europeansleeper transcripts can be recovered from a backup, re-running A1 over them would be the single highest-value follow-up.

**Both misses were closed** in commit `8a8178b`, kept separate so the validation-driven part can be reverted on its own. H3 became a new surface form of the elliptical family ("empty run-up before a colon"), H8 a new bullet under the wrong-reader rule. Neither was a calibration problem; both were genuine holes. The post-fix rate would be 9 of 9, which is not a meaningful number and is not claimed as one — a rule written to catch a specific held-out sentence will catch it.

**On overfitting.** The 78% first-pass rate is the number that means something, and it came from rules built on a 37-item training set drawn from the same user, the same period, and largely the same project. The rules should be expected to degrade on a different writer or a different domain. What partially protects against that is that the two core rules are tests rather than string lists, and both tests are corroborated by outside sources (Scribbr for the fragment test, the AI-editing literature for the subtraction test) rather than derived only from this corpus.

---

## Incidental finding, reported not fixed

`/Users/esther/.claude/projects/-Users-esther-prog-porfoliostrategyframework/` — note the misspelling, "porfolio" — holds 5 files, 4 of them memories, including `user_writing_voice.md`, which is the single richest voice-preference document in the whole corpus (perspective, phrasing, terminology, structure, condensing and enrichment patterns, derived from comparing her manual edits to Claude drafts of the framework). Because the directory name does not match any real project path, none of these will ever be recalled by a session. They were read manually for this research. Merging them into `-Users-esther-prog-portfoliostrategyframework/memory/` would make them live again; that is out of scope here.
