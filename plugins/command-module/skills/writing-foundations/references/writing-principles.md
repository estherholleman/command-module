# Writing Principles Reference

A medium-agnostic reference for writing craft. Applies to articles, presentations, reports, proposals, guides, marketing copy, and any other prose. Organized by discipline, each section covers what good writing does, how to achieve it, and common failures.

---

## 1. Clarity

The first job of writing is to be understood. Everything else — style, voice, persuasion — depends on clarity.

### Say What You Mean

- **One idea per sentence.** If a sentence has two independent thoughts joined by "and," "but," or a semicolon, consider splitting it. Long sentences aren't inherently bad, but each sentence should do one job.
- **Subject-verb-object as the backbone.** The reader should be able to find who does what within the first few words. Burying the subject behind qualifiers, caveats, and prepositional phrases makes the reader work before the sentence has even started.
- **Concrete over abstract.** "Revenue increased 40%" is clearer than "significant financial improvement was achieved." Whenever a sentence can point to a specific thing instead of a category, it should.
- **Name things directly.** "The tool" is vague. "The parser" is specific. "It" three sentences away from its referent is a guessing game. Repeat the noun rather than force the reader to track a pronoun chain.

### Cut What Doesn't Earn Its Place

- **Every word should do work.** If removing a word doesn't change the meaning, remove it. "In order to" is "to." "At this point in time" is "now." "Due to the fact that" is "because."
- **Qualifiers weaken.** "Quite," "rather," "somewhat," "relatively," "fairly" — these hedge without adding information. Either the thing is true or it needs a specific qualifier ("30% faster" instead of "somewhat faster").
- **Adverbs often signal a weak verb.** "Ran quickly" is "sprinted." "Said loudly" is "shouted." If the verb needs an adverb to do its job, pick a better verb.

### Common Clarity Failures

- Sentences that need to be read twice to understand
- Passive voice hiding who did what ("mistakes were made" — by whom?)
- Jargon used to sound sophisticated rather than to be precise
- Nominalization: turning verbs into nouns ("we performed an analysis" instead of "we analyzed")
- Stacking prepositional phrases ("the impact of the decision on the future of the organization in the context of the market")

---

## 2. Structure

Structure is how you organize ideas so the reader can follow your thinking without effort.

### Document-Level Structure

- **Lead with the point.** The most important information goes first — whether that's a document, a section, or a paragraph. Don't make the reader wade through context and caveats to find the conclusion.
- **Pyramid structure for persuasion:** Claim first, then supporting evidence, then detail. The reader can stop at any depth and still have the key message.
- **Chronological structure for narrative:** When telling a story or explaining a process, time order is the natural structure. Don't jump around unless the jumps serve a purpose.
- **Problem-solution structure for proposals:** State the problem clearly before presenting the solution. The reader needs to feel the pain before they'll value the remedy.

### Section and Paragraph Architecture

- **One topic per paragraph.** The first sentence should signal what the paragraph is about. If a paragraph covers two topics, split it.
- **Paragraphs as units of thought, not units of length.** A one-sentence paragraph is fine for emphasis. A ten-sentence paragraph is fine for developing a complex idea. But most working paragraphs are 3-6 sentences.
- **Transitions between paragraphs should be invisible.** If you need "Furthermore," "Additionally," or "Moreover" to connect paragraphs, the logical flow between them is probably weak. Rearrange the paragraphs so each one naturally leads to the next.
- **Section headings as signposts.** A reader skimming only headings should get the gist of the document. Headings like "Background" and "Discussion" tell the reader nothing. Headings like "Why current auth fails under load" tell the reader exactly what's coming.

### Lists and Bullet Points

- **Parallel construction.** Every item in a list should follow the same grammatical pattern. If the first item starts with a verb, they all start with a verb. If the first is a noun phrase, they all are.
- **Lists for scannability, prose for reasoning.** If the reader needs to understand relationships between ideas, write prose. If they need to quickly find or compare items, use a list.
- **Limit list length.** A list of 3-5 items is comfortable. A list of 12 items needs subgroups or is actually a table.

### Common Structure Failures

- Burying the conclusion at the end after pages of context (the "academic essay" trap)
- Sections that repeat what previous sections said in slightly different words
- Documents that are structured by how the author thought about the topic, not by what the reader needs to know
- Headings that all sound the same ("Overview," "Details," "More Details," "Additional Information")
- Bullet points used as a substitute for thinking through how ideas relate to each other

---

## 3. Voice and Tone

Voice is who the writing sounds like. Tone is the attitude for a specific context. Good writing has a consistent voice with tone that adapts to the situation.

### Finding the Right Register

