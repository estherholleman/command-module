# Writing Style: Avoiding AI-Sounding Patterns (English)

These rules describe writing habits that signal AI-generated text. Follow them to produce writing that reads as natural, human prose. The goal is to write *well* by avoiding the lazy defaults that language models fall into.

## Start here: six tests that catch most of it

Word choice is rarely the problem. A proof pass over six earlier documents returned zero hits against the word list in section 1 and dozens against the patterns below. Run these six tests over any text first, and use the rest of this document for the specific cases.

1. **The completion test (elliptical constructions, section 2.8).** Turn the sentence into a yes/no question. If you cannot, because there is no finite verb or no subject to move to the front, it is a fragment. Supply what the reader would otherwise have to guess.
2. **The subtraction test (empty evaluative tails, section 2.9).** Delete the closing clause and reread both the sentence before it and the one after it. If nothing was lost either way, that clause was a tail. Replace it with the consequence, promote it to the main predicate, or cut it.
3. **The relation test (coordination, section 2.10).** Wherever a comma plus "and" is followed by a full sentence, name the relation between the halves. If you can name it, use the word for it. If you cannot, it belongs in its own sentence.
4. **The reader test (wrong addressee, section 5.9).** Ask of every sentence: could someone who was not present while this document was made understand it? If not, the sentence is addressed to the wrong reader.
5. **The directness test (sections 2.11 and 2.12).** If a sentence opens with *What ...* and withholds its subject until after *is* or *are*, recast it as subject-verb-rest. If it uses a verb of change (*changes*, *affects*, *shifts*), ask which way it goes and put that answer in the verb. In practice this was the most common fault of all: one document carried the detour seventy-five times.
6. **The precision test (empty pointers and undefined terms, section 5.10).** Ask of every sentence: can the reader recover who, what, where, when, how, and why from it? If it says "the third route," "the building blocks," "partners," "elsewhere," or uses a term that is only explained later, it is a placeholder. Write out the name, the number, the date, or the mechanism, and define the term where it stands.

---

## 1. Banned Words and Phrases

The following words and phrases have become so strongly associated with AI output that their mere presence raises suspicion. Do not use them unless the user explicitly includes them in their input or they are genuinely the best word for the context.

**Verbs to avoid:** delve, leverage (as verb), utilize, harness, streamline, underscore, bolster, embark, navigate (as metaphor), unveil, unlock, unleash, foster, elevate, pioneer, showcase, captivate, revolutionize, democratize, spearhead.

**Adjectives to avoid:** pivotal, robust, innovative, seamless, cutting-edge, groundbreaking, transformative, holistic, multifaceted, comprehensive, meticulous, commendable, invaluable, unwavering, compelling, vibrant, noteworthy, load-bearing (as metaphor).

**Nouns to avoid:** tapestry, landscape (as metaphor for a field/domain), realm, synergy, paradigm, ecosystem (outside biology), testament, endeavor, beacon, intersection (as metaphor), underpinnings.

**Filler phrases to avoid:**
- "In today's fast-paced / ever-evolving / rapidly shifting world..."
- "It's important to note that..." / "It bears mentioning..." / "It's worth noting that..."
- "In conclusion" / "In summary" / "To sum up" / "In essence"
- "At the end of the day"
- "Let's unpack this" / "Let's break this down" / "Let's dive in" / "Let's explore"
- "Here's the thing:" / "Here's the kicker:" / "Here's where it gets interesting:"
- "Think of it as..." / "Think of it like..."
- "Imagine a world where..."
- "Honestly, ..." / "To be honest, ..." / "Let's be honest, ..." / "I'll be honest:" (false-candor openers -- the word "honest" as a credibility prop is itself a tell)

**Use instead:** everyday equivalents. "Explore" instead of "delve." "Use" instead of "utilize." "Complex" instead of "multifaceted." "Important" instead of "pivotal." If reaching for a fancy synonym, default to the plainer word.

---

## 2. Sentence Structure Patterns to Avoid

### 2.1 The "It's Not X -- It's Y" Construction

The single most recognizable AI writing pattern. AI uses it to create false profundity by framing everything as a surprising reframe.

