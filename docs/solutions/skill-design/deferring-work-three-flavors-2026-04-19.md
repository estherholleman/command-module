---
title: "Three flavors of deferred work and where each belongs"
problem_type: best_practice
component: skills
root_cause: missing_pattern_for_cross_session_continuity
resolution_type: workflow_improvement
severity: medium
tags: [deferred-work, skill-design, implementation-plan, work, document-review, cross-repo, task-tracking]
date: 2026-04-19
---

## Problem

Plans, reviews, and work sessions frequently defer work: "we'll do X
later," "this is out of scope but should be tracked," "this depends on
Y landing first." When those deferred items aren't recorded in a
specific, retrievable place with a clear trigger, they rot — lost
between sessions, invisible to future agents, or rediscovered
weeks later when a symptom surfaces.

There's no single right place for every deferred item. A TODO comment
is wrong for cross-repo work. A task is wrong for grep-findable
code-level markers. A doc entry is wrong for work that only the
originating repo will ever see. Without a framework for deciding,
each session makes ad-hoc calls and the deferred-work layer becomes
inconsistent.

## Symptoms

- TODO comments in code that rot (no trigger condition, no owner,
  no timeline)
- "We should do X later" notes in a plan doc with no task captured,
  so future planners don't see them
- Cross-repo dependencies that only make sense with the conversation
  context that produced them — a fresh agent can't pick them up
- New releases or plans that miss follow-up work from a previous
  change because the deferral wasn't surfaced anywhere discoverable
- Duplicate deferrals — the same item flagged three times across
  three plans because each planner rediscovered it
- "Where did I say that should be done later?" moments

## What Didn't Work

**Single-layer approaches:**

- **Only TODO comments in code:** fine for same-file reminders, but
  invisible across repos and easy to overlook in review
- **Only tasks:** the task system alone loses the grep-findable
  signal that enables discovery-via-search later (e.g., when
  planning a version bump, you want to grep the code for
  `"deprecated in v0.6"` markers, not remember to check the task
  tracker)
- **Only doc entries** (e.g., a `docs/deferred-cleanup.md` file):
  fine for same-repo cleanup, but a fresh agent working in a
  *different* repo will never see it

**Implicit coordination:** assuming the person who wrote the plan
will remember to do the follow-up. Works for hours. Fails for
weeks, and always fails across context boundaries (new conversation,
new agent, new team member).

## Solution

Classify each deferred item into one of three flavors. Each flavor
has a primary home. Use all three layers — they cover non-overlapping
gaps.

### Flavor 1 — Same-repo, code-triggered cleanup

**Example:** a `DeprecationWarning` in v0.6 that should become a
`ValueError` in v0.7.

**Primary home: the code itself + a `docs/deferred-cleanup.md` entry.**

- The code-level signal carries a grep-findable token (e.g., the
  deprecation message contains the literal string
  `"Will be removed in v0.7.0"`). When a future agent plans v0.7,
  they grep the codebase for `"v0.7.0"` and find every deferred
  cleanup automatically.
- `docs/deferred-cleanup.md` mirrors each code-level reminder in
  prose, for readers who don't think to grep.
- A task in the tracker is optional — the grep + doc usually carry
  enough signal.

**Why both:** the grep token survives file moves and doesn't depend
on anyone reading docs. The doc entry survives the case where the
reader doesn't know what to grep for.

### Flavor 2 — Same-repo, condition-triggered work

**Example:** "Regenerate golden test fixtures after we switch data
sources."

**Primary home: a task (with the trigger condition in its
description) + a `docs/deferred-cleanup.md` pointer.**

- The task is the discovery mechanism — it shows up in task-list
  views, morning briefings, status dashboards. The trigger
  condition makes it clear when to execute.
- The doc entry points at the task for discoverability from the
  repo side (someone reading the repo docs sees the deferral
  without needing to query the task tracker).

**Why not just a task:** a task alone is invisible to someone
reading the repo without knowing to check the tracker. A doc
pointer closes that gap.

### Flavor 3 — Cross-repo follow-up work

**Example:** "After revintel v0.6.0 ships, update the Python repo
that consumes it."

**Primary home: a task whose body IS a self-contained execution
prompt.**

