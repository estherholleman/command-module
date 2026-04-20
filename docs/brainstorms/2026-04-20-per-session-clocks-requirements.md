# Per-Session Clocks — Requirements Brainstorm

**Date:** 2026-04-20
**Related task:** missioncontrol T015 (command-module)
**Status:** Brainstorm complete, ready for `/implementation-plan`
**Brainstormed by:** Esther + Claude (in missioncontrol conversation)

---

## Problem

Mission-control's time-tracking uses a single global clock file (`missioncontrol/tracking/.active-clock.json`). Only one clock can run at a time. Esther's actual workflow has multiple Claude Code conversations open in parallel, often across multiple repos, and regularly multiple conversations **within the same repo** simultaneously.

Current symptoms:
- Second conversation asks "clock already running — close it?" on every `/ci` attempt.
- If she dismisses the prompt, the second session's time is never tracked.
- She never manually toggles because it's tedious — so parallel sessions are systematically undercounted.
- `/wrap-up` at end of a session doesn't know which clock to close (it closes *the* clock, which may belong to another still-running conversation).

## Goal

Each Claude Code conversation gets its own clock, auto-started at conversation begin and auto-finalized at conversation end (or at `/wrap-up`/`/co`). Zero manual toggling. Reliable per-session rows in `timesheet.csv`.

---

## Current state

Files involved:
- **Hook**: `~/.claude/hooks/auto-clock-in.py` — runs on `UserPromptSubmit`, writes `.active-clock.json` if none exists, rate-limited by `/tmp/claude-clock-reminded` (30 min dedupe).
- **Skill**: `command-module/plugins/command-module/skills/ci/SKILL.md` — manual clock-in, also handles manual time entries (off-computer work).
- **Skill**: `command-module/plugins/command-module/skills/co/SKILL.md` — closes the active clock, derives session_type + title from conversation, writes CSV row + history entry.
- **Skill**: `command-module/plugins/command-module/skills/wrap-up/SKILL.md` — session wrap-up, calls `/co` as part of its flow.
- **Hook registration**: `~/.claude/settings.json` → `hooks.UserPromptSubmit` → `python3 ~/.claude/hooks/auto-clock-in.py`.
- **Clock state**: `missioncontrol/tracking/.active-clock.json` (single file, to be replaced).
- **Timesheet**: `missioncontrol/reports/timesheet.csv` with columns `date,start,end,repo,cluster,session_type,minutes,title,details,source`.
- **Repo→cluster mapping**: `missioncontrol/projects.yaml` (cwd → repo → cluster resolution).

---

## Locked design decisions

### D1. Clock storage → directory, one file per session
`.active-clock.json` → `.active-clocks/{session_id}.json`.

**Why:** Directory of files avoids race conditions (no cross-session read-modify-write on a shared object). Each clock is atomic to its own session. Easy to enumerate for diagnostics (`ls .active-clocks/`).

**Schema of each clock file:**
```json
{
  "session_id": "<claude-session-id-or-generated-uuid>",
  "repo": "revintel",
  "cluster": "revenuemanagement",
  "start": "2026-04-20T08:29:00",
  "date": "2026-04-20",
  "cwd": "/Users/esther/prog/revintel"
}
```

`cwd` is stored for diagnostics and as a weak fallback identifier.

### D2. Hook events → replace `UserPromptSubmit` with `SessionStart` + add `SessionEnd` safety net
- **`SessionStart`**: writes the clock file for this session. Replaces the current `UserPromptSubmit` auto-clock-in.
- **`SessionEnd`**: safety net. If a clock for this session_id still exists when the conversation closes, finalize it automatically — write CSV row with `end=now`, `source=auto-closed`, derive best-effort session_type/title, then delete the clock file.

**Why:** `SessionStart` fires once per conversation, cleanly (no need for rate-limit dedupe). `SessionEnd` ensures no session is silently lost even if the user forgets `/wrap-up` or `/co`.

### D3. Kill the `/tmp/claude-clock-reminded` 30-min dedupe
No longer needed with `SessionStart` (fires exactly once per session).

### D4. Migrate any existing `.active-clock.json` on first run
If `.active-clock.json` exists when the new hook runs, move it to `.active-clocks/legacy.json` with `session_id: "legacy-pre-migration"`. Don't lose any in-flight clock.

### D5. When `cwd` doesn't map to a known repo → still create a clock (don't skip)
**Why the user rejected "default skip":** "that's happening a lot already" — unknown-repo sessions are currently losing time entirely. The session_id mechanism is the point, not repo detection.