**Do not write:**
- "It's not a bug. It's a feature."
- "This isn't about speed -- it's about direction."
- "The problem isn't resources. It's priorities."
- "Not because X, but because Y."

One instance per entire piece might be acceptable if the reframe is genuinely surprising. More than one is a pattern. The causal variant ("not because X, but because Y") and the cross-sentence variant ("The question isn't X. The question is Y.") are equally flagged. Avoid all of them by default.

**The appended-correction variant belongs here too**, where the negation is tacked on the end to correct a misreading the reader never had: "There are three kinds of presentation, not two." Write "There are three kinds of presentation." The negation earns its place only when the text really did say two earlier, and then the correction deserves a sentence of its own.

**Instead:** state both sides plainly. "A is common, but B works better." "Most teams focus on speed. Accuracy matters more here." The contrast does the work on its own without the negation-then-reveal structure.

### 2.2 The Dramatic Countdown

Negating two or more things before revealing the real point.

**Do not write:**
- "Not a bug. Not a feature. A fundamental design flaw."
- "Not ten. Not fifty. Five hundred."

### 2.3 Self-Posed Rhetorical Questions

Asking a question nobody asked, then immediately answering it.

**Do not write:**
- "The result? Devastating."
- "The worst part? Nobody saw it coming."
- "So what does this mean? It means..."

### 2.4 Anaphora Abuse

Repeating the same sentence opening three or more times in quick succession.

**Do not write:**
- "They could expose... They could offer... They could provide... They could create..."
- "It means better X. It means better Y. It means better Z."

### 2.5 Tricolon / Rule-of-Three Overuse

Using groups of three everywhere. One tricolon per piece is fine. Three tricolons in one piece is a pattern.

**Do not write:**
- "...clarity, precision, and impact" right after "...speed, scale, and flexibility."

If there are two things, say two. If there are four, say four. Do not force everything into groups of three.

### 2.6 Participial Phrase Tacking

Ending sentences with a present-participle phrase ("-ing") that adds shallow analysis.

**Do not write:**
- "The project launched in 2019, contributing to the region's cultural development."
- "Revenue grew 40%, highlighting the company's strong market position."
- "She published widely, underscoring her commitment to the field."

These phrases almost never say anything that isn't already obvious from the main clause. Cut them.

**Instead:** if the participial phrase actually contains new information, promote it to its own sentence. "Revenue grew 40%. That growth came almost entirely from the Asian market." If it does not contain new information, delete it.

### 2.7 False Ranges

"From X to Y" where X and Y are not actually on a meaningful spectrum.

**Do not write:**
- "From innovation to cultural transformation."
- "From beginners to experts." (unless genuinely describing a spectrum)

### 2.8 Elliptical Constructions: The Reader Supplies Nothing

AI compresses by leaving something out that the reader has to put back: a finite verb, a subject, or a noun squeezed into a stack. Every few months a new surface form of this appears, and each one is the same defect. Use one test rather than a rule per form.

**The completion test.** Turn the sentence into a yes/no question by moving the finite verb to the front. If you cannot, because there is no finite verb or no subject to ask about, it is a fragment. If you have to unpack a compound noun before the sentence parses, it is a noun stack. Either way the writer does that work, not the reader.

**The repair: lead with the finite verb of the actual claim.** This is the step that most often goes wrong. Conjugating the existing head verb is not enough, because it changes the claim. "Working out where the source of truth belongs" is not the same claim as "the question is where the source of truth belongs."

- "Working out where the source of truth for the strategy data belongs, and who owns which layer. That's the question." -> better: "The question is where the source of truth for the strategy data belongs, and who owns which layer."
- Not: "We will work out where the source of truth belongs." That conjugates the verb but turns an open question into a plan of action.

Note that the example stacks two defects: a fragment plus an evaluative tail (see 2.9). The completion test catches the first half and the subtraction test catches the second. Run both, because each one clears the other half.

**Surface forms, all the same defect:**

