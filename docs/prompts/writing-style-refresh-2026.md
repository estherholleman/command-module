# Refresh the writing-style guidance (English + Dutch) — 2026 round

You are picking up a research-and-revision task in `/Users/esther/prog/command-module`. Work autonomously; the user is asleep and will review your output in the morning. Everything you need is below.

## The problem

Three surfaces share one body of writing guidance, and all three are in scope:

- **`proof`** — the post-hoc review skill, holding the full EN and NL antipattern references.
- **`writing-foundations`** — the generative-side knowledge base (antipatterns plus positive craft principles), loaded when an agent is *producing* prose rather than editing it.
- **`writing-style-editor`** — the subagent `proof` dispatches, carrying its own condensed checklist that has drifted from both of the above.

**This is equally an English and a Dutch task.** Most of what follows is language-independent — sentence fragments, compression tics, rhythm, stub sentences, over-listing — and only a minority is genuinely NL-specific (tangconstructies, anglicisms, Dutch heading capitalisation, literal idiom translation). Do not treat this as a Dutch job with an English footnote. Where a rule holds in both languages it belongs in both references, in the same shape, with native examples in each.

### The anchor case

An agent produced this Dutch sentence in a strategy document:

> "Bepalen waar de bron van waarheid voor de strategiedata hoort te liggen en wie welke laag beheert. Dat is de vraag."

The user's correction: *"graag niet (erg opgebroken), gewoon 'de vraag is waar de bron van waarheid voor de strategiedata hoort te liggen, en wie welke laag beheert.' bijvoorbeeld."*

Diagnosis: the first half is a **zinsfragment** — an infinitive phrase with no finite verb and no subject. The second is a **resumptive pointer sentence**. Together they form a left dislocation (linksdislocatie) mis-punctuated as two sentences; grammatical Dutch would join them with a comma. The user's preferred fix avoids the dislocation entirely by fronting the finite verb. The English form of the same defect — "Working out where the source of truth belongs, and who owns which layer. That's the question." — is equally common and equally unwanted.

### Why enumeration is failing

The Dutch reference was created on 2026-03-28 and has been amended eight times since. What those commits did:

| Date | Change |
| --- | --- |
| 2026-05-05 | catch internal-event references and bare auxiliary verbs |
| 2026-05-05 | ban colons and semicolons as sentence glue |
| 2026-05-05 | catch sentence fragments and noun-stacks (§6.5) |
| 2026-05-05 | extend the noun-stack rule to 2-concept hyphens |
| 2026-05-05 | catch infinitive-headed sentences and verbless connector fragments |
| 2026-07-13 | harden em dashes, semicolons, inline bold/italic, nadruk-accents |

Five of those patch **the same underlying defect**: a clause that asks the reader to supply a verb, a subject, or an unpacked noun. Each was written to catch one specific surface form that had just annoyed the user. The anchor case is the sixth surface form of that defect, and it still got through in August.

That is the central finding, and the refresh must be built around it. These references are not stale — they are actively maintained. They enumerate by **surface form**, so every new surface form needs a new patch, and the patching is not converging. Adding a sixth fragment rule will simply be followed by a seventh.

Three rules currently sit next to the anchor case without catching it. `writing-style-nl.md` §6.5 covers fragments but only ones following a comma and beginning with *wat / wanneer / indien*. §6.6 covers infinitive heads but prescribes "conjugate the verb, give it a subject", which yields "We bepalen waar…" — not the rewrite the user wanted, so even a hit here would have produced the wrong fix. §6.7 covers bare auxiliaries, a neighbouring defect. The English side has §2.8 (Gerund Fragment Litanies), the same family scoped differently again.

The English reference has received only the 2026-07-13 pass. **None of the May fragment work was mirrored into it**, so English has almost no coverage of a defect family that is not Dutch-specific at all. That asymmetry is itself a finding, and probably not the only one of its kind.

## Current state

| File | Role | Size | Commits |
| --- | --- | --- | --- |
| `plugins/command-module/skills/proof/SKILL.md` | Review workflow: tiering, passes, findings doc | 186 lines | — |
| `plugins/command-module/skills/proof/references/writing-style-en.md` | English antipatterns | ~14KB | 2 |
| `plugins/command-module/skills/proof/references/writing-style-nl.md` | Dutch antipatterns (+ NL-specific §6) | ~23KB | 8 |
| `plugins/command-module/skills/writing-foundations/references/antipatterns_to_avoid_bad_writing.md` | Generative-side antipatterns; partly duplicates the proof references | ~28KB | 2 |
| `plugins/command-module/skills/writing-foundations/references/writing-principles.md` | Positive craft guidance | ~31KB | — |
| `plugins/command-module/agents/docs/writing-style-editor.md` | Subagent dispatched by proof; own condensed checklist | 70 lines | — |