- **Match the audience.** A technical report for engineers, a strategy memo for executives, and a blog post for customers all need different registers. The content may overlap; the delivery shouldn't.
- **Match the medium.** Presentation slides need punchy, compressed language. Reports can afford more nuance. Emails should be conversational but purposeful.
- **Formal doesn't mean stiff.** Professional writing can be direct and clear without being casual. "We recommend replacing the auth middleware" is formal. "The auth middleware replacement is hereby recommended for consideration" is stiff.
- **Casual doesn't mean sloppy.** Conversational writing still needs structure, clarity, and precision. Dropping formality is not the same as dropping standards.

### Confidence and Hedging

- **State claims directly.** "This approach will reduce latency" is confident. "This approach may potentially help to somewhat reduce latency" is afraid of its own conclusion.
- **Hedge only when genuinely uncertain.** "We believe this is the right direction" is appropriate when it's a judgment call. "We believe the sky is blue" is bizarre hedging.
- **Avoid false authority.** Don't overclaim either. "This will definitely solve all performance issues" invites skepticism. Match confidence to evidence.

### Active Voice as Default

- **Active voice:** "The team shipped the feature." Clear subject, clear action.
- **Passive voice:** "The feature was shipped." Who shipped it? Sometimes that ambiguity is the point, but usually it's just weaker writing.
- **Passive voice has legitimate uses:** When the actor is unknown ("the server was compromised"), when the object is more important than the actor ("the patient was discharged"), or when the actor is obvious and repeating it would be tedious.

### Common Voice Failures

- Writing that sounds like nobody — corporate boilerplate with no personality
- Inconsistent register that shifts between formal and casual within a paragraph
- Hedging every claim until nothing feels definitive
- Trying too hard to sound authoritative, which comes across as pompous
- Using "we" when it's unclear who "we" refers to

---

## 4. Sentence Craft

Sentences are the building blocks. Variety in their length, structure, and rhythm keeps prose alive.

### Rhythm and Variety

- **Vary sentence length.** A long sentence that develops an idea, followed by a short one that lands the point. That contrast creates rhythm. Three long sentences in a row become a slog. Three short sentences in a row become staccato.
- **Front-load important information.** "Despite the three-week delay, the project launched on time" puts the surprise (on time) at the end, which is the power position. "The project launched on time despite the three-week delay" buries the interesting part.
- **The power positions are the beginning and end of a sentence.** Weak words in those positions ("There is," "It is," "however") waste prime real estate.

### Sentence Patterns

- **Simple:** Subject-verb-object. The workhorse. "The parser failed."
- **Compound:** Two independent clauses joined by a conjunction. "The parser failed, and the pipeline stopped." Use when both clauses are equally important.
- **Complex:** A main clause with a dependent clause. "When the parser failed, the pipeline stopped." Use when one idea depends on or qualifies another.
- **Mix all three.** Prose written entirely in simple sentences reads like a children's book. Prose written entirely in complex sentences reads like legal text.

### Connective Tissue

- **Transitions within sentences:** "but," "so," "yet," "because," "although," "while" — small words that signal the relationship between ideas.
- **Transitions between sentences:** Sometimes the connection is implicit if the sentences follow logically. When it isn't, a brief connecting phrase at the start of the next sentence works better than transition words like "Furthermore" or "Additionally," which add syllables without meaning.
- **Repetition as a linking device:** Repeating a key word from the end of one sentence at the beginning of the next creates a chain. "The investigation revealed three failure modes. These failure modes shared a common root cause."

### Common Sentence Failures

- Every sentence starting with the same structure ("We did X. We then did Y. We also did Z.")
- Run-on sentences that pack three ideas into one breathless clause chain
- Sentences that start with "It is important to note that" or similar empty throat-clearing
- Overuse of semicolons to connect loosely related thoughts
- Burying the actual point in a subordinate clause

---

## 5. Persuasion and Argument

When writing needs to convince — proposals, strategy docs, pitches, recommendations — craft serves the argument.

### Building an Argument

- **Claim, evidence, reasoning.** State what you believe, show the evidence, explain why the evidence supports the claim. Missing any one of these three makes the argument incomplete.
- **Strongest argument first.** Don't "save the best for last" — the reader's attention is highest at the start. Lead with your strongest point, then reinforce.
- **Acknowledge counterarguments.** Addressing objections before the reader raises them builds credibility. Ignoring obvious objections makes the writing feel naive or dishonest.
- **One throughline.** A persuasive document should be reducible to a single sentence: "We should do X because Y." If you can't state it that simply, the argument isn't clear yet.

### Evidence and Support

- **Specific beats general.** "Three customers reported this issue in the last week" is more persuasive than "customers have been complaining."
- **Numbers are persuasive when contextualized.** "500ms latency" means nothing without context. "500ms latency, 3x our SLA target" tells a story.
- **Examples make abstract ideas concrete.** After stating a principle, show it in action. The example does half the persuasion work.
- **Authority is earned, not claimed.** Citing relevant experience or data builds authority. Saying "as an expert" or "it is well known that" undermines it.

