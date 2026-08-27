# Writing-style refresh 2026: proposal

**Date:** 2026-08-27
**Branch:** `feat/writing-style-refresh-2026`
**Evidence:** `docs/research/2026-08-27-ai-writing-patterns-refresh.md`

The revised reference files are committed on this branch, so the review is a diff rather than a reading assignment. This document records what changed and why, what was deliberately not changed, and the one part that is a recommendation rather than an implementation.

---

## 1. What changed, with the evidence behind each

### Merged: four fragment rules became one

**Commit `734944d`.** NL 6.5, 6.6, 6.7 and EN 2.8 were four rules for one defect. They are now one rule per language, at 2.8 in both files, carrying a single diagnostic with the surface forms listed underneath as examples.

**Evidence.** Five of the eight amendments to the Dutch reference patch this same defect, each written against the surface form that had most recently annoyed the user (Leg A, "why enumeration is failing"). Anchor 1 is the sixth surface form and got through all five. Scribbr's Dutch style guidance treats missing subject, missing verb form and missing article as one category with one test, which is a superset of what the three Dutch rules enumerated.

**The prescription was also wrong, and that mattered more than the coverage gap.** NL 6.6 fired on anchor 1's infinitive head but told the writer to "conjugate the verb, give it a subject", which produces "We bepalen waar de bron van waarheid hoort te liggen", a plan of action where the user wanted a question. The new rule says to lead with the finite verb of the *actual claim* and shows both the right and the wrong repair. A rule that flags the right sentence and prescribes the wrong rewrite is counted as a miss throughout this work.

### Added: empty evaluative tails (EN 2.9 / NL 2.9)

**Commit `34dab19`.**

**Evidence.** Grepping all four reference files for this family returned zero hits. It appears in all three anchor cases. In `portfoliostrategyframework/docs` its density in newly written prose rose from a stable 0.015-0.065 per 1,000 words through May, June and early July to 0.346 by late August. Externally corroborated: tropes.fyi names the comma form "comma-clipped trailing phrase" and the standalone form "short punchy fragments".

**Why it is a separate rule and not folded into 2.8.** The two diagnostics clear each other's cases. "Onbekend, en daar zit het probleem" is grammatically complete, so the completion test passes it; "Bepalen waar de bron van waarheid hoort te liggen" carries real information, so the subtraction test passes it. Anchor 1 contains one of each and anchor 3 stacks both inside a single clause. Each rule now tells the reviewer to run the other one.

**The boundary is stated explicitly**, because over-applying this would strip legitimate landings: a closing clause survives when it adds a consequence, draws a real contrast, or lands a long passage that earned it. One per piece is fine; two or more is the pattern.

### Added: written for the wrong reader (EN 5.9 / NL 5.9)

**Commit `34dab19`.**

**Evidence.** Nineteen corpus items, the largest family, recorded across six memory files in four project directories (`feedback_clean_slate_toolteksten`, `feedback_meeneem_docs_zelfstandig`, `feedback_bevindingen_altijd_uitleggen`, `feedback_task_references`, `feedback_framework_lay_vocabulary`, `feedback_standalone_tools_viewport`) plus item 8 of the anchor batch. Nothing in any of the four reference files covered it; `writing-principles.md` had one abstract line about jargon.

**It is a first-class section rather than a note under tone** because it is the only family that makes a deliverable unusable rather than merely clumsy. The agent wrote sentences addressed to the person who commissioned the document instead of the person who would read it.

**It carries the counter-rule.** On 2026-08-25 the user reverted a rename of `org:capabilities` to `org:vakmanschap` that a "no jargon" instruction had caused, and set the boundary: the jargon rule applies to stakeholder-facing output, not to model element names, and "vague is worse than unfamiliar". Without that clause this rule would have caused real damage; it is stated at the end of the section in both languages.

### Added: over-formal register (EN 5.8 / NL 5.8)

**Commit `34dab19`.** NL 6.3 named the problem and prescribed nothing; English had no equivalent at all.

**Evidence.** Five corpus items, including a full before/after pair from 2026-07-23 where the user rewrote a document herself and said "wellicht zitten daar ook patronen in". The patterns were impersonal reportage ("Er werd ... genoemd") and formal passives with intensifiers ("wordt sterk vergroot" rather than "wordt fors groter"). Onze Taal's naamwoordstijl entry supplies the second half and its repair, cited in the rule.

### Added: three tests at the top of each file

**Commit `34dab19`.** A short triage block naming the completion test, the subtraction test and the reader test, with section pointers.

