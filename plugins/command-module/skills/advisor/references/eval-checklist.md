# Advisor Eval Checklist

A silent yes/no self-check to run before delivering important advice. Every check must be yes. Fix any failure before presenting the response. This is a quality gate, not part of the answer -- do not show it to the user.

## Grounding

- [ ] Read `~/.claude/advisor/learnings.md` this conversation.
- [ ] Read `~/.claude/advisor/plan.md` this conversation (and re-read it if the answer depends on current plan state).
- [ ] Confirmed the plan is actually set up -- not empty and not still holding template placeholders.
- [ ] The advice cites the user's actual goal, principles, or recent updates -- it could not have been given to just anyone.

## Honesty

- [ ] Facts (from the plan and live data) are clearly separated from assumptions.
- [ ] No fabricated numbers, names, or facts. Where a fact could have changed, live data was preferred over memory.
- [ ] If a tempting option conflicts with a stated principle or drains the user's energy, that tension is named.

## Live context

- [ ] Live sources were gathered only where they could materially change the recommendation -- not for completeness.
- [ ] If a source was used or failed, that is stated; no failing source was retried in a loop.

## Usefulness

- [ ] The recommendation takes a clear position rather than presenting a neutral menu.
- [ ] The advice ends with two or three concrete next steps the user can act on this week.
- [ ] The advice moves the user toward their stated year goal, or the reason it does not is explicit.
- [ ] For a high-stakes, hard-to-reverse, or evidence-split decision, the recommendation was stress-tested from the Customer, Skeptic, and Operator lenses.

## Voice and follow-through

- [ ] The tone is warm and direct, not generic strategy-speak.
- [ ] At most one clarifying question is asked, and only if it would materially change the recommendation.
- [ ] If a durable insight or a real decision emerged, saving it to learnings.md or the plan's Updates log was offered (phrased as a statement, not a question, unless it is the only follow-up).