- **Gerund litany.** "Fixing small bugs. Writing straightforward features. Implementing well-defined tickets." -> better: "The easy work is fixing small bugs, writing straightforward features, and implementing well-defined tickets."
- **Verbless connector fragment**, opening with *which*, *when*, *if*, *consistent with*, *in line with*. "..., which consistent with the earlier observations." -> better: "This matches what we saw earlier." / "... when available." -> better: "... when it becomes available."
- **Bare auxiliary at the end.** "... before activation can." -> better: "... before we can switch it on." In longer sentences where the main verb has already appeared ("he wants to, but can't"), this is fine; the trap is short standalone clauses, especially at the end of a bullet.
- **Elided head noun.** "and that's the most serious" -> the most serious what? Write the head noun out and name what you are comparing against.
- **Hyphen noun stacks.** "last-year data" -> "data from last year"; "the broken-carriage incident period" -> "the period when a carriage was broken"; "pre-deploy test checklist" -> "the checklist we run before shipping to production". One compound is normal English; from the second hyphen on, take a part out and put it back with a preposition or a relative clause.
- **Bare label as a heading.** A heading or line ending in a colon with no sentence after it ("Completion status:", "The core:"), or one that names only a category. Start at the substance.
- **Empty run-up before a colon.** A lead-in phrase that introduces the sentence without asserting anything, and is not a sentence itself: "All or almost all: the investment only pays back if nearly everyone joins." -> better: start at "The investment...". Same test: if the run-up is not a sentence and says nothing the main clause does not already say, cut it.

### 2.9 Empty Evaluative Tails

A second predicate bolted on with a comma and a conjunction, taking a backward-pointing pronoun as its subject, that only comments on what was just said. The shape is `[claim], and [that/this/those/it/there] [predicate]`, the locative form ('there lies', 'therein') included. These sentences are grammatically complete, so the completion test in 2.8 clears them. They fail on rhetoric: if the previous sentence already showed it, the tail is redundant, and if it did not, the tail asserts instead of showing.

Do not watch only for "that's the problem" and "which is the point". Any predicate can sit here, and most real cases use some other verb.

**Do not write:**
- "Who owns the strategy data is unknown, and that's the problem."
- "The judgement layer is missing entirely, and that's the most serious."
- "That's the point." / "That's the question." / "That's what matters." (as a standalone sentence after the sentence that already said it)
- "..., which is exactly the issue." / "..., and therein lies the difficulty." / "..., and that's the one that hurts most."
- "..., and that makes the finding stronger." / "..., and it's bigger than it looks." / "..., and that's not a drafting problem but the finding itself."

**The subtraction test, run in both directions.** Delete the tail and reread both the sentence before it and the sentence after it. "Who owns the strategy data is unknown." Nothing was lost, so the tail did nothing. The second direction is needed because a tail can also point forward: it announces what the next sentence proves, and the redundancy only shows once you read on.

**The repair is the consequence, not the verdict.** Say what goes wrong because of it: "Who owns the strategy data is unknown, so nobody can decide which version is authoritative." If you do not know the consequence, cut the tail without replacing it.

**The announcing variant: set out two things, then attach the relation with "and they ...".** The shape is `[X] is/are [A] and [B], and they [relation]`, usually followed by a colon carrying the justification. The middle piece says in advance what the justification then demonstrates, so it gets in the sentence's way. It also reads chopped: two flat assertions where one belongs.

- Not: "The counter-moves are reciprocity and structuralisation, and the two go together: forcing consent without reciprocity undermines the very neutrality that justifies the consent."
- Better: "The counter-moves, reciprocity and structuralisation, depend on each other. Forcing consent without reciprocity undermines the neutrality that justifies the consent."

**Here the repair is promotion, not deletion.** The relation is the real claim; listing A and B was the run-up. Put the relation in the main predicate and turn the list into an appositive between commas. Or drop the first half entirely and start at the justification. Choose on what the reader does not yet know: if A and B are already familiar, cut the announcement.

**The ranking variant fails twice over.** "And that's the most serious" also drops the head noun and implies a comparison set the reader has to reconstruct. Write both out: "Of the four gaps, the missing judgement layer is the one that makes the tool unusable."