**Evidence.** `feedback_writing_tell_emdash` records a proof pass over six of the user's documents in which a banned-word grep returned **zero hits** while the structural patterns returned dozens. Section 1 is the longest single block in both files and the first thing an agent reads. Rather than deleting it, since it is still correct for agent-generated prose and that is the actual target, the block says plainly which tests carry the load.

### Extended: three existing rules

- **2.1** now covers the appended-correction variant ("Er staan drie soorten deck, niet twee"), which the anchor batch flagged and which the old "not X but Y" phrasing did not reach.
- **4.1 (em dashes)** now warns where the replacement goes wrong: a full stop leaves a fragment, a colon breaks 4.2/4.5. See §4 below for the reasoning.
- **General principles** now carry the compression counterweight and the "never replace a punctuation mark with a hole" rule.

### Added after validation: two gaps

**Commit `8a8178b`, kept separate so it can be reverted on its own.** The held-out set scored 7 of 9 on the first pass. Both misses were real holes rather than calibration problems: an empty run-up before a colon ("Alles of bijna alles: de investering...") fell between the bare-label form and the colon-as-glue exception, and a redundant classifier bolted onto a name ("IAMconnected Service provider") was not reachable by the invented-concept-label rule. Added as a new surface form of 2.8 and a new bullet under 5.9.

### Deleted

- **`writing-foundations/references/antipatterns_to_avoid_bad_writing.md`**, 484 lines. See §3.
- **NL 3.1 + 3.2** (uniform paragraph structure, uniform paragraph length) merged into one rule in both languages. Two rules saying one thing, and a small demonstration of the principle the fragment merge established.
- **Nothing else.** The Oxford-comma rule removed on 2026-08-27 has not been reintroduced anywhere; verified by grep across all four surviving files.

### Corrected: two factual errors in the Dutch reference

- **NL 2.2 was titled "De Angelsaksische tangconstructie"** and its examples were anglicised word order and a literal idiom translation. Those are not tangconstructies. Per the Onze Taal taalloket a tangconstructie is a gap between paired elements that taxes working memory. The rule is renamed "Engelse zinsbouw in Nederlandse woorden" and the real definition is added alongside it, with the standard split-into-two-sentences repair.
- **The `## 5. Toonpatronen om te vermijden` heading had been lost** in an earlier renumbering, leaving 5.1 through 5.6 nested under section 4 (punctuation). Restored.

---

## 2. EN/NL parity table

Every rule now exists in both files. The numbers differ where the two files' histories diverged; the four that matter most were deliberately aligned.

| rule | EN | NL | notes |
|------|----|----|-------|
| Not X but Y, incl. appended correction | 2.1 | 2.1 | aligned |
| Dramatic countdown | 2.2 | 2.7 | added to NL |
| Self-posed rhetorical questions | 2.3 | 2.4 | |
| Anaphora abuse | 2.4 | 2.10 | added to NL |
| Tricolon overuse | 2.5 | 2.5 | aligned |
| Participial phrase tacking | 2.6 | 2.3 | |
| False ranges | 2.7 | 2.6 | |
| **Elliptical constructions** | **2.8** | **2.8** | deliberately aligned |
| **Empty evaluative tails** | **2.9** | **2.9** | deliberately aligned |
| Uniform paragraph shape | 3.1 | 3.1 | merged from two rules in both |
| Signposted conclusion | 3.2 | 3.2 | aligned |
| Fractal summaries | 3.3 | 3.6 | added to NL |
| Dead metaphor | 3.4 | 3.3 | |
| One-point dilution | 3.5 | 3.7 | added to NL |
| "Despite its challenges" | 3.6 | 3.4 | |
| Too many lists | 3.7 | 3.5 | added to EN; was NL 6.4, not Dutch-specific |
| Historical analogy stacking | 3.8 | 3.8 | added to NL |
| Em dashes never | 4.1 | 4.1 | aligned; displacement warning added to both |
| Colons and semicolons as glue | 4.2 | 4.5 | EN absorbed its old 4.6 and gained the Dutch standalone-readability test and list of legitimate uses |
| Bold-first bullets | 4.3 | 4.2 | |
| Excessive markdown formatting | 4.4 | 4.4 | aligned |
| Inconsistent quotation marks | 4.5 | 4.6 | added to NL |
| Inline bold/italic for emphasis | 4.6 | 4.7 | |
| Perpetual hedge | 5.1 | 5.1 | aligned |
| Stakes inflation | 5.2 | 5.2 | aligned |
| False vulnerability | 5.3 | 5.3 | aligned |
| Vague attributions | 5.4 | 5.4 | aligned |
| Invented concept labels | 5.5 | 5.7 | added to NL |
| Pedagogical voice | 5.6 | 5.5 | |
| Press-release tone | 5.7 | 5.6 | |
| **Over-formal register** | **5.8** | **5.8** | deliberately aligned; new in EN, prescription added in NL |
| **Written for the wrong reader** | **5.9** | **5.9** | deliberately aligned; new in both |
| Anglicised word order + tangconstructie | n/a | 2.2 | **legitimately NL-only** |
| English-style heading capitalisation | n/a | 4.3 | **legitimately NL-only** |
| Nadruk-accents on vowels | n/a | 4.8 | **legitimately NL-only** |
| Literal translation of English idiom | n/a | 6.1 | **legitimately NL-only** |
| Te foutloos (suspiciously flawless) | n/a | 6.2 | **unresolved, see below** |