This is the most important case and the one most often done poorly.
Cross-repo work means a future agent will be working in a *different*
repo, without the context of the conversation that produced the
deferral. A task that just *describes* the work ("update the Python
repo") requires the executor to rediscover what to edit, why, and
how to verify.

A task whose body contains:

1. **Why this task exists** (one paragraph linking to the
   originating plan / solution / memory)
2. **Trigger conditions** (specific checkable conditions — all must
   be true before executing)
3. **What to edit** (grep commands to find sites, known sites as of
   the task's creation date, provenance checks, exact before/after
   edits)
4. **Verification** (how to confirm the change worked)
5. **After this task completes** (what downstream tasks unblock,
   what to update in trackers)
6. **If something unexpected** (branches for common edge cases)
7. **Scope boundaries** (what's explicitly in and out)

...is executable by a fresh agent from the task file alone, without
the originating conversation.

**Why not a doc in the consuming repo:** the originating repo
doesn't own the consuming repo's docs; the consuming repo's docs
don't know the originating change exists. A task in a cross-project
tracker (or an issues system visible from both sides) is the only
place that naturally spans the gap.

## Decision table

| Question | If yes → |
|---|---|
| Is this a code-level reminder triggered by future code changes (e.g., version bump)? | **Flavor 1** |
| Is this same-repo work waiting on a condition the repo's own code doesn't signal? | **Flavor 2** |
| Does this require editing a different repo than where it was discovered? | **Flavor 3** |

Items may fit more than one flavor — pick the one whose primary
home most robustly surfaces the work at the right time. When in
doubt for cross-repo work, prefer Flavor 3's executable-prompt
format: the extra effort to write a good prompt is small and pays
off every time a fresh agent picks up the task.

## Why This Works

Each layer covers a failure mode the others can't:

- Code-level tokens survive refactors and don't depend on docs
  being current
- Doc entries survive code being renamed or removed (the rationale
  is preserved even when the trigger site moves)
- Task-body-as-prompt survives the conversation context evaporating
  and survives agents working in repos that don't know about the
  originating repo

Together they make deferred work discoverable via multiple paths:
grep, doc scan, task list.

## Prevention

When any skill (plan, review, work session) defers an item:

1. **Ask which flavor it is** before writing the deferral. Use the
   decision table above.
2. **Write the deferral in its primary home.** For Flavor 3, don't
   cheat — write the full self-contained prompt. Future-you will
   thank you.
3. **Add a pointer from the originating repo's
   `docs/deferred-cleanup.md`** so the repo itself carries the
   breadcrumb.

**For complex changes affecting external consumers**: consider a
**dependent scan** before finalizing the plan — enumerate every
external file / repo that uses the API surface being changed, so
the deferred-work plan is complete rather than surfacing gaps
mid-implementation. This is currently manual (grep across known
consumer repos). A dedicated `dependent-scanner` agent invoked by
`implementation-plan` is a natural future extension, especially for
projects where external consumers are known in advance (e.g., a
library with fixed production callers). Not every project needs
this — small projects or single-repo codebases where `implementation-plan`
already sees all consumers can skip it.

**Naming the deferred-cleanup file:** we've been using
`docs/deferred-cleanup.md` at the repo root's docs directory. Any
stable, conventional name works — the point is that agents and
humans both know where to look. Pick one per repo and stick with it.

## Status

v1 — pattern extracted from one project (revintel's T029 /
configurable route_column change, 2026-04-19). Iterate as the
pattern is used on additional projects; the Flavor 3 executable-prompt
template in particular is the most distinctive piece and deserves
real-world validation before canonizing harder.

## Related

- `docs/solutions/skill-design/pass-paths-not-content-to-subagents-2026-03-26.md` — related pattern about how orchestrators hand work to sub-agents; the Flavor 3 executable-prompt format shares the "make the task self-contained" principle
- `docs/solutions/skill-design/script-first-skill-architecture.md` — complementary philosophy about pre-computing work so later phases don't have to
- `plugins/command-module/agents/research/learnings-researcher.md` — the agent that discovers past solutions by searching `docs/solutions/`; it's how this doc itself gets surfaced to future planners
- `plugins/command-module/skills/distill/SKILL.md` — the skill that captures solved-problem documentation (like this doc) after the fact; complementary to the *deferred* work pattern (this doc) which captures UNsolved work