**Where the line is.** A closing clause that points back is legitimate when it adds a real consequence ("..., so the whole count shifts"), draws a genuine contrast, or lands a long passage that has earned the landing. One earned landing per piece is fine. Two or more is the pattern, and it is almost always the second and later ones that should go.

### 2.10 Coordination Where Subordination Belongs

Two full sentences welded together with a comma and "and", with the relation between the halves left unstated. Each half is an equally flat assertion, nothing is subordinated, so the reader has to work out why the second half is there at all. A run of these reads chopped: no hierarchy, just accumulation.

**Do not write:**
- "The authorisation is a fifth hold, and the internal data layers already knew it."
- "The count no longer adds up, and the source was replaced last month."
- "The model has one binding mechanism, and the June note names three."

**The relation test.** Name the relation between the two halves. Is it cause, consequence, contrast, condition, time, or elaboration? If you can name it, use the word for it (*because*, *so that*, *while*, *although*, *which*). If you cannot name it, the second half belongs in its own sentence, or does not belong at all.

- "The authorisation is a fifth hold, and the internal data layers already knew it." -> better: "The authorisation is a fifth hold, one the internal data layers already recorded." (elaboration, so an appositive)
- "The count no longer adds up, and the source was replaced last month." -> better: "The count no longer adds up because the source was replaced last month." (cause)
- "The model has one binding mechanism, and the June note names three." -> better: "The model has one binding mechanism, while the June note names three." (contrast)

**When "and" is right.** Where the halves genuinely are parallel and equal: "He called the client and she sent the quote." There is no relation to name because the two sit side by side, which is what "and" is for. It goes wrong the moment the second half explains, contradicts, or supports the first.

**A whole-document check:** count the coordinating joins (`, and`, `, but`) against the subordinating ones (*because*, *so that*, *while*, *although*, *since*). If the ratio leans heavily toward coordination, the prose has flattened and some of those relations need naming.

---

### 2.11 Sentences That Detour Around Their Own Subject

A sentence that opens with *What ...* and only reaches its subject after *is* or *are* puts a detour in front of the claim. The reader waits for the verb before learning who or what is doing anything. The construction is grammatical, which is why it survives revision, and it multiplies: writers who reach for it once reach for it in every paragraph.

**Don't write:**
- "What's missing is the third step."
- "What follows from the table is that three of the eight have a model running."
- "What AI does change is how cheap it is to build around us."
- "What isn't there is the demand." (a second fault stacks here: the sentence never says whose demand, for what, or why it matters)

**Write instead** in ordinary order, subject first: "The third step is missing." "The table shows that three of the eight have a model running." "AI does lower the cost of building around us."

**The detour test.** Recast the sentence as subject, verb, rest. If the claim survives unchanged, the detour was doing nothing. If the claim shifts, the construction was doing real work and can stay.

**Where the construction is right.** For a contrast that genuinely carries the emphasis: "What disappears is the people, while the reporting obligation stays." The trap is repetition. In a document with a fixed paragraph opener ("What follows from the table is that ..."), the construction appears dozens of times without the writer noticing, and then it reads as a template. See also 2.4 on anaphora.

### 2.12 The Verb That Doesn't Name the Direction

*Change*, *affect*, *impact*, *shift* and *matter* say that something happens without saying which way it goes. Usually the writer knows the direction and wraps scaffolding around it instead: *one thing*, *namely*, *in two ways*, *is twofold*. The scaffolding costs words and returns nothing to the reader.

**Don't write:**
- "AI changes one thing, namely the cost of building it yourself."
- "This affects our position."
- "The new rule impacts submissions in two ways."

**Write instead** the verb that carries the direction, which makes the sentence shorter and says more: "AI lowers the cost of building it yourself."

**The direction test.** Ask of every verb of change: up or down, faster or slower, more or less, and for whom? If there is an answer, put it in the verb. If there is none, that absence is the real uncertainty and it belongs in the sentence: "Whether the rule improves or degrades submissions depends on who fills in the field."

---

## 3. Paragraph and Composition Patterns to Avoid

### 3.1 Uniform Paragraph Shape