**The one asymmetry I am not confident about.** NL 6.2 says human Dutch prose contains small imperfections and AI prose is suspiciously polished. That claim is not Dutch-specific, so parity says mirror it. I did not, because "write deliberately rougher English" is advice I am not sure is right for the stakeholder-facing prose this reference mostly governs, and because the corpus contains no correction asking for it. Flagging rather than deciding: either mirror it into English or delete it from Dutch, and the corpus does not tell me which.

---

## 3. Three-way drift: the decision

**Decision: delete the duplicate. The proof references are the single source; writing-foundations points at them.** Commit `7048680`.

The reasoning is not a judgement call, because the file was already dead:

- `writing-foundations/SKILL.md` already pointed at `skills/proof/references/writing-style-en.md` in **both** of its modes. It never referenced its own `antipatterns_to_avoid_bad_writing.md`.
- Grepping the whole repo for `antipatterns_to_avoid` returned zero hits outside the file itself.
- Its content was a fork frozen around March. A heading diff against the proof references showed it missing the entire May fragment series (NL 6.5, 6.6, 6.7), the July hardening (EN 4.6, 4.7; NL 4.5, 4.6, 4.7), the em-dash change from "overuse" to "never", and the Oxford-comma removal.
- It used em dashes in its own section headings, against the rule it was stating.

So it was 28KB of stale text that nobody read and that would have been a third place for the next patch to be forgotten. `SKILL.md` now says explicitly that the proof references are the single source and names the Dutch reference on equal footing with English rather than as an afterthought, and points at the three tests as the entry point.

The `writing-style-editor` agent keeps its condensed checklist (commit `6cc00d9`), because a subagent needs a short prioritised list rather than a 30KB file, but the checklist now carries section numbers into both references so it stays a pointer rather than a fork. It had drifted badly: it still capped em dashes at "2-3 per 1,000 words" six weeks after the hard zero, had no entry for any fragment rule, and led with banned vocabulary.

---

## 4. Verdict on the em-dash hypothesis

The full measurement is in the research document. In short:

**The rule worked.** Em-dash density in newly written prose fell 58% at the 2026-07-13 hardening (21.97 to 9.27 per 1,000 added words) and stayed there.

**Displacement is visible.** Over the following six weeks the Dutch evaluative tail rose five to eightfold, the fragment proxy quadrupled, and colon density rose 27% while semicolons fell, which is the pressure moving to the one glue mark still permitted. Freeburg's *The Last Fingerprint* (arXiv:2603.27006) gives the mechanism: em-dash use is markdown structure leaking into prose, and suppressing one device redirects the impulse rather than removing it.

**But the timing is not clean and the em-dash rule is not the thing to loosen.** The tail rise lagged by about three weeks, the August work shifted toward argumentative Dutch prose that independently invites evaluative endings, and the same rise shows up in agent chat where no em-dash suppression applies. More decisively, the hard zero is the single most-confirmed preference in the whole corpus: five separate memories across four projects, one of them stating "for this user it is a hard zero", stronger than the generic style-guide cap.

**What was actually missing is the instruction about where the replacement goes.** The rule listed substitutes but never warned that a full stop leaves a fragment or that a colon breaks the next rule. That warning is now attached to the em-dash rule itself, to the general principles, and to the editor agent's checklist, in both languages. The other absolute prohibitions were audited the same way: the colon rule already carried a list of legitimate uses in Dutch and now does in English; the semicolon ban is confirmed by the corpus and unchanged; inline emphasis shows no displacement effect in the data.

---

## 5. Distribution: making good writing the default

**Not implemented. This is a recommendation with a sketch concrete enough to evaluate.**

The anchor sentence came from an agent in `portfoliostrategyframework`, a repo where nobody was running proof. Post-hoc editing cannot fix what generation keeps producing, and the writing-foundations references total roughly 60KB, which no always-on mechanism can carry.

