---
name: here-or-there
description: 'Assess the current conversation at a workflow transition and decide whether to continue inline (here) or hand off to a fresh conversation (there). On "there", auto-invoke the handoff skill with an inferred topic and next-action -- no second confirmation. Triggers: "/here-or-there", "here or there", "should I keep going here", "should I hand off", "continue here or new conversation", "fresh conversation or stay here", "is this conversation getting too long".'
---

# /here-or-there -- Transition Decision Point

Answer one binary question for the user: **should this work continue in the current conversation, or transition to a fresh one?** Read the live transcript, name the rationale in 1-3 lines, and either return control to chat (`here`) or auto-invoke the `handoff` skill with an inferred topic and next-action (`there`). The user is not asked a second time -- this skill carries the assessment burden so they do not have to.

**When NOT to use this skill:** if the user has already decided to hand off, load the `handoff` skill directly with positional arguments to skip the assessment. This skill is for the case where the user is genuinely undecided.

**What this skill does not solve:** context bloat that has already accumulated in the source conversation. The assessment runs against whatever transcript is visible -- if the conversation is already badly degraded, the inferred topic and next-action inherit that degradation. The fix is to invoke this skill earlier, not to expect it to recover from late-stage context drift.

## Phase 0 -- Ground

Read the transcript. Assess whether there is enough context to introspect meaningfully against the **minimum-context threshold**:

1. At least 2 prior user turns in the conversation.
2. At least one named subject the topic could anchor to (a feature name, a file path, a decision, or a workflow phase explicitly mentioned).
3. Some signal that a transition is plausible -- the current user message references "next", "now", "should I", or asks the assessment question itself.

If **any** of these fail, the transcript is too thin to assess. Skip Phase 1, jump straight to Phase 2a, and emit the rationale: *"not enough context to assess -- staying here."* Do not guess.

If all three hold, proceed to Phase 1.

## Phase 1 -- Assess

Walk the five signals below. For each, name what was observed in the transcript -- a verbatim phrase, a turn count, a file path, the workflow phase that just closed. Reason about strength descriptively, not arithmetically: a signal is "materially strong" when it would be visible to a human reader of the transcript, not when it crosses a numeric threshold.

### Signal 1 -- Context accumulation

Many turns. Multiple long tool-result chunks. Multi-step work that has visibly bulked the conversation buffer. The longer and more tool-output-heavy the conversation, the stronger this signal.

### Signal 2 -- Topic shift

The user's current request is materially disjoint from what the conversation opened on. Conversation opened on "refactor parser X", current message is "let's plan feature Y". Different files, different goals, different mental models.

### Signal 3 -- Workflow-phase completion

A discrete unit just closed. A plan was written. A brainstorm wrapped. A review completed. A feature shipped. The next phase is named -- or implied by what just finished. This is a strong structural signal: the work has reached a natural seam.

### Signal 4 -- Explicit transition language

The user used direct words: *"ok now I want to..."*, *"next step is..."*, *"let's move on to..."*, *"fresh conversation"*, *"new chat"*, *"switch to..."*. This is the strongest single signal -- explicit user intent outranks the others.

### Signal 5 -- Carry-forward cost

Most of what is loaded into the current conversation (file reads, plan content, tool outputs) is downstream context the next phase does not need. A fresh conversation pays a small re-grounding cost to shed substantial noise. Inverse: if most of the loaded context *is* load-bearing for the next phase, the carry-forward cost is low and this signal is weak.

### Decision rule

Recommend `there` when at least two signals fire with material strength. Signal 4 (explicit transition language) is uniquely strong: when it fires verbatim it counts as the materially-strong half of the pair, so any other firing signal -- even at moderate strength -- tips toward `there`. For Signals 1, 2, 3, and 5, both signals in the pair must fire with material strength.

On weak or contradictory signals, default to `here`. The user can always invoke `/handoff` directly if they disagree -- forcing fresh starts the user did not ask for is the worse error.

## Phase 2 -- Route

### Phase 2a -- Stay (here)