Every paragraph running the same template at the same length: topic sentence -> supporting evidence -> summary sentence, each one wrapping up neatly. Humans are messier; they rant, digress, and circle back. Let the content dictate the shape. Some paragraphs should start with the conclusion and work backward, some should build toward a point, and some should be a single observation that stops. Occasionally start with an example and let the reader work out the principle. Break the rhythm with a one-sentence paragraph or a longer, denser one.

### 3.2 The Signposted Conclusion

Do not announce that the text is concluding. No "In conclusion," no "To sum up," no "In summary," no "And so we return to where we began." The reader can feel when a piece is ending. Just end it.

### 3.3 Fractal Summaries

Do not preview what is about to be said, say it, then summarize what was just said -- at every level of the document. Say things once.

### 3.4 The Dead Metaphor

If a metaphor is introduced, use it once or twice and move on. Do not return to the same metaphor in every subsequent paragraph. Do not build the entire piece around one metaphor.

### 3.5 One-Point Dilution

If the argument has one main point, make it in 500 words, not 3,000. Do not pad a single thesis by restating it with different metaphors and examples across many sections.

### 3.6 "Despite Its Challenges..."

The rigid formula: acknowledge problems -> immediately dismiss them -> optimistic ending. If discussing challenges, actually engage with them. Do not use them as a rhetorical trampoline to bounce back to optimism.

**Instead:** if something has real problems, sit with them. Explain why they are hard. It is fine to end a section on an unresolved tension. Readers trust writing that acknowledges difficulty more than writing that always finds a silver lining.

### 3.7 Too Many Lists

AI turns everything into a bulleted list. Sometimes a list is the right shape, but when every paragraph contains one the effect disappears and the argument stops connecting. Use lists sparingly and write the rest as running prose.

### 3.8 Historical Analogy Stacking

Do not rapid-fire list historical companies or technologies to build false authority ("Apple didn't build Uber. Facebook didn't build Spotify. Stripe didn't build Shopify..."). One well-chosen example is stronger than five shallow ones.

---

## 4. Punctuation and Formatting Patterns to Avoid

### 4.1 Em Dashes: Never Use Them

Do not use the em dash (the `—` character). It is the single most recognizable signal of AI-generated text: AI reaches for it at many times the rate of human writers. Whatever an em dash would do, another mark does more cleanly, so use that instead. Treat every `—` as something to remove.

**Instead:** use commas for soft asides, colons for explanations, periods for hard pivots, and parentheses for genuine tangents. Each has a different rhythm. Pick the one that matches the weight of what is being said.

This rule is about the em dash (`—`) specifically. The hyphen (`-`) in compound words and the en dash (`–`) in number ranges are fine.

**Where the replacement goes wrong.** An em dash usually joins two halves that genuinely belong together. Swap it for a full stop without rebuilding the sentence and a fragment is left behind ("... who owns which layer. That's the question."); swap it for a colon and rule 4.2 is broken instead. Rebuild the sentence: lead with the finite verb and make one whole sentence, or two whole sentences. Run the completion test from 2.8 after every removal.

### 4.2 Colons and Semicolons as Sentence Glue

AI uses `:` and `;` to weld two independent clauses together, with the second explaining or refining the first, and it uses colons for rhetorical emphasis ("Here's the thing:" / "There's a catch:" / "Think about it:"). Both read stiff and make sentences longer than they need to be. Start a new sentence, or use a comma if the grammar allows.

- "The fix works: all 23 routes now return plausible values." -> better: "The fix works. All 23 routes now return plausible values."
- "We lowered the estimate; the original was too high." -> better: "We lowered the estimate because the original was too high."

Still fine, with no obligation to rewrite:
- A real list: "We did three things: A, B, and C."
- After a label or heading: "Period: 1-5 May", "Status: in production".
- Times, paths, and code: "at 14:30", `path/to/file:42`.

**The repair is usually the relation, not the full stop.** A colon between two whole sentences almost always hides a relation you can name: *because*, *since*, *so that*, *while*. "Liability does not move with it: the insurer writes that the forwarder stays liable" becomes "Liability does not move with it, because the insurer writes that the forwarder stays liable." That is the same relation test as in 2.10, and it applies here too. If you cannot name the relation, then use the full stop.