Read all six before proposing anything. The Oxford-comma rule was deliberately removed from the Dutch material on 2026-08-27 (the user writes Dutch with Oxford commas by choice) — do not reintroduce it anywhere.

## The work

### Leg A — Mine the user's own corpus (do this first, and spend real effort here)

The user's own corrections are a labelled dataset of her actual preferences and they beat any generic web research. Critically: **they live in conversations with agents, not in committed files.** She corrects prose in chat, the agent applies the fix, and the commit shows only the result. Transcripts are therefore the primary seam and git history is a weak secondary one. Budget your effort accordingly.

**A1. Transcripts — `portfoliostrategyframework` above all.**

`/Users/esther/.claude/projects/-Users-esther-prog-portfoliostrategyframework/` — 41 session files, ~629MB. Nearly all of the user's externally-facing written work happened here, and this is where the corrections were given. Go deep on it.

Practical constraint: 629MB of JSONL cannot be read into context. Grep for candidate lines, then extract a window around each hit and pull the user message plus the preceding assistant text with `jq`. Report your extraction method so a later pass can repeat it.

Search user-role messages for correction markers. Dutch: `graag niet`, `liever`, `schrijf niet`, `niet zo`, `opgebroken`, `klinkt als`, `dit is geen`, `herschrijf`, `te formeel`, `gewoon "`, `mag weg`, `dit leest`, `Nederlands`. English: `don't write`, `rewrite`, `reads like`, `too formal`, `sounds like AI`, `that's not how`, `simpler`, `plainer`. Then look for the *shape* as well as the keyword: a short user message immediately following a block of agent-written prose and containing a quoted alternative is a correction even when it uses no marker word at all. The anchor case above has exactly that shape.

Secondary transcript sources, lighter pass: `-Users-esther-prog-portbase` (corrections to deck and presentation wording) and `-Users-esther-prog-revintel` (explainer documents written for two specific external readers, Norbert and Wolter). Skip `missioncontrol`, `systems-blog`, and `emotional-coasters` — the user confirms there is nothing useful in those.

**A2. Git history — secondary, low expected yield.**

Check `/Users/esther/prog/portfoliostrategyframework/docs`, the portbase decks, and the revintel explainers for commits where prose was *reworded without changing what it says*. Confound: agents commit under the user's name, so authorship cannot separate human edits from agent edits — rely on the reword-without-rescope heuristic and say so. Do not spend long here. If A1 is yielding well, go deeper on A1 instead.

**Output of Leg A:** a table of before/after pairs, grouped by the defect each one corrects, each tagged EN or NL. For every pair, record which existing rule would have caught it, in which file, and whether that rule's *prescribed fix* matches what the user actually did. A rule that flags the right sentence but prescribes the wrong rewrite (as §6.6 does for the anchor case) counts as a miss, not a hit. Uncaught and mis-prescribed cases are your priority list. Report how many candidates you reviewed and how many were usable.

### Leg B — External research, corroborating and extending Leg A

This leg supports Leg A rather than leading. You are not looking for another list of banned words; you are looking for structure and mechanism.

- **The overcorrection signature.** Current models have largely learned to avoid the 2023–2024 tells. The failure mode has moved toward over-compression: fragmentation, staccato rhythm, telegraphic constructions, dropped finite verbs, nominalisation stacks, standalone stub sentences used for emphasis ("That's the point." / "Dat is de kern."), the profound one-liner cadence. Characterise this properly, in both languages.
- **Test whether existing rules are causing it.** Specific hypothesis worth serious attention: the hard "never use em dashes" rule may be *producing* the fragmentation. An em dash is the natural joint for exactly the construction in the anchor case; forbid it without supplying a replacement joint and the model reaches for a full stop instead, which yields fragment-plus-stub. The timeline is suggestive — em dashes were hardened to "never" on 2026-07-13 and the anchor case appeared in August — though that is circumstantial, not evidence. Test it against the Leg A corpus: did fragment-type corrections rise after mid-July? If the hypothesis holds, the fix is loosening or reshaping an existing rule, not adding a new one. Audit the other absolute prohibitions (colons, semicolons, inline emphasis) for the same displacement effect.
- **Dutch-specific grounding.** Anglicism patterns, tangconstructies, NL prose norms. Onze Taal, Taaladvies.net, Dutch editorial style guidance. Distinguish "AI tic" from "the user simply prefers otherwise" — both belong in the references but labelled differently, because the first generalises and the second does not.

Cite sources. The user's standing research preferences (see the `research` skill) apply: comprehensive, no length caps, find-all over top-N, do not impose a taxonomy in advance.

### Leg C — Restructure, consolidate, and fix parity

This is where the refresh earns its keep.