### Common Persuasion Failures

- All evidence, no argument (data dumps without interpretation)
- All argument, no evidence (opinions presented as conclusions)
- Undermining your own case with excessive hedging
- Trying to prove too many things at once — diluting the main argument
- Assuming the reader shares your context, priorities, or values

---

## 6. Audience and Purpose

Every piece of writing has a reader and a job. Misunderstanding either produces writing that misses.

### Know Your Reader

- **What do they already know?** This determines how much context you need to provide. Over-explaining insults experts; under-explaining loses beginners.
- **What do they care about?** Lead with what matters to them, not what matters to you. An executive cares about outcomes and cost. An engineer cares about implementation and trade-offs. Same project, different lead.
- **What will they do with this?** If they'll make a decision, give them what they need to decide. If they'll implement something, give them what they need to build. If they'll share it with others, make it easy to excerpt.

### Match Writing to Purpose

- **Inform:** Clarity and structure dominate. The reader needs to understand.
- **Persuade:** Argument and evidence dominate. The reader needs to be convinced.
- **Instruct:** Steps and specificity dominate. The reader needs to do something.
- **Narrate:** Pacing and scene dominate. The reader needs to experience something.

Most documents serve multiple purposes, but one dominates. Identify it and let it shape the structure.

### Common Audience Failures

- Writing for yourself instead of your reader (organizing by your thought process, not their needs)
- Explaining things the reader already knows (wastes their time, signals you don't know your audience)
- Skipping things the reader needs to know (assumes shared context that doesn't exist)
- Using the same register for every audience

---

## 7. Medium-Specific Principles

### Presentations and Slides

- **Slides support speech, not replace it.** If the slides are the entire message, they're a document pretending to be a presentation.
- **One point per slide.** The audience processes spoken and visual information simultaneously. Competing messages on screen and from the speaker cause neither to land.
- **Headlines, not labels.** A slide titled "Q3 Results" tells the audience the topic. A slide titled "Q3 revenue exceeded target by 40%" tells them the point. Use the headline to deliver the message.
- **Minimal text.** If the audience is reading the slide, they're not listening to you. Keywords and phrases over full sentences.
- **Speaker notes carry the nuance.** Everything the audience doesn't need to see but the speaker needs to say goes in notes.

### Reports and Memos

- **Executive summary first.** The busiest reader should get the full picture from the first page.
- **Progressive detail.** Each section adds depth. The reader can stop at any point and have a complete (if less detailed) understanding.
- **Recommendations are explicit.** Don't make the reader infer what you're suggesting. State it directly, early.

### Articles and Long-Form

- **The opening earns the reader's attention.** You have one paragraph to make the reader want the second paragraph. Don't waste it on throat-clearing ("In today's rapidly evolving landscape...").
- **Each section earns the next.** If a section doesn't make the reader curious about what comes next, the piece loses momentum.
- **The ending should resonate, not summarize.** A strong closing adds something — a new angle, a provocative question, a callback to the opening. Restating what was already said is deflating.

### Emails and Messages

- **Subject line is the headline.** It should tell the reader whether to open now or later.
- **First sentence is the point.** "Can you review this PR by Thursday?" not "Hi, I hope you're having a great week. I wanted to reach out regarding..."
- **If it's longer than a screen, it should probably be a document.**

---

## 8. Critique Framework

When evaluating any written artifact, work through these questions in order.

### First Impression (30-second scan)

- Can you identify the main point without reading the whole thing?
- Does the structure make the content navigable?
- Is the length appropriate for the content and audience?
- Does it look like someone cared about the writing?

### Clarity

- Can every sentence be understood on first reading?
- Are there sentences you need to read twice?
- Is the vocabulary appropriate for the audience?
- Are concrete details used where abstract language could hide vagueness?

### Structure

- Does it lead with the most important information?
- Does each section have a clear purpose?
- Can a reader skim headings and get the gist?
- Are transitions between sections smooth and logical?
- Are related ideas grouped together?

### Voice and Confidence

- Does the writing sound like a person?
- Is the tone appropriate for the audience and context?
- Are claims stated with appropriate confidence (not over-hedged, not overclaimed)?
- Is the register consistent throughout?

### Sentence-Level Craft

- Is there variety in sentence length and structure?
- Are there throat-clearing phrases that could be cut?
- Do sentences start with strong words, not empty ones?
- Is every word earning its place?

### Purpose Fit

- Does the writing do the job it's supposed to do (inform, persuade, instruct, narrate)?
- Would the intended reader find it useful, clear, and appropriately detailed?
- Is the medium (slides, report, email, article) being used to its strengths?

### Overall Assessment

- What are the three changes that would improve this most?
- What's working well that should be preserved?
- Rate overall quality on a 1-10 scale with a one-sentence justification