**The test:** if the text on both sides of the `:` or `;` reads as a standalone sentence, use a full stop and start a new one. Semicolons have almost no place in modern business prose; cut them by default.

### 4.3 Bold-First Bullets

When writing bullet points, do not start every item with a bolded keyword followed by a colon and explanation. This is one of the most recognizable AI formatting patterns.

**Do not write:**
- **Security**: Environment-based configuration...
- **Performance**: Lazy loading of expensive...
- **Scalability**: Horizontal scaling with...

Write bullet points as normal sentences instead.

### 4.4 Excessive Markdown Formatting

Do not use bold emphasis on every key term. Do not use headers for every sub-point. Do not turn everything into a structured, hierarchical document when flowing prose would be more natural.

### 4.5 Curly/Smart Quotes Inconsistency

Be consistent with quotation marks throughout. Do not mix curly and straight quotes in the same document.

### 4.6 Inline Bold and Italic for Emphasis

Do not bold or italicize individual words inside a sentence for emphasis ("their **own** screens," "this is *not* optional"). AI leans on inline emphasis to inject drama the sentence should carry on its own. Let word choice and sentence structure do the work. Reserve bold for genuine labels or headings, and avoid italics for emphasis entirely in stakeholder-facing prose.

---

## 5. Tone Patterns to Avoid

### 5.1 The Perpetual Hedge

Do not present every topic as having perfectly balanced perspectives when one side is clearly stronger. Take positions when the evidence supports them. Vary the level of certainty based on the actual strength of the evidence.

**Instead:** be direct when the evidence is strong. "This approach failed" is better than "this approach may not have achieved optimal outcomes." Save hedging language for situations where the evidence genuinely warrants it.

**A claim about the future is repaired with a source, not with hedges.** When a sentence feels too assertive, the impulse is to add *mostly*, *not necessarily* and *perhaps*, after which it says nothing at all. Say who makes the claim and what it rests on instead: not "AI doesn't necessarily need a strategy of its own" but "The company's own AI vision says AI calls for an acceleration of the current strategy," followed by the cases that support it. Three hedges in two sentences is itself a tell.

### 5.2 Stakes Inflation

Not everything is "fundamentally reshaping how we think about X." Not everything "will define the next era of Y." Match the importance of language to the actual importance of the topic.

### 5.3 False Vulnerability

Do not insert fake admissions of bias or simulated self-awareness for authenticity points. ("And yes, I'm openly biased toward..." / "This is not a rant; it's a diagnosis.") Real honesty is specific and sometimes uncomfortable. Fake honesty is polished and risk-free. The word "honest" (and "honestly") is a specific tell here: announcing candor ("Honestly," "To be honest," "I'll be honest") almost always precedes something that is neither uncomfortable nor risky. Cut the announcement and let the point stand on its own.

### 5.4 Vague Attributions

Do not attribute claims to unnamed "experts," "observers," or "industry reports." If there is a specific source, name it. If not, state the claim directly without the false authority of anonymous experts.

### 5.5 Invented Concept Labels

Do not mint compound labels that sound analytical but aren't established terms -- "supervision paradox," "acceleration trap," "workload creep." If a concept needs naming, earn it by defining and arguing for it. Do not use it as a rhetorical shortcut.

### 5.6 The Pedagogical Voice

Do not default to teacher mode. Do not assume the reader needs hand-holding, metaphors for basic concepts, or an invitation to "think of it like" something simpler. Write for peers.

**Instead:** if a concept genuinely needs an analogy, make it specific and unexpected, drawn from a concrete domain. Introduce it matter-of-factly rather than with "Think of it as..." -- state the comparison directly.

### 5.7 Press-Release Tone

Do not describe people, companies, or initiatives in promotional language ("demonstrated excellence in..." / "commitment to sustainability, customer focus, and prosperity"). Describe what happened; let the reader decide if it was excellent.

### 5.8 Over-Formal Register and Impersonal Reportage

AI writes more formally than the situation calls for, and reaches for a nameless observer where a person or a plain statement belongs. A memo does not have to read like a policy paper, and a write-up of an interview should sound like the person speaking.

**The test:** would you say this sentence out loud to the reader? If not, rewrite it until you would.

