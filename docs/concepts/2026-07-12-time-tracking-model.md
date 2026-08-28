# Time-Tracking Model — Next Evolution (Concept)

**Date:** 2026-07-12
**Status:** DRAFT — decision-ready, awaiting Esther's reactions. Nothing here is built.
**Consolidates:** command-module T020 (model concept), T014 (unified timesheet), T021 (silent-gap detection)
**Ground truth read for this doc:** `~/.claude/hooks/*` (live honest-clock implementation), `missioncontrol/docs/tracking-protocol.md` ("The honest clock & auto-wrap"), `missioncontrol/reports/timesheet.csv` (785 rows), live `tracking/.active-clocks/` snapshot (2026-07-12, 12 clock files), `/ci` `/co` `/wrap-up` skills, `/morning` `/evening` commands, dashboard `TimersView`.

---

## 1. Current state — what actually exists today

The question T020 asked in April ("bookend vs activity-sampling?") was posed against the old
`/ci`–`/co` world. That world is gone. Since 2026-07-07 the live system is already neither pure
bookend nor pure sampling — it is an **engaged-span hybrid**:

**The clock lifecycle** (per-session file in `tracking/.active-clocks/{session_id}.json`):

- **Armed** — `SessionStart` hook writes `opened_at`, `start: null`. Bills nothing, ever. A tab
  that never works never produces a row (this is what killed the ghost-row era).
- **Started** — first substantive tool (Edit/Write/Bash/NotebookEdit, immediate) **or** 2nd
  engaged turn (backdated to the 1st turn). Turns count since the 2026-07-09 fix, so
  design/discussion/reading sessions bill honestly, not just editing bursts.
- **Idle-gap sealing** — a gap > 30 min (`IDLE_GAP_SECONDS`) between engaged moments seals the
  current sub-span into `accrued_seconds` and opens a fresh one. Honest minutes =
  accrued sub-spans + open span. **Long silent gaps are already excluded mechanically.**
- **Wrapped** — `/wrap-up` (usually auto, via the Stop-hook nudge) writes one row per burst,
  resets the clock (`start: null`, `wrapped_at` set) so a later burst opens a fresh span.
- **Backstops** — SessionEnd hook and daily launchd sweep finalize unwrapped clocks with honest
  spans; **transcript reconciliation** reconstructs engaged minutes from message timestamps
  (clustered, split at >30-min gaps, sidechain/subagent messages excluded) and finalizers take
  `max(clock, transcript)` so under-tracking is recovered.

**The ledgers** (three, loosely coupled):

| Store | Role today |
|---|---|
| `reports/timesheet.csv` | 11 cols (`date,start,end,repo,cluster,session_type,minutes,title,details,source,session_id`). Declared "primary time database". |
| `tracking/{repo}/history.jsonl` `session` entries | Denormalized echo (`duration_hours`) + narrative; per-repo log. |
| `tracking/missioncontrol/history.jsonl` `day_start`/`day_end` | Wall-clock day bracket; `/evening` writes `hours_worked` (wall) + `project_hours` (summed from CSV). |

**What the data says** (785 CSV rows as of today):

- Ghost-era sources still dominate the file: `auto-session-end` (315) + `auto-close-20h` (203)
  ≈ 66% of all rows — pre-rewrite wall-clock/phantom rows. Post-rewrite quality sources are
  small but clean: `auto-wrap` 26, `clock` 27, `manual` 11, `*-unwrapped` 59.
- ~6 rows are structurally malformed (unquoted commas shifted their columns — `source` values
  like ` merged (PR #11)`). Any migration must repair these by hand.
- The 2026-07-05 swarm day: 22 rows, 22 distinct sessions, **47.1h logged** — a mix of real
  parallel work and ghost-era inflation (11× `auto-close-20h`), indistinguishable after the
  fact. Post-rewrite days (07-09 → 07-11) run 4–7.5h across 6–20 honest rows.
- Live snapshot right now (12 July, ~11:26): 12 clock files — 6 started (real parallel
  sessions), 6 armed-only (harmless but noisy), including one stray non-UUID file
  (`empty-state-draft.json`, repo=`.claude`) that nothing validates against.