Output a 1-3 line rationale naming the strongest signal(s) for staying. Examples (illustrative, not templates -- adapt to the actual transcript):

- *"Conversation is short and on-topic; current context is still load-bearing for the work in progress. Staying here."*
- *"Topic shift noted, but signals 1 and 5 don't fire -- the carry-forward cost is small. Staying here."*

Return control to chat. Do not invoke `handoff`. Done.

### Phase 2b -- Route (there)

Output a 1-3 line rationale naming the firing signals. Then **infer `<topic>` and `<next-action>`** from the transcript using the same grammar the `handoff` skill documents:

- **Topic** = the subject matter the new conversation will work on (e.g. `here-or-there-skill`, `auth-rewrite`, kebab-case).
- **Next-action** = the verb or skill the new conversation will run (e.g. `plan`, `build`, `review`, `concept`).

State the inferred values in chat in one short line: *"Invoking /handoff with topic=`<X>` next-action=`<Y>`."* Then proceed to Phase 3.

**Inference-failure fallback.** Before passing args to `handoff`, verify the inferred values pass two shape checks:

1. `<topic>` is a single kebab-case token: no whitespace, no quotes, no `/` prefix.
2. `<next-action>` is a single non-stopword token (a verb or a known skill name like `plan`, `build`, `review`, `concept`).

If either check fails, or if either value cannot be inferred from the transcript with even minimal confidence (the transcript names no clear subject, or the next phase is genuinely unclear), do **not** route. Fall back to Phase 2a with rationale: *"leaning fresh start, but cannot infer the next phase confidently -- invoke /handoff directly with your own topic and next-action if you want to proceed."* Passing garbage args to `handoff` is worse than declining to route -- once `handoff` sees `$ARGUMENTS` of any shape, it skips its own Phase 1.5 confirmation, so the shape check here is the last guard before the file is written.

## Phase 3 -- Auto-invoke

Load the `handoff` skill with positional arguments `<topic> <next-action>` (whitespace-separated; first token is topic, the remainder is next-action). The `handoff` skill detects the arguments and skips its Phase 1.5 confirmation -- the file is written and the prompt is displayed without a second prompt to the user.

The user sees one continuous output: rationale -> "Invoking /handoff..." line -> the `handoff` skill's standard closing (resolved file path + the full prompt content rendered in chat).

Done. No follow-up question, no further branching.

## State machine summary

The skill has three terminal paths. They are explicit so edge cases do not invent a fourth path:

```
        +------------------+
        | /here-or-there   |
        +--------+---------+
                 |
                 v
        Phase 0: Ground
        |              |
   too-thin?         enough context?
        |              |
        v              v
   +----------+   Phase 1: Assess
   | Phase 2a |   five signals, decision rule
   | "not     |        |
   | enough   |   +----+----+
   | context, |   |         |
   | staying  | "here"   "there"
   | here"    |   |         |
   +----------+   v         v
   DONE       Phase 2a   Phase 2b
              "stay"     infer topic + next-action
              DONE          |
                            v
                       Phase 3
                       load `handoff` with args
                       DONE

   Inference fails in Phase 2b? -> fall back to Phase 2a.
```

Three terminal states, no fourth. If a scenario seems to need a different exit (e.g., "wrap up first, then hand off"), recommend `here` and let the user invoke `/wrap-up` and `/handoff` themselves -- multi-destination routing is intentionally out of scope.

## Relationship to /handoff

`/here-or-there` is the upstream "should I?" gate that `/handoff` already names in its `When NOT to use this skill` carve-out. The two skills are kept separate by design:

- **`/handoff` alone** is for users who have already decided -- it skips the assessment and writes the prompt straight away.
- **`/here-or-there`** is for users who are undecided -- it runs the assessment and routes.

The integration point is `/handoff`'s `$ARGUMENTS` gate: when arguments are present, `/handoff` skips its Phase 1.5 confirmation. This skill's auto-invoke step relies on that contract -- no edits to `/handoff` are required.