1. **Collapse the fragment family into one rule with a diagnostic test.** NL §6.5 / §6.6 / §6.7 and EN §2.8 all describe one defect: a clause that asks the reader to supply a verb, a subject, or an unpacked noun. Write a single rule whose *test* catches the family — something along the lines of "does the reader have to mentally supply a word to make this a sentence? then supply it" — then list the surface forms beneath it as examples: infinitive head, resumptive stub, bare auxiliary, gerund litany, hyphen-stacked noun, left dislocation split by a full stop. The anchor case must be caught by the test itself, not by matching an example. Give the rule a worked rewrite that reaches the user's preferred form (front the finite verb), since §6.6 shows that catching the sentence is not sufficient if the prescription is wrong.
2. **Apply the same treatment wherever else enumeration has fragmented one idea.** Audit for it. The fragment family is the clearest case, not necessarily the only one.
3. **EN/NL parity.** Produce a parity table of every rule against both references. Resolve each asymmetry deliberately: mirror it, or record why it is legitimately language-specific. Expect the English side to need substantial additions given that it missed the May work.
4. **Three-way drift.** `proof/references/*`, `writing-foundations/references/antipatterns_*`, and the `writing-style-editor` checklist overlap and have diverged. Decide whether the generative side should *reference* the proof side rather than duplicating it, and justify the choice. Three copies of one rule set is three places for the next patch to be forgotten.
5. **Distribution: make good writing the default, not a post-hoc pass.** The anchor sentence came from an agent in a different repo that was not running `proof` at all. Post-hoc editing cannot fix what generation keeps producing, in either language.

   Write up a recommendation for how the `writing-foundations` skill (and the relevant antipattern rules) could apply **automatically to every agent that writes prose**, across languages and across repos, without the user invoking anything. Consider at minimum: the global `~/.claude/CLAUDE.md`, a Claude Code output-style, a `UserPromptSubmit` or `PreToolUse` hook, a slim always-on rule set distilled from the full references, skill auto-invocation via description tuning, and anything the plugin itself could ship. For each option assess: does it fire reliably, what does it cost in context on every turn, does it reach agents in repos without the plugin installed, and how does it degrade on the other platforms the converter targets (OpenCode, Codex, Gemini).

   Note the real tension: `writing-foundations` is ~60KB across two reference files and no always-on mechanism can carry that. Part of the recommendation must be *what the distilled always-on subset contains* — the smallest rule set that would have prevented the anchor case and the most common defects Leg A surfaces — and how it hands off to the full references when a prose task warrants them.

   Recommend one option with its tradeoffs and sketch the distilled rule set concretely enough to evaluate. **Do not implement any of it.**

### Leg D — Validate

Hold out roughly 20% of the Leg A before/after pairs, chosen *before* you write any rules, balanced across EN and NL. After revising the references, check for each held-out pair whether the new rules flag the original and whether the prescribed fix resembles what the user actually did. Report the hit rate honestly, including misses and mis-prescriptions. A rule set that scores well on the pairs it was written from and poorly on held-out pairs has overfitted — say so plainly if that happens rather than adjusting the holdout.

## Output contract

Work on a dedicated branch off `main`: `feat/writing-style-refresh-2026`. Do not use `feat/prompt-research-skills` — other sessions work there.

Produce:

1. `docs/research/2026-08-27-ai-writing-patterns-refresh.md` — research findings: the Leg A corpus table with extraction method, Leg B findings with citations including the verdict on the em-dash hypothesis, and Leg D validation results including misses.
2. `docs/brainstorms/writing-style-refresh-2026.md` — the proposal: rules to add, merge, rewrite, or delete, each carrying evidence from Leg A or Leg B; the EN/NL parity table; the three-way drift decision; and the Leg C.5 distribution recommendation with its distilled rule set. Flag anything you are unsure about rather than deciding it silently.
3. **The revised reference files, committed on the branch**, so the morning review is a diff rather than a reading assignment. Keep commits granular and separated by concern (consolidation, additions, parity fixes) so individual pieces can be reverted.

## Constraints

- Repo conventions are in `AGENTS.md`. Read it. Commit prefixes classify by intent, not file type: the reference files are product code, so use `feat:` or `fix:` with a narrow scope (`proof`, `writing-style`, `writing-foundations`), never `docs:`.
- Never hard-wrap prose in markdown. One paragraph is one line.
- No `Co-Authored-By` lines in commits.
- Run `bun run release:validate` if you touch `.claude-plugin/` or plugin manifests. Pre-existing drift can make it fail on clean HEAD; do not hand-bump versions to make it pass.
- The reference files are read by agents at runtime, not by humans for pleasure. A sharp diagnostic test beats a thorough essay. If the refresh makes the files meaningfully longer, justify the growth or cut something — given the accretion history, net shrinkage would be a good outcome.
- Where the corpus shows a genuine conflict between the user's preference and general good style, follow the user's preference and note the conflict in the proposal.