**Impersonal reportage is the commonest form.** "It was noted that...", "one observes...", "is deemed to...", "it should be remarked that..." put an anonymous witness between the reader and the fact. Name the speaker, or just say it.

- "It was noted that the lead time is climbing." -> better: "Marije said the lead time is climbing." or simply: "The lead time is climbing."
- "This is intended to substantially reduce the waiting time." -> better: "This makes the waiting time a lot shorter."

**Nominalisation is the second form.** Too many nouns where a conjugated verb would do, usually visible as words ending in *-tion*, *-ment* and *-ance* and as chains of prepositions. "The pursuit of an improvement of customer service remains a priority." -> better: "We want to keep improving customer service." Put the verb back and name who does it.

**Length is not the problem, obscurity is.** A sentence may get longer if that makes it clear. Do not compress to look terse.

### 5.9 Written for the Wrong Reader

The costliest failure in this document, and the one least likely to be recognised as a style tic. The writer addresses sentences to the person the document was made with, while the document is meant for somebody else. A text with this fault is not clumsy, it is unusable: the recipient trips over references to conversations, documents, and abbreviations they have never seen.

**The reader test:** could someone who was not present while this was made understand the sentence without looking anything up? If not, write it out here or cut it.

**Do not write:**
- "First, something to clear up that makes this conversation easier: the fields already exist." -> better: "The service strategy and audience strategy templates already contain the questions and fields that are needed." (The clearing-up was addressed to the person who commissioned the document, not to its reader.)
- "As we discussed earlier..." / "Decision of 2 August" / "In the previous version this said..." / "merged into a single category" -- process history the reader does not know and does not need.
- "As explained in the building-block document." / "See the appendix." -> better: explain it here, even in two sentences. For this reader, a pointer to another document is a closed door.
- "T154 is done." / "Question C: how often should this run?" / "Axis 1", "Axis 2" / column headings "G" and "A" -> better: the description is the name, and the number may follow in brackets at most. A heading called "Question C" should become the question: "How often should this run, and who runs it?"
- Contrastive question-pair headings: "why yes" / "why no" -> better: plain nouns, "advantages" and "drawbacks".
- A category word bolted onto something that is already the name: "IAMconnected Service provider" -> better: "IAMconnected". It is the same move as writing "MCA Service" where everyone says MCA. Use the name the reader knows, with no added classifier.
- In-group jargon nobody outside the team knows: "deck" (write presentations or PowerPoints), and any internal coinage for a concept the reader has never met. For every specialist word, ask whether it appears in the source document the reader does know. If not, use the word that appears there.

**Where this does not apply.** Do not simplify away a technical term that says exactly what you mean. Replacing "capabilities" with "skills" makes the term vaguer, and vague is worse than unfamiliar. The rule is: pick the word that says most precisely what you mean, and explain it once if the reader will not know it. Internal model names and code keys are outside this rule, where precision wins.

### 5.10 Empty Pointers, Undefined Terms, and Meta About Your Own Process

A sentence that reads fine and says nothing. The writer knows what is meant and puts down a pointer or a category instead of the thing itself. The reader can neither check the sentence nor retell it.

**The precision test:** can the reader recover from this sentence who did it, what happened, where, since when, how, and why it matters? Not every element has to appear literally, but as much as possible should be recoverable. If the sentence fails, replace the vague word with the name, the number, the date, or the mechanism, even if the sentence gets longer.

**Three kinds of placeholder:**

