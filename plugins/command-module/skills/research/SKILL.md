---
name: research
description: "Dispatch a deep-research run with the user's durable research preferences baked in -- comprehensive by default, no length or time caps, never pre-impose structures (assumed taxonomies become open questions), find-all over top-N, and build-up-over-time as the default temporal frame. Accepts a free-form topic or a task ID. Use when the user says '/research', 'research X', 'do deep research on this', 'look into X thoroughly', 'research T042', or wants a comprehensive cited report without re-stating how they like research done."
argument-hint: "[topic to research, or a task ID like T042]"
---

# /research -- Deep Research with Durable Preferences

Dispatch a deep-research run without re-stating (or accidentally violating) how the user likes research done. The user's research preferences are **universal across every project and durable over time** -- this skill is the canonical place they live in execution, so each run inherits them automatically instead of being hand-specified and quietly drifting thin.

The value is entirely in what gets baked in before dispatch. A research run with a `~600-word` cap, a pre-imposed three-tier table, or a "top 3" framing bakes AI-typical thinness into work that should be thorough. This skill strips all of that out of the framing before the run starts.

## The durable preferences (baked in -- do not re-derive per run)

These are canonical. They originate from the user's standing preference on all research/exploration work (recorded in the `feedback_research_comprehensiveness` memory); this skill is their execution home. If the two ever diverge, this skill wins for what actually runs -- and the user should be reminded to update both if the preference itself changes.

- **Comprehensive, detailed, nuanced.** Find as many sources, angles, and ideas as the topic actually contains. Comprehensiveness is a feature, not a scope risk.
- **No length caps. No time caps.** `~600 words`, `~1h`, `top 2-3` are all wrong defaults. The run happens in the background regardless, so there is nothing to save by capping it. Never ask the research to self-limit ("if this gets too long, stop") -- that undersells the run; trust it.
- **Never pre-impose structures.** Any assumed taxonomy, tier, category set, or count in the framing is a hidden assumption. Convert it into an open research question instead. "Produce a table of three difficulty tiers" becomes "Are there common difficulty tiers? If so, how many, and do they vary by approach?" Same for every assumed structure.
- **Find-all, not top-N.** Ranking the set by relevance or importance is fine; capping it at a number is not. The set is whatever the topic contains.
- **Anti-fits, open questions, contested points are encouraged, never required and never numerically capped.** Ask for them as "surface any that exist," not "give me three."
- **Cite all claims; note source credibility.** Distinguish primary sources, strong secondary sources, and weak or contested ones.
- **Build-up-over-time is a valid default frame.** For any topic that has a temporal dimension, include how the thing evolved -- across sessions, weeks, months, or years -- not only its current-state snapshot. Surface the trajectory, not just the endpoint.

## Phase 0 -- Ground

1. **Resolve the repo** for output: `git rev-parse --show-toplevel` (fall back to the current directory, and note the fallback). Reports land in this repo's `docs/research/`.
2. **Parse `$ARGUMENTS`.**
   - A `T\d+` token is a **task ID** -- read `missioncontrol/tracking/{repo}/tasks/T0NN.md` for the actual research questions, its `origin`, and any framing the task already carries. (Tracking lives under `missioncontrol/tracking/{repo}/`; if that relative path is not resolvable, use the absolute missioncontrol tracking root.)
   - Anything else is a **free-form topic** -- research it directly.
   - If `$ARGUMENTS` is empty, ask the user what to research using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini; chat fallback otherwise).

## Phase 1 -- Build the research brief

1. **Extract the real questions.** From the topic or the task, state what the run is actually trying to learn -- as open questions, not as a template to fill.
2. **Audit the framing and neutralise pre-imposed structures.** Read the user's phrasing (and the task notes) for smuggled-in assumptions: word or time caps, "top N", assumed taxonomies, assumed counts, a pre-decided table shape. For each one found, rewrite it as an open question and briefly tell the user what you converted ("you asked for the three main approaches -- I've turned that into 'what approaches exist, and do they group naturally?' so the run isn't capped at three"). This audit is the core of the skill; do not skip it even when the framing looks clean.
3. **Add the build-up-over-time dimension** when the topic is temporal, as an explicit question in the brief.
4. **Do NOT pre-scope depth or length.** That contradicts the preferences. Assemble the brief as a self-contained set of open questions plus the standing preferences above, and dispatch. No pre-flight length/depth negotiation.

The brief is sent verbatim to whatever engine runs it, so it must stand alone -- the engine sees only this text, not the conversation.

## Phase 2 -- Dispatch

These runs are long, so start them in the background where the platform supports it and reclaim the latency for other work.

Pick the mechanism by what is available:

1. **Native deep-research harness (preferred).** If a `deep-research` skill/capability is available (Claude Code's harness fans out web searches, fetches primary sources, adversarially verifies claims, and synthesises a cited report), invoke it with the brief. This best satisfies the "cite all claims, note credibility" preference.
2. **Research agent (fallback).** Otherwise dispatch a research agent via the platform's agent/task tool -- `command-module:research:best-practices-researcher` for practices/standards questions, `command-module:research:framework-docs-researcher` for library/framework questions, or a general-purpose research agent for open topics. Pass the full brief including the preferences block, and run it in the background for long runs.
3. **Multi-model panel (offer when triangulation matters).** When the user wants the same question cross-checked across engines, mention that the `deep-research-panel` skill runs the brief through Claude, Gemini, and ChatGPT side by side -- do not invoke it by default, only when the user asks for multiple models.

Whichever mechanism runs, the baked-in preferences travel with the brief -- they are not the engine's to re-decide.

## Phase 3 -- Save the report

1. Write the cited report to `docs/research/` in the calling repo. Use a dated, kebab-case name: `<YYYY-MM-DD>-<slug>.md` (or a `<YYYY-MM-DD>-<slug>/` folder with the report plus the brief when the run produced multiple artifacts). Create the directory if missing.
2. If the run was dispatched to a task ID, note the report path back on the task (or offer to `/capture` a follow-up) so the tracking stays connected to the output.
3. Report the resolved path(s) back to the user. If a run failed or an engine was unavailable, say so plainly rather than presenting a thin report as complete.

## Guardrails

- **Never cap the run.** No word count, no time box, no "top N", no "stop if too long." If the user's phrasing contains a cap, surface it and convert it -- do not silently honour it.
- **Never pre-impose a structure.** Every assumed taxonomy or count in the framing becomes an open question. Flag what you converted so the user can confirm.
- **Comprehensive over thin, always.** When in doubt, widen the net. Thinness is the failure mode this skill exists to prevent.
- **Cite everything and grade the sources.** An uncited claim or an ungraded weak source is a defect, not a stylistic choice.
- **This skill is the canonical home of the preferences.** Do not re-derive them per run or let a dispatched engine override them. If the user changes the preference itself, update this skill (and remind them the memory should match).
