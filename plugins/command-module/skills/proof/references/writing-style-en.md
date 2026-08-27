# Writing Style: Avoiding AI-Sounding Patterns (English)

These rules describe writing habits that signal AI-generated text. Follow them to produce writing that reads as natural, human prose. The goal is to write *well* by avoiding the lazy defaults that language models fall into.

## Start here: three tests that catch most of it

Word choice is rarely the problem. A proof pass over six earlier documents returned zero hits against the word list in section 1 and dozens against the patterns below. Run these three tests over any text first, and use the rest of this document for the specific cases.

1. **The completion test (elliptical constructions, section 2.8).** Turn the sentence into a yes/no question. If you cannot, because there is no finite verb or no subject to move to the front, it is a fragment. Supply what the reader would otherwise have to guess.
2. **The subtraction test (empty evaluative tails, section 2.9).** Delete the closing clause and reread. If nothing was lost, that clause was a tail. Replace it with the consequence, or cut it.
3. **The reader test (wrong addressee, section 5.9).** Ask of every sentence: could someone who was not present while this document was made understand it? If not, the sentence is addressed to the wrong reader.

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

A clause or standalone sentence that points back at what was just said and tells the reader how to feel about it, without adding information. These sentences are grammatically complete, so the completion test in 2.8 clears them. They fail on rhetoric: if the previous sentence already showed the problem, the tail is redundant, and if it did not, the tail asserts instead of showing.

**Do not write:**
- "Who owns the strategy data is unknown, and that's the problem."
- "The judgement layer is missing entirely, and that's the most serious."
- "That's the point." / "That's the question." / "That's what matters." (as a standalone sentence after the sentence that already said it)
- "..., which is exactly the issue." / "..., and therein lies the difficulty." / "..., and that's the one that hurts most."

**The subtraction test:** delete the tail and reread. "Who owns the strategy data is unknown." Nothing was lost, so the tail did nothing.

**The repair is the consequence, not the verdict.** Say what goes wrong because of it: "Who owns the strategy data is unknown, so nobody can decide which version is authoritative." If you do not know the consequence, cut the tail without replacing it.

**The ranking variant fails twice over.** "And that's the most serious" also drops the head noun and implies a comparison set the reader has to reconstruct. Write both out: "Of the four gaps, the missing judgement layer is the one that makes the tool unusable."

**Where the line is.** A closing clause that points back is legitimate when it adds a real consequence ("..., so the whole count shifts"), draws a genuine contrast, or lands a long passage that has earned the landing. One earned landing per piece is fine. Two or more is the pattern, and it is almost always the second and later ones that should go.

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

---

## 6. General Principles

**Compression is not the goal; being understood is.** The rules above cut a great deal, which tempts overcorrection. Two failures sit equally close: saying too little in too few words, so the reader has to guess, and writing three lines that all say the same thing. Be specific without being long-winded. If a sentence has to be longer to be right, let it be longer.

**Never replace a punctuation mark with a hole.** When an em dash, colon, or semicolon has to go (sections 4.1 and 4.2), put a real sentence in its place, not a full stop with a fragment after it. Banning one mark pushes the impulse to the next one: to colons, to loose sentence pieces, and to the evaluative tail in 2.9. After every removal, check that what is left is still a whole sentence.

**Vary sentence length deliberately.** A monotone rhythm is as much a giveaway as any word choice. Mix short and long. Let some sentences breathe. Cut others to the bone.

**Be specific.** Instead of "a seamless shift in the digital landscape," write "companies moved from email campaigns to TikTok ads almost overnight." Specifics are harder to fake and more useful to read.

**Earn your structure.** If the content is naturally list-shaped, use a list. If it's naturally flowing prose, write prose. Do not impose structure for the sake of appearing organized.

**Write with texture.** Include a concrete detail, a small aside, or an unexpected observation. These are the things that make writing feel like it came from a mind that has actually experienced the world.

**Omit needless words.** If a sentence works without "important," "crucial," "significant," or "key," leave them out. If a transition word adds nothing ("Furthermore," "Moreover," "Additionally"), cut it and just start the next sentence.

**Do not announce what is about to happen.** Just do it. No "In this section, we will explore..." No "Let's take a closer look at..." Start with the substance.

**When in doubt, read it aloud.** If a sentence sounds like something no one would actually say to another person, rewrite it until it does.