### The options assessed

| option | fires reliably? | context cost per turn | reaches repos without the plugin? | other converter targets |
|--------|-----------------|------------------------|-----------------------------------|--------------------------|
| Global `~/.claude/CLAUDE.md` | Yes. Prepended to every turn of every session, subagents included. | Whatever the block costs, always. ~300 tokens for the sketch below. | **Yes.** Its main advantage. | Does not convert. Codex reads `AGENTS.md`, Gemini reads `GEMINI.md`; each would need its own copy. |
| Claude Code output-style | Only when the user selects it, and it replaces the default behaviour wholesale. | Varies. | No. | No equivalent on any target. |
| `UserPromptSubmit` hook | Every prompt; can be gated on prose-shaped input. | Zero unless it fires. | Yes if configured in `~/.claude/settings.json`. | Converter **drops hooks entirely** for Gemini, Copilot and Kiro; translates only for OpenCode. |
| `PostToolUse` hook on Write/Edit | At the moment of writing, and it can inspect what was written. | Zero unless it fires. | Yes if global. | Same limitation. |
| Skill auto-invocation via description tuning | Unreliable; depends on the model noticing. | Near zero until loaded, then ~60KB. | Plugin-installed repos only. | Skills copy across mostly intact. |
| Plugin ships it | `plugin.json` has no `hooks` key today; it would have to be added. | Zero unless it fires. | Plugin-installed repos only. | Dropped on 3 of 11 targets. |

### Recommendation: two layers

**Layer 1, generation: a distilled rule set in the global `~/.claude/CLAUDE.md`, replacing the current two-bullet stopgap.** It fires on every turn of every agent in every repo, including subagents and repos without the plugin, which no other option does. Its cost is a few hundred tokens a turn, which is cheap against the cost of a stakeholder document that has to be rewritten.

**Layer 2, detection: a `PostToolUse` hook on `Write|Edit` that greps prose files for the handful of mechanically-detectable patterns and emits a warning.** The user already runs global `PreToolUse` and `PostToolUse` hooks on `Write|Edit` (`danger-guard.py`, `work-heartbeat.py`, `sync-command-module-skills.sh`), so this is proven infrastructure rather than a new mechanism. It costs nothing until it fires, and it catches at the moment of writing what generation still missed. Scope it to `.md` files outside `docs/plans/`, `docs/brainstorms/` and `.context/`, matching the proof skill's own scope rules. Detectable mechanically and worth detecting: the `—` character, `, en daar zit` / `, en dat is` / `that's the problem` / `which is exactly the`, a standalone `Dat is de vraag.` / `That's the point.`, `Er werd ... genoemd` / `It was noted that`, and hyphen stacks of three or more parts.

**Tradeoffs, stated plainly.** The global `CLAUDE.md` is user-global and sits in her global gitignore, so it cannot be version-controlled or shipped by the plugin. The fix is for the plugin to keep the canonical text of the distilled block in the repo, at `plugins/command-module/skills/proof/references/always-on.md`, which the user syncs into her global file. That gives it a versioned home, makes it reviewable in a diff, and gives the converter something to copy into `AGENTS.md` and `GEMINI.md` for the other targets. Layer 2 degrades to nothing on Gemini, Copilot and Kiro, which is acceptable because layer 1 is the load-bearing one.

**Rejected: output-styles** (session-level toggle, replaces the persona, does not reach subagents) and **skill auto-invocation as the primary mechanism** (the anchor case is exactly what happens when the model does not think to load the skill). Auto-invocation stays as a secondary path for real prose tasks.

### The distilled rule set, sketched

Roughly 230 words. It would have caught all three anchor cases and the four commonest families in the corpus. It ends by handing off to the full references.

```markdown
## Prose Style

Applies to all prose you write, English and Dutch alike, in documents and in chat.

- **Every sentence needs a subject and a finite verb.** If the reader has to supply a word before the sentence parses, supply it yourself. Repair by leading with the finite verb of the actual claim. Not "Bepalen waar de bron van waarheid hoort te liggen. Dat is de vraag." but "De vraag is waar de bron van waarheid hoort te liggen." Not "We bepalen waar..." — that changes the claim.
- **Never append a clause that points back at what you just said and rates it.** "…, en daar zit het probleem", "…, and that's the point", "…, en dat is de ernstigste", "Dat is de vraag." Test by subtraction: delete it and reread. If nothing was lost, it was filler. Write the consequence instead ("…, waardoor niemand kan bepalen welke versie leidend is"), or cut it.
- **Write for the person who will read it, not the person you are talking to.** No commentary about this conversation, no process or version history, no pointers to documents they have not seen, no bare identifiers where a description belongs ("T154", "Vraag C", column "G"), no in-group jargon. Explain each point where it appears. Do not simplify away a term that is precise, because vague is worse than unfamiliar.
- **No em dashes.** When you remove one, rebuild the sentence. Do not leave a full stop with a fragment after it, and do not swap in a colon.
- **Say it the way you would say it aloud.** Not "Er werd genoemd dat…" or "It was noted that…", but who said it, or just the fact.
- **Being understood beats being brief.** A sentence may be longer if that makes it right.

For a document that will be read by someone else, load the `writing-foundations` skill and the matching `proof` reference before drafting.
```