**Known pains, restated against this reality:**

1. **Ghost clocks** — armed leftovers from unclosed tabs. They no longer bill time (armed = no
   row), so the surviving pain is *clutter and attribution confusion*: `/evening` Step 2
   interrogates every survivor, the dashboard LIVE list mixes real work with dead tabs, and
   strays like `empty-state-draft.json` are never rejected.
2. **Neglected parallel sessions** — a forgotten conversation among several. Idle-gap sealing
   already caps the damage at ≤30 min per neglect episode; the residue is *row quality*
   (`-unwrapped` rows with guessed type/title), not duration inflation.
3. **Undercounting thinking time** — the 2026-07-09 turn fix addressed in-conversation
   thinking. Still exposed: thinking that spans >30 min with no message (a walk, whiteboard,
   reading a long doc) gets sealed away as idle.

---

## 2. Principles (Esther, 2026-07-12 — these govern everything below)

1. **Bias toward capturing work, not trimming it.** The system historically tracked too
   little. When in doubt, count it; corrections should mostly move numbers *up*.
2. **Parallel work multiplies, it does not dedupe.** Five conversations in one hour can be 5h
   of work. Each session's time counts fully. Earlier "double-count problem" framing is
   superseded: the real ghost-clock problem was *attribution confusion*, never the
   multiplier. Reports lead with **summed work-hours**; wall-clock span is secondary at most.
3. **Thinking time is work** (standing, from T020): reading, framing, staring at a slide. Any
   design that systematically undercounts invisible work is disqualified.
4. **Mechanical over disciplined.** Fixes must not depend on Esther remembering to close tabs,
   run `/co`, or answer prompts. (The honest clock's whole history is the graveyard of
   discipline-based designs.)

---

## 3. The model choice (T020): three candidates

### A. Pure bookend (classic `/ci`–`/co`, wall-clock span)

Time = clock-in to clock-out, human-triggered. **Fails every failure mode:** forgotten `/co`
inflates (the 20:00-cap era), forgotten `/ci` loses whole sessions (violates principle 1),
parallel neglect bills idle tabs, and it is maximally discipline-dependent (violates
principle 4). This is the world the 2026-07-07 rewrite already left. **Rejected.**

### B. Pure activity-sampling (per-message micro-captures, summed)

Each message/tool event bills a small window; a session's row is the sum. Wins: silent gaps
cost nothing by construction; no stale-clock machinery. Loses, decisively:

- **Thinking time becomes structurally invisible** (violates principle 3, and principle 1 —
  it is a systematic *undercounter*, the exact direction Esther is correcting away from).
  Window-size tuning can't fix this: any window short enough to exclude lunch excludes a
  think-walk.
- Rewrites a foundation that shipped five days ago and is finally producing honest rows.
- Manual off-computer entries (`/ci HH:MM-HH:MM`) never merge cleanly with sampled rows.

**Rejected** — same conclusion as the April conversation, now with stronger grounds: the one
thing sampling buys (gap exclusion) the current system already does mechanically.

### C. Engaged-span hybrid — *the current model, named and tuned*

Bookend semantics (a row has a start, an end, a span) with the bookends *derived from
activity* (tools + turns) instead of human ritual, idle-gaps >30 min mechanically excluded,
and a transcript-derived ground truth as backstop. This is what's running. Gaps under 30 min
count as work (thinking-friendly); gaps over 30 min don't (lunch-proof); the threshold is the
single dial that trades the two off.

### Recommendation: **C — keep the engaged-span hybrid. The model is right; finish it.**

The remaining work is not a model change. It is four completions, which are sections 4–7:
the unified timesheet (T014), parallel-first reporting, gap handling re-reconciled with the
capture bias (T021 inverted), and mechanical ghost hygiene. T020 closes with this decision;
T021 closes superseded (see §6).

---

## 4. Unified timesheet v2 (T014)

### What "unified" means

Not one file — one **authority**. `timesheet.csv` v2 becomes the single time database;
`history.jsonl` `session` entries stay as a narrative echo (already true per protocol);
`day_start`/`day_end` stay as the wall-clock day bracket (needed for the leverage figure,
§5). The unification that matters is *inside the CSV*: today, minutes of wildly different
fidelity (honest spans, wall-clock ghosts, human estimates) share one `minutes` column,
distinguishable only by parsing 20 historical `source` strings.