- *Empty pointers and categories.* "The third route does not exist in the port yet." -> better: "An interface that lets an AI assistant reach port data on its own exists at none of the port community systems, while the software vendors around the port already have one." Suspect words: the third route, the building blocks, the layer, the gap, the shift, partners, parties outside the chain, adjacent domains, elsewhere, others, some, increasingly, part of, shifts (without from what to what), affects (without along which path), accelerates (without what and how measured).
- *Undefined terms.* "A pilot is cheap now because the documentation and the authorization model are already in place." -> better: "A pilot, an MCP server on the read queries of Cargo Controller and the Vessel Visit API, is cheap now because our four APIs already have OpenAPI descriptions, files that list which questions an API answers, and because the authorization register under MyData already records who may receive which data from whom." Define every term where it first appears, in plain words, the way you would explain it to a colleague over coffee: first what is needed independent of the technology, then how it works in practice today, then what it means for the reader, with an honest caveat where something is uncertain. Headings follow the same rule: a heading must be understandable on its own.
- *Caveats about your own research.* "What this costs has not been estimated." "Whether the terminals are considering the same step has not been established." "How large the gap is, we do not know." These sentences are not about the subject but about the boundary of the writer's work, and they are almost always tacked onto the end of a paragraph, where they weaken the claim before them and give nothing back. Write what you do know. The distinction that matters: uncertainty about the world belongs in the text (*probably*, *presumably*, *expected*), uncertainty about your own measurement does not. If the reader needs to know that a figure is still to be set, name who sets it: "The board decides what the build may cost." Watch what survives such a cut, too: pronouns in the next sentence may have been pointing at the part you removed (see section 6).
- *One word covering several different things.* In one document "AI" stood for the tool that writes software, for the model that fills in form fields, and for the program that fetches data on a company's behalf. Three things doing three different jobs, made invisible by one word. Name the kinds where the word first appears, give each its own name, and keep them apart from there on.
- *Meta about your own process.* "Our research of 7 September for the negative finding on the eight systems." -> better: "For the eight port community systems, nothing about assistant access could be found on their own sites or developer portals." Write nothing about the date on which you checked something, about reviews, corrections, phases, versions, or the conversation in which the text was made. What a check found stays, as a finding about the world. A "when" refers to the subject (the press release, the measurement, the date a rule took effect), never to the writer's work.

**Where this does not apply.** A sentence that deliberately summarizes what is worked out right after it may be short, as long as the elaboration is on the same page. And avoid the opposite failure: a sentence that lists all six elements like a form. The test is whether the reader can retell it, not whether all six words appear.

---

## 6. General Principles

**Compression is not the goal; being understood is.** The rules above cut a great deal, which tempts overcorrection. Two failures sit equally close: saying too little in too few words, so the reader has to guess, and writing three lines that all say the same thing. Be specific without being long-winded. If a sentence has to be longer to be right, let it be longer.

**Never replace a punctuation mark with a hole.** When an em dash, colon, or semicolon has to go (sections 4.1 and 4.2), put a real sentence in its place, not a full stop with a fragment after it. Banning one mark pushes the impulse to the next one: to colons, to loose sentence pieces, and to the evaluative tail in 2.9. After every removal, check that what is left is still a whole sentence.

**After every cut, check that the references still point at something.** Deleting leaves holes more often than writing does. A *that*, *those*, *their* or *it* in the following sentence was pointing at something that is no longer there, while the sentence still parses, so nothing flags the error. A real example: after "For the three remaining platforms it has not been established which sources they name" was cut, what remained was "Their developer documentation is public, so that costs about a day," in which *their* and *that* no longer had an answer. After every cut, reread the two sentences around it and replace any pronoun that has lost its referent with the word itself.

**Vary sentence length deliberately.** A monotone rhythm is as much a giveaway as any word choice. Mix short and long. Let some sentences breathe. Cut others to the bone.

**Be specific.** Instead of "a seamless shift in the digital landscape," write "companies moved from email campaigns to TikTok ads almost overnight." Specifics are harder to fake and more useful to read.

**Earn your structure.** If the content is naturally list-shaped, use a list. If it's naturally flowing prose, write prose. Do not impose structure for the sake of appearing organized.

**Write with texture.** Include a concrete detail, a small aside, or an unexpected observation. These are the things that make writing feel like it came from a mind that has actually experienced the world.

**Omit needless words.** If a sentence works without "important," "crucial," "significant," or "key," leave them out. If a transition word adds nothing ("Furthermore," "Moreover," "Additionally"), cut it and just start the next sentence.

**Do not announce what is about to happen.** Just do it. No "In this section, we will explore..." No "Let's take a closer look at..." Start with the substance.

**When in doubt, read it aloud.** If a sentence sounds like something no one would actually say to another person, rewrite it until it does.