The current stopgap in `~/.claude/CLAUDE.md` covers families 1 and 2 with their tests, written from three samples. This replaces it: same two families, plus the audience family (nineteen corpus items, the largest), plus the register and displacement rules, plus the counterweight against overcorrecting toward compression. **It is a proposal, not a change. Nothing outside this repo has been touched.**

---

## 6. Size

| file | before | after | change |
|------|--------|-------|--------|
| `proof/references/writing-style-en.md` | 14.4 KB | 26.5 KB | +12.1 KB |
| `proof/references/writing-style-nl.md` | 22.9 KB | 31.9 KB | +9.0 KB |
| `writing-foundations/references/antipatterns_to_avoid_bad_writing.md` | 27.6 KB | deleted | −27.6 KB |
| `agents/docs/writing-style-editor.md` | 3.7 KB | 5.7 KB | +2.0 KB |
| **total** | **68.6 KB** | **64.1 KB** | **−4.5 KB** |

Baseline is the state at commit `50f3d71`, which is the pre-refresh content including the July hardening and the Oxford-comma removal, not `main` (those two commits live on `feat/prompt-research-skills` and were cherry-picked onto this branch so the diff starts from what the user actually has).

Net shrinkage, but only because of the deletion. The two proof references grew by 21.1 KB between them, and that growth needs justifying rather than waving through.

**Where it went, and why I think it is earned.** English absorbed most of it (+12.1 KB, close to doubling) because English had received only the July hardening and none of the May work, so closing parity meant importing four substantial rules plus enriching the colon rule. That is the specific gap the task identified. The rest is three new families, each of which is a rule plus a test plus a worked repair plus a stated boundary, which is the shape that makes a rule usable by an agent rather than merely present.

**Where it could still come down, and what I chose not to touch.** Section 1's word lists are the longest single block in each file and the lowest-yield on this user's own prose (zero hits over six documents). Cutting them would save roughly 3 KB per file. I did not, because the target is agent-generated prose rather than the user's own, and because deleting a rule the corpus does not contradict is not the same as deleting a rule the corpus refutes. The triage block now tells an agent where the load actually is, which is the cheaper fix. Other merge candidates I looked at and left alone: 3.2 and 3.3 (signposted conclusion, fractal summaries) both say "say it once"; 5.2 and 5.7 (stakes inflation, press-release tone) overlap; 4.4 and 4.6 both concern excessive emphasis. Each merge is defensible and none is forced by evidence, so they are listed here as candidates rather than done.

---

## 7. Open questions

1. **NL 6.2 "Te foutloos".** Mirror it into English or delete it from Dutch. See §2. No corpus evidence either way.
2. **The English rules are untested against held-out English corrections.** One hit out of two is two data points, not a measurement, and the reason there are only two is that the revintel and europeansleeper project directories now contain memory files and no transcripts at all. If those can be recovered from a backup, re-running the A1 extraction over them is the single highest-value follow-up to this work.
3. **Four orphaned memories** sit in `~/.claude/projects/-Users-esther-prog-porfoliostrategyframework/` (note the misspelling), including `user_writing_voice.md`, the richest voice-preference document in the corpus. The directory name matches no real project path, so none of them will ever be recalled. Reported, not fixed.
4. **Candidate rules from tropes.fyi not added**, because no corpus item supports them yet: "never-ending conclusion" (stacking clauses instead of landing one point), "premise stacking" (repeating a point before stating it), "belaboring the unnecessary" (defending minor points against objections nobody raised), "self-echo" (reusing your own earlier phrases as if paying them off). Worth watching for in the next batch of corrections.
5. **The holdout leaked during drafting** and had to be de-contaminated (commit `609d221`) before validation could mean anything. If this process runs again, the holdout sentences should be moved out of reach, into a separate file the rule-writing pass does not read, rather than merely recorded.
