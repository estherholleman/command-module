# Refresh the writing-style references (EN + NL) — 2026 round

You are picking up a research-and-revision task in `/Users/esther/prog/command-module`. Work autonomously; the user is asleep and will review your output in the morning. Everything you need is below.

## The problem

The writing-style references that power the `proof` skill and the `writing-style-editor` agent were written in July 2025. They catalogue the tics of that model generation: `delve`, `tapestry`, "it's not X — it's Y", em dashes, stakes inflation. Current models have largely learned to avoid those. The tics have moved, and the current signature is the *overcorrection*: over-compression, fragmentation, staccato rhythm, elliptical stubs, sentences broken into pieces where one well-formed sentence would carry the thought.

### The anchor case

An agent produced this Dutch sentence in a strategy document:

> "Bepalen waar de bron van waarheid voor de strategiedata hoort te liggen en wie welke laag beheert. Dat is de vraag."

The user's correction: *"graag niet (erg opgebroken), gewoon 'de vraag is waar de bron van waarheid voor de strategiedata hoort te liggen, en wie welke laag beheert.' bijvoorbeeld."*

Diagnosis: the first half is a **zinsfragment** — an infinitive phrase with no finite verb and no subject. The second is a **resumptive pointer sentence**. Together they form a left dislocation (linksdislocatie) that has been mis-punctuated as two sentences; grammatical Dutch would join them with a comma. The user's preferred fix avoids the dislocation entirely by fronting the finite verb.

### Why this case matters more than the sentence itself

Three existing rules nearly catch it and none does:

- `writing-style-nl.md` §6.5 (Verkapte zinnen) covers fragments, but scoped to fragments after a comma beginning with *wat / wanneer / indien*.
- §6.6 (Infinitief-koppen) covers infinitive heads, but prescribes "conjugate the verb, give it a subject" — which yields "We bepalen waar…", not the rewrite the user wanted.
- §6.7 (Kale hulpwerkwoorden) covers a neighbouring but different defect.
- The English side has §2.8 (Gerund Fragment Litanies), which is the same family again, scoped differently.

The references enumerate by **surface form**. Every new surface form slips between the enumerated ones. Adding a fourth fragment rule will not fix that; it will make it worse. The refresh must produce *family-level rules with diagnostic tests*, not more entries in a list.

## Current state

| File | Role | Size |
| --- | --- | --- |
| `plugins/command-module/skills/proof/SKILL.md` | The review workflow: tiering, passes, findings doc | 187 lines |
| `plugins/command-module/skills/proof/references/writing-style-en.md` | English antipatterns | ~14KB |
| `plugins/command-module/skills/proof/references/writing-style-nl.md` | Dutch antipatterns (+ NL-specific §6) | ~23KB |
| `plugins/command-module/skills/writing-foundations/references/antipatterns_to_avoid_bad_writing.md` | Generative-side antipatterns; partly duplicates the proof references | ~28KB |
| `plugins/command-module/skills/writing-foundations/references/writing-principles.md` | Positive craft guidance | ~31KB |
| `plugins/command-module/agents/docs/writing-style-editor.md` | Subagent dispatched by proof; carries its own condensed checklist | 71 lines |

Read all six before proposing anything. The Oxford-comma rule was deliberately removed from the Dutch material in August 2026 (the user writes with Oxford commas by choice) — do not reintroduce it, in either the reference files or the agent checklist.

## The work

### Leg A — Mine the user's own corpus (do this first; it is the highest-signal source)

Generic web research returns generic rules. The user's own corrections are a labelled dataset of her actual preferences. Two seams:

**A1. Claude Code transcripts.** `~/.claude/projects/*/*.jsonl` contains her sessions with agents. Grep the user-role messages for style corrections — Dutch markers like `graag niet`, `schrijf niet`, `liever`, `dit is geen`, `klinkt als`, `opgebroken`, `herschrijf`, `te formeel`, `gewoon "`, and English equivalents (`don't write`, `rewrite this`, `reads like AI`, `too formal`, `this sounds`). For each hit, capture the AI text that triggered it and the correction she gave. These are ground truth. Expect noise; report how many you reviewed and how many were usable.

**A2. Git history of her prose repos.** Candidate locations (verify each exists before assuming): `/Users/esther/prog/portfoliostrategyframework/docs/strategy`, `/Users/esther/prog/portbase/docs`, `/Users/esther/prog/missioncontrol/reports`, `/Users/esther/prog/revintel/docs`, `/Users/esther/prog/systems-blog`, `/Users/esther/prog/emotional-coasters/docs`. Look for commits where prose was *reworded without changing what it says* — the content stayed, the phrasing changed. Those hunks are her editing AI output. Note the confound: agents commit under her name, so authorship does not separate human edits from agent edits; rely on the reword-without-rescope heuristic and say so in your writeup.

