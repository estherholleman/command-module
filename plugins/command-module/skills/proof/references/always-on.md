# Always-on prose rules

The smallest rule set that catches the most common defects, sized to sit in a global instruction file and fire on every turn of every agent, in every repo, whether or not this plugin is installed.

This is the canonical copy, kept under version control so it is reviewable in a diff. The live copy lives under a `## Prose Style` heading in the user's global `~/.claude/CLAUDE.md`, which is user-global and gitignored. When this file changes, sync it there.

Every rule below is derived from a measured defect in the user's own corpus, not from a generic AI-writing list. The full rules, boundaries and worked repairs are in `writing-style-en.md` and `writing-style-nl.md`; this is the subset worth paying for on every turn.

---

## Prose Style

Applies to all prose you write, English and Dutch alike, in documents and in chat.

- **Every sentence needs a subject and a finite verb.** If the reader has to supply a word before the sentence parses, supply it yourself, and lead with the finite verb of the actual claim. Not "Bepalen waar de bron van waarheid hoort te liggen. Dat is de vraag." but "De vraag is waar de bron van waarheid hoort te liggen." Not "We bepalen waar...", which changes the claim. Not "en dat is de ernstigste" but "en dat is de ernstigste tekortkoming".
- **Never weld a commenting clause on with a comma.** The shape is `[claim], en/and [die/dat/daar/hier/deze/ze/het/that/this/it/there] [any verb]`: "..., en daar zit het probleem", "..., en dat maakt de vondst sterker", "..., en die is groter dan hij lijkt", "..., and that's the point". Test by subtraction, rereading both the sentence before it and the one after: if nothing is lost either way, cut it, or write the consequence instead ("..., waardoor niemand kan bepalen welke versie leidend is"). Where the tail carries the real claim, promote it: not "De tegenzetten zijn A en B, en die horen samen" but "De tegenzetten, A en B, vullen elkaar aan."
- **Name the relation, or split the sentence.** Wherever a comma plus "en"/"and" is followed by a full independent clause, say what the relation is: cause, contrast, consequence, elaboration. Not "De machtiging is een vijfde greep, en de eigen datalagen kenden hem al" but "..., die in de eigen datalagen al terug te vinden was." If the relation cannot be named, the second half needs its own sentence. Plain "en" is for genuinely parallel halves.
- **Write for the person who will read it,** not the person you are talking to. No commentary about this conversation, no process or version history, no pointers to documents they have not seen, no bare identifiers where a description belongs ("T154", "Vraag C", column "G"), no in-group jargon. Explain each point where it appears. Do not simplify away a precise term: vague is worse than unfamiliar.
- **No em dashes.** Rebuild the sentence when you remove one. Do not leave a full stop with a fragment after it, and do not swap in a colon.
- **Say it the way you would say it aloud.** Not "Er werd genoemd dat..." or "It was noted that...", but who said it, or just the fact.
- **Being understood beats being brief.** A sentence may be longer if that makes it right. Do not compress to look terse.

For a document someone else will read, load the `writing-foundations` skill and the matching `proof` reference before drafting.