### Proposed schema (v2, 13 columns)

```
date, window_start, window_end, repo, cluster, session_type,
clocked_minutes, estimated_minutes, title, details, method, source, session_id
```

- **`clocked_minutes`** — machine-derived honest engaged minutes (clock or transcript). Empty
  when no clock/transcript evidence exists.
- **`estimated_minutes`** — human/model retroactive estimate. Empty when the clock is trusted.
  Set by the retroactive-estimate flow (below) or by manual `/ci HH:MM-HH:MM` entries.
- **`method`** — how the minutes were derived: `engaged-span | transcript | manual-range |
  estimate`. (Today this hides inside free-text `details`: "honest span" / "reconciled from
  transcript". Promote it to a column.)
- **`source`** — which writer wrote the row: `auto-wrap | co | ci-manual | session-end |
  sweep | evening-reconcile`. Cleanly separated from *how* (method) — today `source`
  conflates both, which is why it has 20 historical values.
- **`window_start`/`window_end`** — kept, deliberately deviating from the 2026-04-17 sketch
  (which dropped start/end for the paired minute columns). Rationale: under the honest clock
  the window is *information* — `clocked_minutes < window span` is exactly the "idle was
  excluded" signal, `/evening` reconcile and the dashboard HISTORY view both use the bracket,
  and gap-reclaim (§6) needs it. The sketch predates the honest clock. **Flagged as an open
  question (§8-Q2) since it reverses her stated design.**

**Reporting rule:** `billed = estimated_minutes if set, else clocked_minutes`. A human
override beats the machine — the estimate flow only writes when the clock is known wrong or
absent, and a deliberate human trim stays possible without fighting the system. When *both*
are set and diverge >25%, `/evening` surfaces the divergence rather than silently picking.
(Alternative — `max()` per the capture bias — is §8-Q3.)

**Row granularity:** one row per **wrapped burst**, not per session (a session that wraps
three times gets three rows, as today — e.g. session `b836e356` on 07-10). Reports group by
`session_id`. T014 said "one row per session"; per-burst is what wrap-and-reset naturally
produces, keeps rows append-only (no rewriting a session's row on the next wrap), and
grouping recovers the per-session view for free.

### Retroactive-estimate flow

Lives in **`/evening` reconcile** (primary) and **`/wrap-up`** (opportunistic):

- `/evening` already reconciles `-unwrapped` rows (fixing guessed type/title). Extend it:
  for each of today's rows where clock evidence looks thin (armed-only sessions that got
  drained, `method=transcript` reconstructions, sealed gaps — §6), ask once, batched:
  *"These N rows look under-clocked; estimates?"* Answers write `estimated_minutes` —
  **never overwrite `clocked_minutes`**, so machine truth and human judgment stay separately
  auditable (this is the whole point of the two-column split).
- Off-computer work stays as today's manual `/ci` path, landing as
  `estimated_minutes` + `method=manual-range`.

### Migration from v1

1. **Freeze v1:** copy `reports/timesheet.csv` → `reports/timesheet-v1.csv` (archived, never
   written again).
2. **Mechanical column mapping** (a script, e.g. `scripts/migrate-timesheet-v2.py` in
   missioncontrol): machine sources (`clock`, `auto-wrap`, `wrap-up`, `auto-*`) →
   `clocked_minutes`; human sources (`retroactive`, `manual`, `backfill`, `manual-correction`)
   → `estimated_minutes`; old `source` maps to new `source`+`method` via a lookup table;
   repair the ~6 malformed rows by hand. **No re-interpretation of ghost-era durations** —
   they stay what they are, tagged `method=wall-clock-legacy` so reports can discount them.
3. **Cut the writers over in one change:** `~/.claude/hooks/_clock_shared.py` (`CSV_HEADER`,
   `write_csv_row`) + its two finalizer callers, the `/ci` `/co` `/wrap-up` skills (source +
   staging copies in `plugins/command-module/staging/hooks/`), and `/evening`/`/morning` in
   `missioncontrol/.claude/commands/`.
4. **Readers next, same day:** dashboard server CSV parser + `types.ts` `TimesheetRow` +
   `TimersView`; `/evening` Step 4; `/weekly-review` (indirect, via `day_end`).

Because writers are few and all under our control, a single-day atomic cutover is cheaper
than a dual-format transition period.

---

## 5. Parallel-work reporting

### The headline metric flips

**Work-hours (summed engaged minutes across all sessions) is the number.** Wall-clock span is
context. Derived: **leverage = work-hours ÷ wall-clock span** — the multiplier made visible
and celebrated, replacing the old instinct to "fix" totals that exceed the day.

- **`/evening`:** lead with *"Work done: 9.4h across 6 sessions"*, then *"Day span:
  08:17–18:40 (10.4h wall)"*, then *"Leverage: 0.9×"* (or 1.6× on a swarm day). The existing
  apologetic footnote *"(includes parallel work)"* is deleted — that's the headline now. The
  `day_end` entry gains `work_hours` (summed) alongside the existing `hours_worked` (wall);
  `project_hours` is already CSV-summed and therefore already the multiplied figure — correct
  as-is.
- **`/weekly-review`:** the per-day table becomes Work-h (primary) | Wall-h | Leverage;
  weekly total = Σ work-hours. Per-project hours stay summed (already correct). A weekly
  leverage trend is one extra line and genuinely informative (swarm days vs solo days).
- **Dashboard Timers tab:** add a *Today* strip above LIVE: summed engaged minutes today
  (finished rows + running clocks' open spans), wall span since `day_start`, leverage badge.
  LIVE table splits **started** clocks (ticking, prominent) from **armed** clocks (dimmed,
  "opened, no work yet") — today they're visually identical, which *is* the attribution
  confusion.

### Attribution rule for agents and subagents

> **A session's clock owns everything that happens inside that session — including its
> subagent fleet. Subagents never get their own clocks or rows, and fleet size never
> multiplies time. The parallel multiplier applies across top-level sessions only.**

Rationale: sessions are the units of *Esther's leveraged attention* — the things she juggles.
Subagents are a session's implementation detail, like threads of a process. One hour
orchestrating a 5-agent swarm in one conversation = 1 hour on that session (already a
5× output multiplier in *content*, which the row's `details` records); five parallel
*conversations* for an hour = 5 work-hours. This matches the mechanics almost for free:
subagent tool calls fire the PostToolUse heartbeat in the parent session, so a working fleet
keeps the parent clock alive even while Esther reads or thinks.

One known asymmetry to fix when convenient: transcript reconciliation skips `isSidechain`
messages, so the *backstop* under-reconstructs a session whose fleet ran while Esther was
silent (the live clock captures it; the transcript fallback wouldn't). Include sidechain
timestamps in `reconcile_from_transcript` for sessions that started — one condition —
so both paths agree with the attribution rule. Whether *unattended* long fleet runs (she
leaves entirely; agents run 2h) should bill is §8-Q4.

---

## 6. Silent gaps (T021) — reconciled with the capture bias

T021 was specced when gaps inflated time. Under the honest clock the polarity has flipped:

- **Gaps > 30 min are already excluded, mechanically, live** (idle-gap sealing +
  transcript clustering). The inflation problem T021 targeted no longer exists.
- **Gaps < 30 min count as work, silently.** Correct per principles 1 and 3 — that's
  thinking, reading, reviewing agent output. No prompt, no threshold-fiddling.
- The remaining risk is the **opposite** one: a genuine 45-min think-walk or deep read gets
  sealed away as idle. The current system's only error direction is now *under*-counting.

**Proposal — replace trim-prompts with a reclaim flow:**

1. Keep auto-sealing at wrap time exactly as is (no confirmation friction — principle 4).
2. Record sealed gaps on the row (cheap: `details` already notes the method; add
   `gaps: 14:20–15:07` when a burst sealed one) or derivable from `window span −
   clocked_minutes`.
3. In **`/evening` reconcile**, surface the day's sealed gaps *adjacent to engaged spans*
   once, batched: *"Sealed as idle today: 47 min (14:20–15:07, missioncontrol) and 38 min
   (16:10–16:48, revintel). Reclaim any as work?"* A reclaim writes `estimated_minutes =
   clocked + reclaimed` on that row — clock truth untouched, capture bias honored, one
   keystroke.
4. Manual `/ci HH:MM-HH:MM` entries have no activity signal — never gap-scanned (human-entered
   is trusted as-is, unchanged from today).

**T021 closes as superseded.** Its confirm-or-trim UI at `/co` would today mostly invite
trimming — the wrong direction — and `/co` itself is nearly extinct (auto-wrap is the normal
path; 26 `auto-wrap` vs 27 lifetime `clock` rows and climbing).

The one genuinely open dial is the threshold itself: §8-Q1.

---

## 7. Ghost-clock prevention — mechanical only

Armed clocks already bill nothing, and the daily 20:00 sweep drains them. What remains is
same-day clutter and attribution confusion. Four fixes, none requiring discipline:

1. **Liveness probe instead of interrogation.** A clock's `transcript_path` mtime is ground
   truth for "is this conversation actually alive?". `/evening` Step 2 and the sweep use it:
   transcript untouched for >2h → armed clocks drain silently, started clocks finalize
   without asking. `/evening` stops interrogating Esther about every survivor (today's
   Step 2 asks per clock — discipline in disguise) and reports one line: *"Drained 4 dead
   tabs, finalized 1 abandoned session (23 min)."* Only genuinely-alive clocks ever prompt.
2. **Arm-time TTL.** At every `SessionStart`, opportunistically drain sibling *armed-only*
   clocks whose `opened_at` is a previous day (or >12h old). Ghosts then die at the next
   morning's first tab, not at 20:00 — the LIVE view stays honest all day.
3. **Validate at arm time.** `session-start-clock.py` refuses to arm when `session_id` isn't
   a UUID (kills strays like today's `empty-state-draft.json`) and logs to stderr instead.
4. **Make armed vs started visually distinct** in the dashboard LIVE section (dimmed "no work
   yet" rows). Attribution confusion was always a *seeing* problem; this is where it's seen.

Explicitly not proposed: auto-deleting started clocks aggressively, heartbeat PID-tracking,
or any "are you still there?" prompting — the armed/started split plus transcript mtime
already carries all the signal needed.

---

## 8. Open questions for Esther (genuine forks only)

1. **Idle threshold (the one dial):** keep `IDLE_GAP` at 30 min with `/evening` reclaim as
   the safety valve, or raise to 45–60 min so think-walks count by default (accepting that a
   45-min true absence next to an engaged span bills as work until reclaim-review)? The
   capture bias argues for raising it; 30 min + reclaim is the conservative version of the
   same instinct.
2. **Window columns:** timesheet v2 keeps `window_start`/`window_end` (my recommendation,
   §4) — but your 2026-04-17 sketch explicitly dropped start/end for the paired minute
   columns. Keep the bracket, or honor the sketch and go minutes-only?
3. **When both columns are set:** does `estimated_minutes` override `clocked_minutes`
   (human beats machine — my recommendation), or does `max()` win (pure capture bias, never
   report less than the clock saw)?
4. **Unattended fleet runs:** a swarm that keeps working for 2h after you leave keeps the
   parent clock alive and bills 2h. Count it (it's real produced work — my lean, consistent
   with principle 2), or should work-hours mean *attended* time, with unattended agent
   runtime reported as its own line?
5. **Migration depth:** mechanical column-mapping of all 785 v1 rows with ghost-era rows
   tagged `wall-clock-legacy` (my recommendation), or hard cut-over at 2026-07-07 with
   everything earlier left in the v1 archive and excluded from v2 reports entirely?

---

## 9. What closes, what opens

- **T020** → closes with the §3 decision (keep engaged-span hybrid; no model change).
- **T021** → closes as superseded (§6); reclaim flow becomes part of the /evening reconcile work.
- **T014** → becomes the implementation track: timesheet v2 schema + migration (§4),
  parallel-first reporting in /evening, /weekly-review, dashboard (§5), reclaim flow (§6),
  ghost hygiene (§7). Suggest decomposing after Esther reacts to §8 — Q1–Q3 change the
  schema; Q4–Q5 only change scripts.