Behavior when cwd is unknown:
- Create clock file with `repo: <bare-directory-name>`, `cluster: "unassigned"`.
- At `/co` time, if `cluster == "unassigned"`, prompt the user to assign one (or choose from existing clusters in `projects.yaml`).
- At `SessionEnd` auto-close: if still unassigned, write CSV row with `cluster="unassigned"` and let the user fix up in post.

### D6. Add `session_id` as a new column to `timesheet.csv`
Columns become: `date,start,end,repo,cluster,session_type,minutes,title,details,source,session_id`

**Why:** Debugging/forensics — lets you trace any CSV row back to the conversation that produced it. Especially valuable for `source=auto-closed` rows. Existing rows can be backfilled with `session_id=""` (empty).

### D7. `/wrap-up` and `/co` must key on this session's session_id
Neither skill uses the "find the active clock" heuristic anymore. Both explicitly look up `.active-clocks/{MY_SESSION_ID}.json`, finalize that one file, leave other sessions' clocks alone.

---

## Open question for implementation plan → session_id propagation

**The hard technical question the plan must answer:** how do skills (`/co`, `/wrap-up`, `/ci`) know *which* `session_id` is theirs, given that skills run as Markdown-driven Claude turns, not as processes that natively receive hook stdin?

### Preferred path (verify first)
Claude Code may expose `CLAUDE_SESSION_ID` (or equivalent) as an environment variable available to Bash tool calls inside skills. If so, skills read it via `echo $CLAUDE_SESSION_ID` and look up their own clock file. **This is the cleanest solution — use it if verified.**

### Fallback if not natively exposed
Hook (`SessionStart`) generates a UUID at session start, writes it to a well-known per-session location that skills can reliably read. Candidates:
1. **Inject into Claude's context** via hook's `hookSpecificOutput.additionalContext` — Claude "remembers" its session_id for the rest of the conversation. Risk: context compaction could drop it.
2. **Write to a file whose name is tied to the Claude Code process** (e.g. parent-process PID of the Bash tool). Skills read `$PPID` or walk the process tree. Fragile across platforms.
3. **Write session_id into a per-cwd marker file** (`.claude-session` in cwd). Skills read it. Simple but pollutes working directories.
4. **Environment variable set via shell rc or hook export** — tricky because hook output doesn't always propagate to later tool calls.

**Verification step for plan phase:** before finalizing design, run a small test — does a `Bash` tool call inside a skill see `$CLAUDE_SESSION_ID`? Or any Claude-specific env var that uniquely identifies the conversation? Document the answer.

**If native env var exists:** use it. No fallback needed.
**If not:** the plan picks from the four fallbacks above with a tradeoff analysis.

---

## Affected files / scope

New or modified:
- `~/.claude/hooks/auto-clock-in.py` → repurposed as `SessionStart` hook. Rename? (`session-start-clock.py`?)
- `~/.claude/hooks/session-end-clock.py` → NEW, `SessionEnd` safety-net hook.
- `~/.claude/settings.json` → register `SessionStart` + `SessionEnd` hooks, remove `UserPromptSubmit` auto-clock-in registration.
- `command-module/plugins/command-module/skills/ci/SKILL.md` → update "clock already running" logic to check per-session file; update "write clock" logic to include `session_id`.
- `command-module/plugins/command-module/skills/co/SKILL.md` → look up clock by session_id; handle `cluster=unassigned` prompting.
- `command-module/plugins/command-module/skills/wrap-up/SKILL.md` → same as `/co` on the clock-close step.
- `missioncontrol/tracking/.active-clocks/` → NEW directory (created lazily by hook).
- `missioncontrol/reports/timesheet.csv` → header update (add `session_id` column) + migration of any existing rows (backfill empty).

---

## Out of scope

- Changes to `session_type` derivation logic (that stays as is).
- Changes to the manual-entry flow of `/ci` (time ranges for off-computer work).
- Integration with the planned unified-timesheet redesign (T014) — that's a separate brainstorm. This change is compatible with either timesheet schema.
- Changes to how `/evening` aggregates `project_hours`.

---

## Success criteria

1. Two parallel Claude Code conversations in the same repo can both run independent clocks without conflict.
2. `/co` in either conversation closes *only* that conversation's clock.
3. If a user closes a conversation without running `/wrap-up` or `/co`, `SessionEnd` auto-finalizes the clock with `source=auto-closed`.
4. `timesheet.csv` rows are attributable to their originating session via `session_id` column.
5. Existing behavior for solo sessions is unchanged (no regressions).
6. Migration from `.active-clock.json` to `.active-clocks/` is seamless (no lost in-flight clock).

---

## Next step

Run in command-module repo:
```
/implementation-plan docs/brainstorms/2026-04-20-per-session-clocks-requirements.md
```

Then `/document-review` on the resulting plan, then `/work`.