Output of Leg A: a table of before/after pairs, grouped by the defect each one corrects. Note which existing rule (if any) would have caught each. The uncaught ones are your priority list.

### Leg B — External research on the current-generation signature

Research how AI prose has changed between the 2023–2024 generation and now. You are looking specifically for the overcorrection signature, not another list of banned words. Candidate directions:

- Fragmentation and staccato rhythm as a tell; the "profound one-liner" cadence; standalone stub sentences used for emphasis ("That's the point." / "Dat is de kern.").
- Compression tics: nominalization stacks, dropped finite verbs, telegraphic constructions that read as broken rather than economical.
- Whether the old rules have become *counterproductive* — e.g. a hard "never use em dashes" rule pushing models toward period-splitting, which produces exactly the fragmentation problem in the anchor case. This hypothesis is worth testing seriously; if it holds, the fix is a rule change, not a rule addition.
- Dutch-specific: anglicism patterns, tangconstructies, and NL prose norms. Useful sources include Onze Taal, Taaladvies.net, and Dutch editorial style guidance. Distinguish "AI tic" from "the user simply prefers otherwise" — both belong in the references, but labelled differently.

Cite sources. The user's standing research preferences (see the `research` skill) apply: comprehensive, no length caps, find-all over top-N, do not impose a taxonomy in advance.

### Leg C — Restructure, consolidate, and check parity

This is where the refresh earns its keep.

1. **Collapse the fragment family.** NL §6.5 / §6.6 / §6.7 and EN §2.8 all describe one underlying defect: a clause that asks the reader to supply a verb, a subject, or an unpacked noun. Write one rule with a general diagnostic test, then list the surface forms (infinitive head, resumptive stub, bare auxiliary, gerund litany, hyphen-stacked noun, left dislocation split by a period) as instances beneath it. The anchor case must be caught by the test, not by an example matching it.
2. **Apply the same treatment wherever else enumeration has fragmented one idea.** Audit for it; do not assume the fragment family is the only case.
3. **EN/NL parity check.** The two references have drifted — some rules exist on one side only, sometimes for good reason (Oxford comma, tangconstructies) and sometimes by accident. Produce a parity table and resolve each asymmetry deliberately.
4. **Three-way drift check.** `proof/references/*`, `writing-foundations/references/antipatterns_*`, and the `writing-style-editor` agent checklist overlap and have drifted apart. Decide whether the generative side should reference the proof side rather than duplicating it, and say why.
5. **Distribution question.** The anchor sentence was produced by an agent in a *different repo* that was not running `proof` at all. Post-hoc editing cannot fix what generation keeps producing. Investigate how the Dutch guidance could reach agents writing Dutch prose outside the proof workflow — global CLAUDE.md, an output-style, a hook, a slim always-on rule set — and recommend one option with its tradeoffs. Recommend; do not implement without approval.

### Leg D — Validate

Hold out a sample of the Leg A before/after pairs (roughly 20%, chosen before you write any rules). After revising the references, check whether the new rules would have flagged each held-out AI original and whether the prescribed fix resembles the correction the user actually made. Report the hit rate honestly, including misses. A rule set that scores well on the pairs it was written from and poorly on held-out pairs has overfitted — say so if that happens.

## Output contract

Work on a dedicated branch off `main`: `feat/writing-style-refresh-2026`. Do not work on `feat/prompt-research-skills` — other sessions use it.

Produce:

1. `docs/research/2026-08-27-ai-writing-patterns-refresh.md` — the research findings: Leg A corpus table, Leg B external findings with citations, and the Leg D validation results including misses.
2. `docs/brainstorms/writing-style-refresh-2026.md` — the proposal: which rules to add, merge, rewrite, or delete, and why. Each proposed change carries evidence from Leg A or Leg B. Flag anything you are unsure about rather than deciding it silently.
3. **The revised reference files themselves**, committed on the branch, so the morning review is a diff and not a reading assignment. Keep the commits granular and separated by concern (consolidation, additions, parity fixes) so individual pieces can be reverted.

Do not implement the Leg C.5 distribution recommendation — write it up and stop there.

## Constraints

- Repo conventions live in `AGENTS.md`. Read it. Commit prefixes classify by intent, not file type: the reference files are product code, so changes to them are `feat:` or `fix:` with a narrow scope (`proof`, `writing-style`), not `docs:`.
- Never hard-wrap prose in markdown. One paragraph is one line.
- No `Co-Authored-By` lines in commits.
- Run `bun run release:validate` if you touch anything under `.claude-plugin/` or plugin manifests. Note that pre-existing drift can make it fail on clean HEAD; do not hand-bump versions to make it pass.
- The reference files are read by agents at runtime, not by humans for pleasure. Terseness with a sharp diagnostic test beats a thorough essay. If the refresh makes the files meaningfully longer, justify the growth or cut something.
- Where the corpus shows a genuine conflict between the user's preference and general good style, follow the user's preference and note the conflict in the proposal doc.
