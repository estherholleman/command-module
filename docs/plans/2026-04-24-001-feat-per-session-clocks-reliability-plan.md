---
title: Per-session clocks and time-tracking reliability
type: feat
status: active
date: 2026-04-24
origin: docs/brainstorms/2026-04-20-per-session-clocks-requirements.md
---

# Per-session clocks and time-tracking reliability

## Overview

Rewrite the time-tracking subsystem so every Claude Code conversation tracks its own independent clock, keyed by Claude's `session_id`. Replace the single-slot `.active-clock.json` with a directory of per-session files. Replace the sleep-fragile cron-based orphan sweep with a launchd agent that catches up on wake. Absorb the silent-miss path-resolution bug by using absolute paths and failing loud throughout.

This plan covers three coupled problems as one coherent unit of work:

- **A.** Per-session clock architecture (the brainstorm's primary scope)
- **B.** Path-robustness silent-miss bug (absorbed by A — no extra work)
- **C.** Orphan-sweep reliability when the Mac is asleep at 20:00 (cron → launchd)

## Problem Frame

Current system uses a single `.active-clock.json` file, a `UserPromptSubmit` hook that rate-limits itself for 30 minutes, and a cron-scheduled 20:00 sweep. Observed failure modes:

1. **Parallel conversations fight over one slot.** Second conversation asks "clock already running — close it?" every `/ci` attempt, so the user dismisses and time is systematically lost.
2. **`/wrap-up` doesn't know which clock to close.** It closes *the* clock, which may belong to another still-running conversation.
3. **`/co` silent-misses on relative path.** `co/SKILL.md` Step 1 reads `missioncontrol/tracking/.active-clock.json` — a relative path. When CWD isn't `missioncontrol`, the read resolves to a nonexistent path and `/co` responds "no active clock" even though the file exists at the absolute path.
4. **Cron never catches up on sleep.** `0 20 * * * auto-close-clock.py` is installed, but if the Mac is asleep at 20:00 the job silently never runs. Stale clock then blocks `auto-clock-in.py` (which exits early if the file exists) across the next day's conversations.

Incident reproduced 2026-04-23 → 2026-04-24: 20:00 cron missed, stale clock file from the prior evening blocked auto-clock-in across multiple conversations in portfoliostrategyframework the next day, `/co` reported "no active clock" despite the file existing. Tracking for an entire working day was lost.

See origin: `docs/brainstorms/2026-04-20-per-session-clocks-requirements.md` (7 locked design decisions).

## Requirements Trace

All six success criteria from the origin document, plus two derived from the incident and the silent-miss bug:

- **R1.** Two parallel Claude conversations in the same repo can both run independent clocks without conflict. *(origin SC1)*
- **R2.** `/co` in either conversation closes only that conversation's clock. *(origin SC2)*
- **R3.** If a user closes a conversation without `/wrap-up` or `/co`, the clock is auto-finalized by SessionEnd (best-effort) or the launchd orphan sweep (reliable). *(origin SC3)*
- **R4.** `timesheet.csv` rows are attributable to their originating session via a `session_id` column. *(origin SC4)*
- **R5.** Existing behavior for solo sessions is unchanged (no regressions). *(origin SC5)*
- **R6.** Migration from `.active-clock.json` to `.active-clocks/` is seamless — no lost in-flight clock. *(origin SC6)*
- **R7.** `/ci`, `/co`, `/wrap-up` never silent-miss due to CWD — absolute paths throughout, fail loud on missing session_id or missing clock file. *(derived from silent-miss bug)*
- **R8.** Orphan sweep catches up when the Mac was asleep at 20:00. *(derived from the 2026-04-23 incident)*

## Scope Boundaries

Explicit non-goals:

- Not changing `session_type` derivation logic (stays as-is).
- Not changing the manual-entry flow of `/ci` (time ranges for off-computer work).
- Not integrating with T014 unified timesheet — schema-compatible with either outcome.
- Not changing `/morning` or `/evening` aggregation logic.
- Not rewriting `projects.yaml` resolution (port existing logic as-is).
- Not hand-bumping plugin version (release automation handles it).
- Not adding backward-compat shims that keep `.active-clock.json` working after migration — D4 says migrate once, delete old path from code.
- Not moving the Python hooks into repo version control (tracked as deferred-cleanup item; out of scope here).

## Context & Research

### Relevant Code and Patterns

- Current hook: `~/.claude/hooks/auto-clock-in.py` (140 lines; UserPromptSubmit; single-file state; 30-min dedupe). Port `load_repo_cluster_map`, `parse_projects_simple`, `detect_repo_from_cwd` as-is into the new SessionStart hook. **Semantic note:** old hook fires per-prompt (tracks cwd each turn); new hook fires once at SessionStart (freezes repo attribution to startup cwd). Mid-conversation `cd` to a different repo mis-attributes. Acceptable for current usage; a SessionStart + per-turn refresh hybrid is a future option if needed.
- Current sweep: `~/.claude/hooks/auto-close-clock.py` (164 lines; cron-scheduled 20:00 daily). Existing `close_clock`, `write_csv_row`, `write_history_entry` are reusable with minor refactor.
- Current reminder: `~/.claude/hooks/clock-reminder.sh` (22 lines; redundant with SessionStart — to be deleted).
- Skills: `plugins/command-module/skills/{ci,co,wrap-up}/SKILL.md` — all three embed the relative path to `.active-clock.json` that causes the silent-miss bug.
- CSV schema: `missioncontrol/reports/timesheet.csv` header `date,start,end,repo,cluster,session_type,minutes,title,details,source` — to be extended with `session_id` as the 11th column.
- Settings: `~/.claude/settings.json` `hooks.UserPromptSubmit` currently registers both `auto-clock-in.py` and `clock-reminder.sh`; will migrate to `SessionStart` + `SessionEnd`.
- Hook path convention: all existing hooks live at `~/.claude/hooks/` and are NOT versioned in this repo. Kept at the same location for this work. **Deployment implication:** hooks and settings.json live outside the repo, so "merging the PR" alone does not deploy them. The Phase 2 install script (Unit 5) is the actual deployment mechanism — see D5. Versioning the hooks into the repo is captured as deferred work.

### Institutional Learnings

- `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md` — multi-step stateful workflows are state machines; re-read live state at every decision boundary; do not cache values across transitions. **Applies strongly here:** skills must re-read the current session's clock file on each invocation rather than trusting an earlier read. The per-session-file-per-session_id design enforces this structurally: identity is in the filename, not an in-memory value.
- The knowledge base has no prior solutions for Claude Code hooks, launchd vs cron, CWD-relative-path skill bugs, or single-file-to-directory state migrations. This plan will generate three new solution docs (see Documentation Plan).

### External References

- **Claude Code hook docs** (`code.claude.com/docs/en/hooks`, consulted 2026-04-24). SessionStart stdin includes `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `source` (`startup|resume|clear|compact`), `model`. SessionEnd stdin includes `session_id`, `hook_event_name`, `reason` (`clear|resume|logout|prompt_input_exit|bypass_permissions_disabled|other`).
- **Claude Code env vars** (`code.claude.com/docs/en/env-vars`). SessionStart hooks get a `CLAUDE_ENV_FILE` path in the hook's environment. Hook appends `KEY=VALUE` lines to that file and those vars are exported into subsequent Bash tool calls for the same session. `CLAUDE_SESSION_ID` is NOT set natively in Bash tool calls (verified: `echo $CLAUDE_SESSION_ID` returns empty).
- **Open issues on SessionEnd reliability:** anthropics/claude-code #20197 (doesn't fire on API 500), #41577 (async work killed before completion), #17885 (doesn't fire on some `/exit` paths). SessionEnd cannot be the sole reliability mechanism.
- **SessionStart reliability:** Not deeply researched; no known open issues, but treated as best-effort. The launchd sweep (Phase 3) is also the safety net for any "SessionStart silently didn't fire" path — if no clock file is ever written, no sweep action, no harm. The user-visible symptom would be `/ci`/`/co`/`/wrap-up` failing loud with "CLAUDE_SESSION_ID not set" — acceptable compared to silent time loss.
- **Open issues on `CLAUDE_SESSION_ID` env var:** anthropics/claude-code #25642, #13733, #17188, #44607 — all open, none implemented. CLAUDE_ENV_FILE is the currently documented workaround.
- **Apple `launchd.plist(5)` man page.** "Unlike cron which skips job invocations when the computer is asleep, launchd will start the job the next time the computer wakes up." Multiple missed intervals coalesce into one event on wake. LaunchAgent in `~/Library/LaunchAgents/` runs in user's GUI session (right tool for this job, not LaunchDaemon).
- **launchctl commands** — `bootstrap`/`bootout` are current (since macOS 10.11); `load`/`unload` are deprecated. Common silent failures: wrong plist ownership/permissions, non-absolute paths in ProgramArguments, in-place edits without `bootout` + `bootstrap`, System Settings → General → Login Items & Extensions toggle (Sonoma+).

## Key Technical Decisions

### D1. Session_id propagation via `CLAUDE_ENV_FILE` (the crux)

**Decision:** SessionStart hook reads `session_id` from stdin JSON and appends `CLAUDE_SESSION_ID=<id>` to the file path in its `$CLAUDE_ENV_FILE` env var. Bash tool calls in the same session then see `$CLAUDE_SESSION_ID` natively. Skills read it via a small Bash invocation.

**Why this beats the four fallbacks named in the brainstorm:**

| Fallback | Problem |
|---|---|
| `hookSpecificOutput.additionalContext` injection | Lost on `/compact`; model might not reliably surface it |
| PID / parent-process walking | Fragile across tmux, VS Code extension, remote shells |
| `.claude-session` marker file in CWD | Pollutes working directories; concurrent same-CWD sessions conflict |
| Shell rc / hook env export | Propagation to later tool calls unreliable |

`CLAUDE_ENV_FILE` wins because it is: (1) documented and supported, (2) session-scoped (applied only to this session's Bash tool calls), (3) automatically re-applied when SessionStart fires again on `/resume` / `/clear` / `/compact`, (4) zero filesystem pollution outside the user's Claude state dir.

**Rejected alternatives also considered:**

- Transcript path heuristic (`ls -t ~/.claude/projects/<slug>/*.jsonl | head -1`). Transcript filename *does* contain session_id, but mtime only updates on model turns — unreliable in a freshly-opened conversation before the first turn. Also fragile for concurrent same-project sessions.

### D2. SessionEnd is best-effort, not the reliability mechanism

Research-surfaced reality: SessionEnd does not fire on process kill, API 500, OS reboot, or some `/exit` paths. Open issues track this.

**Decision:** SessionEnd hook finalizes the clock opportunistically when it does fire, but the **launchd orphan sweep is the actual reliability guarantee**. Any time a SessionEnd fires with `reason ∈ {clear, resume}`, the hook must **not** finalize — those are lifecycle events (context cleared / session resumed) not terminations. Finalize-eligible reasons: `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`.

### D3. launchd replaces cron for the orphan sweep

- `LaunchAgent` at `~/Library/LaunchAgents/com.esther.auto-close-clock.plist`.
- `StartCalendarInterval { Hour = 20, Minute = 0 }` — catches up on wake per Apple docs.
- Use `launchctl bootstrap gui/$(id -u)` + `launchctl enable` (modern; `load`/`unload` deprecated since 10.11).
- Coalesced-firings caveat: if the Mac was off for 3 days, launchd runs the sweep once, not three times. The existing `auto-close-stale` logic already reconstructs end-times from each clock's timestamp, so one run correctly closes all stale clocks from prior days.
- Crontab entry for `auto-close-clock.py` is removed (with user confirmation) as part of the install step. The unrelated `claude-configs/sync.sh` cron entry is left intact.

### D4. Migrate on first SessionStart run (lazy, not a separate script)

Per brainstorm D4. SessionStart hook, on every invocation, checks whether legacy `.active-clock.json` exists; if so, **discards it** (logs a one-line stderr record of the legacy payload, then unlinks). No CSV row is written for the legacy clock — the start timestamp is potentially days old and would produce a garbage-duration entry. If that day's work mattered, the user can manually enter time via `/ci` manual-entry mode. Tolerant of racing (`FileNotFoundError` → skip).

This is a simpler revision of the original "move to `.active-clocks/legacy.json` with synthetic session_id" plan — writing a synthetic row adds noise and a permanent magic-string sentinel to the CSV schema without adding value.

### D5. Hooks, skills, and settings ship together as one install sequence

The half-shipped case — SessionStart writes per-session but skills still read legacy single-file — silently loses time for every session. There is no safe intermediate state.

**Decision:** Phase 2 ships as one PR *plus* one install step. Because `~/.claude/hooks/*.py` and `~/.claude/settings.json` are not versioned in this repo, "merge" alone doesn't deploy anything. The install sequence (documented in the PR description) is:

1. Merge the Phase 2 PR (skills updated in repo; plugin cache refreshed).
2. Copy the two new hook files into `~/.claude/hooks/` (`session-start-clock.py`, `session-end-clock.py`).
3. Edit `~/.claude/settings.json` to swap the hook registrations (`UserPromptSubmit` → `SessionStart` + `SessionEnd`).
4. Delete the two old hook files (`auto-clock-in.py`, `clock-reminder.sh`).

Between steps 1 and 3 the user is in the half-shipped state. The window must be minutes, not hours. A small install script (Unit 5) automates steps 2–4 so the sequence is one command at the end of the merge.

Orphan-sweep (Phase 3) ships after; the old 20:00 sweep sitting on the legacy path between Phase 2 and Phase 3 harmlessly finds no `.active-clock.json` and exits.

### D6. Rename `auto-clock-in.py` → `session-start-clock.py`

The current name misrepresents the mechanism. Rename pairs naturally with the new `session-end-clock.py` sibling.

### D7. Delete `clock-reminder.sh`

Redundant: SessionStart always creates a clock, so the "remind if no clock" bash hook has no condition under which it should fire. Remove file + settings registration.

### D8. CSV schema migration ships first, standalone (Phase 1)

Add `session_id` as the 11th column; backfill existing rows with empty strings via a one-shot Python migration script; update `CSV_HEADER` constant in the old `auto-close-clock.py` to match. Zero behavioral change, zero rollback risk. Ships alone so the schema surface is stable before Phase 2 starts writing non-empty session_id values.

### D9. Fail-loud everywhere a silent miss used to live

Skills must explicitly surface when `$CLAUDE_SESSION_ID` is empty OR the clock file at `/Users/esther/prog/missioncontrol/tracking/.active-clocks/{session_id}.json` doesn't exist. Error messages name both the expected absolute path and the current session_id. No more silent "no clock" responses that turn out to be path-resolution bugs.

### D10. Skills resolve the clock-file path inline — no helper script

Skill Markdown expands `$CLAUDE_SESSION_ID` inline when issuing the Bash tool call (e.g., `cat "/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json"`). Before reading, the skill asserts `$CLAUDE_SESSION_ID` is non-empty with an explicit error message naming the missing variable and the likely cause (SessionStart hook didn't run or CLAUDE_ENV_FILE wasn't set).

A helper script was considered and rejected as speculative complexity: three skills copying six lines of bash, or a shared helper that centralizes only a hardcoded path. Inline expansion is simpler with no functional loss.

## Open Questions

### Resolved During Planning

- **How do skills know their session_id?** → `CLAUDE_ENV_FILE` mechanism. SessionStart hook writes `CLAUDE_SESSION_ID=<id>` to it; Bash tool calls in the same session see the env var. Settled via external research (see D1).
- **Does SessionEnd reliably fire?** → No. Open issues confirm misses on API 500s, `/exit`, async kills, reboots. Launchd sweep is the safety net; SessionEnd is opportunistic. (D2)
- **Which SessionEnd `reason` values should finalize the clock?** → `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`. NOT `clear` or `resume` — those are lifecycle events within a continuing session. (D2)
- **Does cron catch up on sleep?** → No. launchd `StartCalendarInterval` does. (D3)
- **Migration strategy?** → Lazy, idempotent, inside SessionStart hook — not a separate scripted step. (D4)
- **Can hooks + skills ship separately?** → No. Atomic Phase 2 required. (D5)
- **Filename for session_id directory entries?** → `{session_id}.json`. Session IDs from Claude Code are UUIDs (no colons/reserved chars), so no sanitization needed. Cross-platform filename safety is fine.

### Deferred to Implementation

- **Whether `source=clear` or `source=resume` in SessionStart should reset the clock's start timestamp** (treat `/clear` as a new work-session boundary) or preserve it (treat `/clear` as just a context reset). Defer to implementer; default is preserve — `/clear` is a context operation, not a work-session boundary.
- **CSV row session_id population for auto-close-stale rows** where the session no longer exists: default is to write the session_id from the clock file payload (since the file was originally keyed by it). Implementer confirms during Phase 3.
- **Deduping `CLAUDE_SESSION_ID=<id>` lines in `$CLAUDE_ENV_FILE`** on re-invocation. Harmless either way; implementer picks what's cleanest.
- **Exact helper-script location** for skills (one shared helper vs. per-skill copies). Plugin convention allows both; implementer picks one and follows it for all three skills.
- **Whether to keep the hook-emitted `hookSpecificOutput.message` text** exactly as today or tweak it. UX-only; implementer chooses.

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

### Session_id flow — two parallel conversations, same repo

```
Conversation A starts                         Conversation B starts (parallel, same repo)
──────────────────────────                    ──────────────────────────────────────────────
Claude Code fires SessionStart                Claude Code fires SessionStart
  stdin: {session_id: "A", cwd, ...}            stdin: {session_id: "B", cwd, ...}
  env: CLAUDE_ENV_FILE=/tmp/...envA             env: CLAUDE_ENV_FILE=/tmp/...envB
       │                                             │
       ▼                                             ▼
  session-start-clock.py                         session-start-clock.py
       │                                             │
       ├─ append CLAUDE_SESSION_ID=A                 ├─ append CLAUDE_SESSION_ID=B
       │  to $CLAUDE_ENV_FILE                        │  to $CLAUDE_ENV_FILE
       │                                             │
       ├─ (if legacy .active-clock.json              ├─ (no legacy — already discarded
       │   exists, log payload, unlink once)         │   by conversation A)
       │                                             │
       │                                             │
       ├─ write                                      ├─ write
       │  .active-clocks/A.json                      │  .active-clocks/B.json
       │                                             │
       └─ emit additionalContext:                    └─ emit additionalContext:
          "Auto clocked in: repo (cluster)"             "Auto clocked in: repo (cluster)"

Bash tool call inside A later sees            Bash tool call inside B later sees
$CLAUDE_SESSION_ID="A"                        $CLAUDE_SESSION_ID="B"


Inside conversation A: user runs /co
──────────────────────────────────────
skill reads $CLAUDE_SESSION_ID           ── "A"
skill reads                              ── /Users/esther/prog/missioncontrol/
                                            tracking/.active-clocks/A.json
                                            (absolute — fails loud if missing)
skill derives session_type, title        (unchanged logic)
skill appends CSV row                    (11 cols, session_id=A)
skill deletes .active-clocks/A.json      (B's file untouched)


If conversation A is closed WITHOUT /co or /wrap-up
──────────────────────────────────────────────────────
  Case 1 — SessionEnd fires with reason=logout:
    session-end-clock.py reads .active-clocks/A.json
      → writes CSV row (source=auto-session-end, session_id=A)
      → deletes file

  Case 2 — reason=clear or reason=resume:
    session-end-clock.py exits 0 (lifecycle event, not termination)
    .active-clocks/A.json preserved

  Case 3 — process killed, API 500, OS reboot (SessionEnd never fires):
    .active-clocks/A.json persists
    At next 20:00 (or on wake after missed 20:00) launchd fires:
    auto-close-clock.py iterates .active-clocks/*.json
      → closes A with source=auto-close-20h or auto-close-stale
      → appends CSV row with session_id=A
```

### Directory layout after migration

```
/Users/esther/prog/missioncontrol/tracking/
├── .active-clocks/                    ← NEW directory
│   ├── <session_A_uuid>.json          ← per-session clock files
│   └── <session_B_uuid>.json
├── .active-clock.json                 ← DELETED on first SessionStart after install
└── <repo>/history.jsonl               ← unchanged
```

Legacy `.active-clock.json` is discarded on migration (not converted to a synthetic row) — see D4.

### Clock file schema

```json
{
  "session_id": "<claude-session-id>",
  "repo": "portfoliostrategyframework",
  "cluster": "meta",
  "start": "2026-04-24T16:01:57",
  "date": "2026-04-24",
  "cwd": "/Users/esther/prog/portfoliostrategyframework",
  "source_at_start": "startup"
}
```

`cwd` and `source_at_start` are diagnostic additions — help debug orphan clocks and understand whether the clock came from a fresh start vs. a resume/clear.

## Implementation Units

Four phases plus a pre-flight check. Phases 1 and 2 are dependency-ordered; Phase 3 can lag Phase 2 briefly without breaking anything; Phase 4 runs verification.

### Phase 0 — Pre-flight: verify CLAUDE_ENV_FILE propagation

- [ ] **Unit 0: Smoke-test CLAUDE_ENV_FILE → Bash tool call propagation** *(throwaway hook + checklist staged at `plugins/command-module/staging/smoke-test/`; user runs before merging Phase 2)*

  **Goal:** Before committing Phase 2's atomic rewrite, verify empirically that writing `KEY=value` to `$CLAUDE_ENV_FILE` from a SessionStart hook actually causes subsequent model-issued Bash tool calls in the same session to see `$KEY`. The entire design rests on this mechanism — a 10-minute test prevents a failed rollout.

  **Approach:**
  - Write a throwaway SessionStart hook that appends `CLAUDE_SMOKE_TEST=ok` to `$CLAUDE_ENV_FILE`.
  - Register it in `~/.claude/settings.json`.
  - Open a fresh Claude Code conversation.
  - In a Bash tool call: `echo "$CLAUDE_SMOKE_TEST"`. Expect `ok`.
  - If it returns empty, STOP. The design premise is wrong; revisit D1.
  - Remove the throwaway hook + registration.

  **Verification:** documented result (pass/fail) in the PR that opens Phase 1.

### Phase 1 — CSV schema expansion (ship standalone)

- [ ] **Unit 1: Add `session_id` column to timesheet.csv**

  **Goal:** Extend CSV schema so new rows can reference session_id without breaking existing consumers. Zero behavior change; pure schema expansion.

  **Requirements:** R4

  **Dependencies:** none

  **Files:**
  - Create: `plugins/command-module/scripts/migrate-timesheet-schema.py`
  - Modify: `~/.claude/hooks/auto-close-clock.py` — update `CSV_HEADER` constant to include `"session_id"` as 11th field, append empty string in `write_csv_row`
  - Test: `plugins/command-module/tests/hooks/test_migrate_timesheet_schema.py`

  **Approach:**
  - One-shot migration script that reads `missioncontrol/reports/timesheet.csv`, appends `session_id` column to header if absent, appends empty field to every data row, writes back via temp file + rename (atomic).
  - Idempotent: if header already contains `session_id`, exit with "Already migrated" and no file changes.
  - Update `auto-close-clock.py` in the same PR so existing cron runs write 11-column rows (empty session_id) rather than 10-column rows that would be off-by-one in the expanded schema.

  **Patterns to follow:**
  - Atomic-write via tempfile + `os.replace` — standard Python stdlib pattern.
  - Small one-shot scripts live under `plugins/command-module/scripts/`.

  **Test scenarios:**
  - Empty CSV (just header): header gets `session_id` appended.
  - CSV with rows: every row gets empty 11th field, no column mismatches.
  - Already-migrated CSV: no-op, prints "Already migrated".
  - Malformed CSV (short rows, stray whitespace): fail loud with clear error message, original file untouched.
  - Concurrent invocation: temp-file + rename pattern tolerates (at worst one writer wins).

  **Verification:**
  - `head -1 timesheet.csv` shows 11 fields ending in `session_id`.
  - `awk -F, '{print NF}' timesheet.csv | sort -u` returns only `11` (accounting for quoted-field edge cases — use a proper CSV reader if awk counts mislead).
  - `auto-close-clock.py --dry-run` (or equivalent manual invocation) writes an 11-column row.
  - **Consumer check (gates Phase 1 completion):** open `/morning` and `/evening` reports against the migrated CSV. Confirm they load without errors and produce correct output. If either fails, fix before proceeding to Phase 2.

### Phase 2 — Core rewrite, atomic

All four units in this phase ship together in one PR. No safe intermediate state exists.

- [x] **Unit 2: SessionStart hook — `session-start-clock.py`**

  **Goal:** Replace `UserPromptSubmit` auto-clock-in with `SessionStart`-driven per-session clock creation. Sets up `CLAUDE_SESSION_ID` for subsequent skill invocations.

  **Requirements:** R1, R5, R6

  **Dependencies:** Unit 1

  **Files:**
  - Create: `~/.claude/hooks/session-start-clock.py`
  - Test: `plugins/command-module/tests/hooks/test_session_start_clock.py`
  - (Unit 5 deletes `auto-clock-in.py` after settings.json is updated.)

  **Approach:**
  - Parse JSON from stdin; extract `session_id`, `cwd`, `source`.
  - Read `$CLAUDE_ENV_FILE` env var. If set, append `CLAUDE_SESSION_ID=<id>\n` to that file (idempotent — dedupe the line if already present). If unset, log a warning to stderr (skill-level lookups will fail loud; this is visible, not silent).
  - **Lazy migration:** if `/Users/esther/prog/missioncontrol/tracking/.active-clock.json` exists, log the payload to stderr as a single line (for archival visibility), then `unlink` the file. No CSV row written — see D4. Tolerate `FileNotFoundError` (another concurrent hook already migrated).
  - Compute clock file path: `/Users/esther/prog/missioncontrol/tracking/.active-clocks/{session_id}.json` (absolute).
  - If clock file for this session_id already exists → idempotent no-op (covers `source=resume|clear|compact`).
  - Otherwise resolve repo and cluster from `cwd` using the existing `load_repo_cluster_map` / `parse_projects_simple` / `detect_repo_from_cwd` logic (port as-is).
  - Handle unmapped-cwd case (brainstorm D5): `repo = <basename(cwd)>`, `cluster = "unassigned"`. Still write the clock file — never silently skip.
  - Write clock file with schema shown in High-Level Technical Design.
  - Emit `hookSpecificOutput.additionalContext` message (keep current UX: "Auto clocked in: {repo} ({cluster}) at {HH:MM}. Run /co when done.").
  - Drop the 30-min dedupe via `/tmp/claude-clock-reminded` — no longer needed; also delete any residual file.

  **Patterns to follow:**
  - Existing `auto-clock-in.py` yaml/simple parsing, cwd-to-repo logic — port as-is.
  - JSON stdin parsing pattern from existing Claude Code hook examples.
  - Per plugin AGENTS.md: use absolute paths; fail loud; no shell chaining.

  **Test scenarios:**
  - Fresh `startup`: no legacy, no existing clock → writes clock + env line + message.
  - Legacy `.active-clock.json` present: logs payload to stderr, deletes legacy path, writes current session's file. No CSV row from the discarded legacy.
  - Same `session_id` fires twice (`source=clear`): idempotent — clock file unchanged, env line deduped, no duplicate CSV effect.
  - Unknown cwd (not under `/Users/esther/prog`): writes clock with `repo=<basename>`, `cluster="unassigned"`.
  - Missing `CLAUDE_ENV_FILE`: writes clock, stderr warning; does not crash.
  - Malformed stdin JSON: stderr error, exit 1.
  - Concurrent legacy migration: second invocation silently tolerates missing source file.

  **Verification:**
  - Open a Claude Code conversation. `ls /Users/esther/prog/missioncontrol/tracking/.active-clocks/` lists the new session's file.
  - In a Bash tool call: `echo $CLAUDE_SESSION_ID` returns the id.
  - `.active-clock.json` no longer exists; stderr of the hook run shows the discarded legacy payload (check `~/.claude/hooks/*.log` or Claude Code's hook-error output).

- [x] **Unit 3: SessionEnd hook — `session-end-clock.py`**

  **Goal:** Best-effort finalize-on-conversation-end for reasons that represent true termination. Skip lifecycle-only reasons.

  **Requirements:** R3

  **Dependencies:** Unit 2

  **Files:**
  - Create: `~/.claude/hooks/session-end-clock.py`
  - Test: `plugins/command-module/tests/hooks/test_session_end_clock.py`

  **Approach:**
  - Parse stdin: `session_id`, `reason`.
  - If `reason ∈ {clear, resume}` → exit 0 (lifecycle, not termination). Log at stderr for diagnostics.
  - If `reason ∈ {logout, prompt_input_exit, bypass_permissions_disabled, other}` → proceed.
  - Check `.active-clocks/{session_id}.json`; if missing → exit 0 (clock already closed by `/co` or `/wrap-up`).
  - Read clock; compute `end = now`; default `session_type = "execution"`; title `"Auto-closed at SessionEnd ({reason})"`.
  - Append CSV row with `source = "auto-session-end"`, `session_id = <id>`.
  - Append `history.jsonl` entry (reuse logic from `auto-close-clock.py`).
  - Delete the clock file only after successful writes.

  **Patterns to follow:**
  - `auto-close-clock.py`'s `write_csv_row` and `write_history_entry` — lift into a small shared module (`~/.claude/hooks/_clock_shared.py`) or duplicate inline. Implementer picks; shared module preferred if refactor is low-friction.

  **Test scenarios:**
  - `reason=clear` with clock present: no-op, clock unchanged.
  - `reason=resume` with clock present: no-op.
  - `reason=logout` with clock present: CSV row written, history written, clock deleted.
  - `reason=logout` with no clock (already finalized by `/co`): no-op.
  - `reason=other` (unknown-but-terminal): finalizes.
  - Malformed stdin: exit 1 to stderr.

  **Verification:** close a conversation via `/exit` — CSV shows row with `source=auto-session-end`, `session_id` matches that conversation.

- [x] **Unit 4: Update `/ci`, `/co`, `/wrap-up` skills for per-session keying**

  **Goal:** All three skills key on `$CLAUDE_SESSION_ID`, use absolute paths, fail loud on missing clock or missing session id.

  **Requirements:** R1, R2, R4, R5, R7

  **Dependencies:** Unit 2 (skills depend on the env var set by SessionStart)

  **Files:**
  - Modify: `plugins/command-module/skills/ci/SKILL.md`
  - Modify: `plugins/command-module/skills/co/SKILL.md`
  - Modify: `plugins/command-module/skills/wrap-up/SKILL.md`

  **Approach:**
  - Replace every `missioncontrol/tracking/.active-clock.json` reference with the inline-expanded absolute path `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` in each Bash tool call (see D10 — no helper script).
  - Before any clock read, the skill instructs the model to assert `$CLAUDE_SESSION_ID` is non-empty; if empty, display a specific error (naming the missing var and that SessionStart is the expected setter) and stop.
  - **`/ci` Normal Clock-In mode:**
    - Because SessionStart auto-creates a clock on every session, bare `/ci` will almost always hit the "already running" branch. **New UX:** bare `/ci` becomes an informational no-op — prints `"Clock running for this session since HH:MM ({repo}, {cluster}). Use /ci --force to reset or /ci <range> for manual entry."` Exits successfully.
    - Write clock file with `session_id` field populated (used when SessionStart didn't fire, e.g., bare `/ci` after hook failure).
    - `--force` closes the current session's clock and opens a fresh one.
  - **`/ci` Manual Entry mode:** unchanged (no state file involved; explicitly in scope per brainstorm "out of scope" list).
  - **`/co`:**
    - Step 1: read the per-session clock file via inline `$CLAUDE_SESSION_ID` expansion. If `$CLAUDE_SESSION_ID` empty → error message names the missing var and instructs user to check SessionStart/hook state. If file missing → error names the expected absolute path and the session_id. No silent "no clock" response.
    - Step 5: CSV row includes `session_id` as 11th field.
    - **New step** (from brainstorm D5): if clock's `cluster == "unassigned"`, prompt user to pick a cluster before writing the CSV row — use the platform's question tool (AskUserQuestion / request_user_input / ask_user), with fallback of presenting numbered options. Offer existing clusters from `projects.yaml` as options. In non-interactive contexts (no question tool available AND no user response), write the row with `cluster="unassigned"` and exit — user can correct manually later.
    - Step 6: delete only the per-session clock file.
  - **`/wrap-up`:**
    - Step 1: read `missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` via inline expansion.
    - Step 1.5: clock-check only surfaces THIS session's clock. Prompt and `/co` flow unchanged otherwise.
  - Update all prose in the three SKILL.md files to say "this session's clock" rather than "the active clock" wherever the distinction matters.

  **Patterns to follow:**
  - Cross-platform user-interaction rule: name platform-specific question-tool equivalents in the skill prose.
  - Frontmatter rules (names match dir names, descriptions quoted if they contain colons) — run `bun test tests/frontmatter.test.ts` after editing.

  **Test scenarios (mostly manual — see Unit 9 checklist):**
  - Two conversations in same repo, each runs `/co`: each finalizes only its own clock, CSV shows two distinct session_ids.
  - `/co` with empty `$CLAUDE_SESSION_ID`: fails loud, error names the missing var.
  - `/co` with session_id set but missing clock file: fails loud, error names the expected absolute path.
  - `/co` on a clock with `cluster=unassigned`: prompts for cluster; CSV row uses chosen cluster.
  - `/ci` in conversation where SessionStart already ran: "Clock already running for this session since HH:MM".
  - `/wrap-up` in one conversation while another has a clock: only this session's clock surfaces in Step 1.5.
  - Frontmatter validation (`bun test tests/frontmatter.test.ts`) passes.

  **Verification:**
  - `bun test` passes (frontmatter harness unchanged).
  - Manual two-conversation scenario (Unit 9 checklist) shows per-session independence.

- [x] **Unit 5: Install script — `install-phase2.sh`**

  **Goal:** One command that copies the new hooks into `~/.claude/hooks/`, updates `~/.claude/settings.json` to register `SessionStart`/`SessionEnd` and remove the old `UserPromptSubmit` entries, and deletes the obsolete hook files. Operationally the "deploy" step of Phase 2.

  **Requirements:** R1, R3, R5

  **Dependencies:** Units 2, 3, 4 (all hook and skill components must exist before settings.json is flipped — per D5, no safe intermediate state)

  **Files:**
  - Create: `plugins/command-module/scripts/install-phase2.sh`
  - (Script operates on:) `~/.claude/hooks/session-start-clock.py`, `~/.claude/hooks/session-end-clock.py`, `~/.claude/settings.json`, `~/.claude/hooks/auto-clock-in.py` (delete), `~/.claude/hooks/clock-reminder.sh` (delete), `/tmp/claude-clock-reminded` (delete if present).

  **Approach:**
  - Copy hook files from the repo (source location decided when hooks get versioned — for now, script accepts `--hook-source <dir>` or reads from a hand-provided staging dir).
  - JSON-patch `~/.claude/settings.json`:
    - Add `hooks.SessionStart`: matcher `startup|resume|clear|compact`, command `/usr/bin/python3 /Users/esther/.claude/hooks/session-start-clock.py`.
    - Add `hooks.SessionEnd`: no matcher (the hook itself filters by `reason` — SessionEnd matchers filter on tool-name in current Claude Code, which is meaningless here). Command `/usr/bin/python3 /Users/esther/.claude/hooks/session-end-clock.py`.
    - Remove `UserPromptSubmit` entries pointing at `auto-clock-in.py` or `clock-reminder.sh`.
    - Preserve all other hook and permission entries exactly (use `jq` or a small Python patcher — do not hand-edit).
  - Back up settings.json to `~/.claude/settings.json.bak.YYYYMMDDHHMMSS` before editing.
  - Delete the two old hook files + the residual `/tmp` file.
  - Print a post-install checklist (open a fresh conversation, verify hooks fired, etc.).
  - Idempotent: re-running does nothing harmful.

  **Test scenarios:**
  - Start a fresh Claude Code conversation → SessionStart hook fires (per-session clock file created).
  - Run `/exit` → SessionEnd fires, clock finalized.
  - Run `/clear` → SessionEnd fires with `reason=clear`, hook logs but does not finalize; subsequent SessionStart fires with `source=clear` and is idempotent.
  - `UserPromptSubmit` no longer triggers a clock-in action.

  **Verification:**
  - `grep -E "auto-clock-in|clock-reminder" ~/.claude/settings.json` returns nothing.
  - The two old hook files are gone.
  - `ls ~/.claude/hooks/` shows only the new filenames + the auto-close-clock.py.

### Phase 3 — Orphan-sweep reliability

- [ ] **Unit 6: Update `auto-close-clock.py` for multi-file layout**

  **Goal:** Sweep iterates `.active-clocks/*.json` instead of a single file; writes CSV rows with session_id populated.

  **Requirements:** R3, R8

  **Dependencies:** Phase 2 complete

  **Files:**
  - Modify: `~/.claude/hooks/auto-close-clock.py`
  - Test: `plugins/command-module/tests/hooks/test_auto_close_clock.py`

  **Approach:**
  - Replace `CLOCK_FILE` constant with `CLOCKS_DIR = MISSION_CONTROL / "tracking" / ".active-clocks"`.
  - `main()` iterates `CLOCKS_DIR.glob("*.json")`; for each, calls refactored `close_clock(path)` that takes a file path.
  - Keep existing policies: `start_date == today and now < 20:00 → cap at 20:00`; `start_date < today → end at 20:00 of start_date (or +30min fallback for late-night starts)`.
  - `source` values unchanged: `auto-close-20h` for today, `auto-close-stale` for prior days.
  - CSV row writes `session_id` from clock payload.
  - Delete each clock file only after its CSV row and history entry are written successfully.
  - Empty or missing directory → no-op, clean exit (tolerate `FileNotFoundError` on the glob).

  **Patterns to follow:**
  - Existing `close_clock` / `write_csv_row` / `write_history_entry` — refactor `close_clock` to take a path and extract clock payload inside.

  **Test scenarios:**
  - Empty `.active-clocks/`: no-op, exits 0.
  - One fresh clock from today, current time before 20:00: closed at 20:00.
  - Multiple clocks from today (parallel sessions both left open): all closed independently, each CSV row has its own session_id.
  - Stale clock from yesterday with start before 20:00: closed at yesterday's 20:00, source=auto-close-stale.
  - Stale clock from yesterday with start after 20:00: +30min fallback duration.
  - Mix of today + stale clocks: all handled correctly in one pass.
  - Missing `.active-clocks/` directory: clean exit, no crash.
  - Partial-write failure (disk full simulation): clock file NOT deleted on exception; re-run resumes.

  **Verification:**
  - Manual: create two test clock files under `.active-clocks/` with known timestamps, run `python3 auto-close-clock.py`, confirm both CSV rows and both files deleted.

- [ ] **Unit 7: launchd plist replaces cron**

  **Goal:** Install `~/Library/LaunchAgents/com.esther.auto-close-clock.plist` that runs the sweep at 20:00 daily with on-wake catch-up; remove the cron entry.

  **Requirements:** R3, R8

  **Dependencies:** Unit 6

  **Files:**
  - Create: `plugins/command-module/scripts/install-auto-close-launchagent.sh`
  - Create (generated by script, not committed): `~/Library/LaunchAgents/com.esther.auto-close-clock.plist`

  **Approach:**
  - Install script generates the plist in-place (avoid committing a user-specific label/path to the repo — keep the script as the source of truth; user can re-run after path changes).
  - Plist contents: `Label=com.esther.auto-close-clock`, `ProgramArguments=[/usr/bin/python3, /Users/esther/.claude/hooks/auto-close-clock.py]`, `StartCalendarInterval { Hour=20, Minute=0 }`, `StandardOutPath=/Users/esther/.claude/hooks/auto-close.log`, `StandardErrorPath=/Users/esther/.claude/hooks/auto-close.log`.
  - Install sequence: `bootout` (tolerant of missing), `bootstrap`, `enable`, `kickstart` (test-run), `print` (verification output).
  - Remove the existing cron entry: `crontab -l | grep -v 'auto-close-clock.py' | crontab -`. **Prompt user first** (destructive on shared config; ask yes/no before editing crontab). Leave the `claude-configs/sync.sh` cron entry intact.
  - Script is idempotent: re-running just re-installs cleanly.
  - Print next-firing timestamp at end for verification.

  **Patterns to follow:**
  - Single shell script under `plugins/command-module/scripts/` for one-shot install tools. Plain bash; `set -euo pipefail` at top.
  - Treat crontab edit as a destructive action — confirmation required (see CLAUDE.md global safety rule).

  **Test scenarios:**
  - Fresh install (no existing plist, no cron entry): plist created, agent loaded, kickstart runs without error.
  - Re-install (plist already exists): `bootout` succeeds, `bootstrap` re-adds with new content; idempotent.
  - User declines crontab edit at prompt: script installs launchd but leaves cron entry; prints warning that both will now run (user can remove cron entry manually).
  - After install: `launchctl print gui/$(id -u)/com.esther.auto-close-clock` shows state=scheduled, next-firing is 20:00 today or tomorrow.

  **Verification:**
  - `launchctl print gui/$(id -u)/com.esther.auto-close-clock | grep -iE 'state|runat'` returns active state and a future timestamp.
  - `crontab -l | grep auto-close-clock.py` returns nothing (after user confirms removal).
  - One manual sleep-wake cycle: `sudo pmset sleepnow` after 20:00 with a test clock present, wake, confirm sweep ran.

- [ ] **Unit 8: Document launchd install + pattern in solutions doc**

  **Goal:** Capture institutional knowledge — future-me (or another contributor) hits a similar "cron doesn't catch up on sleep" problem and finds the answer.

  **Requirements:** none directly; cross-cutting knowledge capture

  **Files:**
  - Create: `docs/solutions/developer-experience/launchd-replaces-cron-for-sleep-aware-scheduling-2026-04-24.md`

  **Approach:** document:
  - The failure mode (cron silently skips missed intervals on sleep).
  - The fix (launchd `StartCalendarInterval` + `bootstrap`/`bootout`).
  - Coalesced-firings caveat (multiple missed → one run).
  - Top 3 silent-failure pitfalls (ownership, absolute paths, System Settings login-items toggle).
  - The install script location and how to re-run.
  - Sources: Apple `launchd.plist(5)` man page.

### Phase 4 — Verification and knowledge capture

- [ ] **Unit 9: Manual parallel-sessions test checklist**

  **Goal:** Human-run ordered checklist to verify the six success criteria end-to-end. Automated parallel-conversation testing isn't feasible — this is the pragmatic substitute.

  **Requirements:** R1, R2, R3, R4, R5, R6, R7, R8

  **Dependencies:** Phase 2 complete (Unit 9 steps 3-9); Phase 3 complete (steps 10-11)

  **Files:**
  - Create: `docs/plans/2026-04-24-001-test-checklist-per-session-clocks.md`

  **Approach:** ordered scenarios the user runs once after Phase 2 ships, then again after Phase 3 ships. Each line states the action and the expected observable outcome.

  **Checklist content (summary; full version in the checklist file):**
  1. **Pre-migration baseline.** Record current state of `.active-clock.json` and `.active-clocks/` if present.
  2. **Deploy Phase 2** (merge + hook files installed).
  3. **Fresh conversation.** Open one Claude Code conversation. Verify: (a) `.active-clocks/<session_id>.json` created; (b) `.active-clock.json` no longer exists (discarded on migration); (c) stderr log of the hook run contains the discarded legacy payload if a legacy file had existed.
  4. **Env var propagation.** In the same conversation's Bash tool: `echo $CLAUDE_SESSION_ID` returns a uuid.
  5. **Parallel start.** Open a second conversation in the same repo. Verify: two distinct files in `.active-clocks/`; each conversation's `$CLAUDE_SESSION_ID` matches its own file.
  6. **Independent `/co`.** In conversation 1, run `/co`. Verify: only conversation 1's clock file deleted; conversation 2's untouched; CSV row has session_id matching conversation 1.
  7. **Wrap-up isolation.** In conversation 2, run `/wrap-up`. Verify: Step 1.5 surfaces only conversation 2's clock.
  8. **`/clear` preservation.** In a third conversation, run `/clear`. Verify: clock file unchanged; SessionEnd fires with `reason=clear` but no CSV row written; subsequent `$CLAUDE_SESSION_ID` unchanged.
  9. **SessionEnd finalize.** In a fourth conversation, exit via `/exit` (or close terminal). Verify: CSV row with `source=auto-session-end`, clock file deleted.
  10. **Orphan sweep — stale day.** Manually write a clock file dated yesterday into `.active-clocks/fake.json`. Invoke `python3 auto-close-clock.py` directly. Verify: CSV row with `source=auto-close-stale`, session_id preserved, clock file deleted.
  11. **launchd scheduling.** `launchctl print gui/$(id -u)/com.esther.auto-close-clock | grep -iE 'next|runat'` returns a future 20:00 timestamp.
  12. **Silent-miss regression check.** In a conversation where `CLAUDE_SESSION_ID` is somehow unset (simulate by `unset CLAUDE_SESSION_ID` in a Bash call), run `/co`. Verify: explicit error message names the missing var — no silent success or silent "no clock".
  13. **Cluster-unassigned prompting.** Manually write a test clock with `cluster="unassigned"`, run `/co`. Verify: prompts for cluster choice before writing CSV.

- [ ] **Unit 10: Write two solution docs capturing the CWD and migration patterns**

  **Goal:** Fill the two institutional-knowledge gaps the research surfaced.

  **Requirements:** none; knowledge capture

  **Files:**
  - Create: `docs/solutions/integrations/cwd-relative-paths-silent-miss-in-skills-2026-04-24.md`
  - Create: `docs/solutions/skill-design/single-file-to-per-session-state-migration-2026-04-24.md`

  **Approach:**
  - First doc: describe the silent-miss failure mode (relative paths in skill markdown resolve against the current conversation's CWD, not the skill's intended base), the fix (absolute paths + inline `$CLAUDE_SESSION_ID` expansion + fail-loud on missing var).
  - Second doc: describe the migration pattern (single-slot state file → directory-of-files keyed by identity), the `CLAUDE_ENV_FILE` mechanism for session_id propagation, and why the legacy state is discarded on migration rather than synthetically finalized (avoids permanent magic-string sentinels in output data and garbage-duration CSV rows).

- [ ] **Unit 11: Mark T015 complete**

  **Goal:** Reflect work completion in missioncontrol tracking.

  **Files:**
  - Modify: `/Users/esther/prog/missioncontrol/tracking/command-module/tasks/T015.md`

  **Approach:** change frontmatter `status: next` → `status: done`; add a completion note referencing this plan file and the ship PR(s).

## System-Wide Impact

- **Interaction graph:** SessionStart + SessionEnd are new hook events attached to every Claude Code conversation. UserPromptSubmit no longer triggers clock-in logic. Skills (`/ci`, `/co`, `/wrap-up`) now depend on `CLAUDE_ENV_FILE`-injected env var; if that mechanism breaks in a future Claude Code version, skills will fail loud (no silent corruption).
- **Error propagation:** Hook failures exit non-zero → surfaced in Claude Code output. Skills fail loud on missing session_id or missing clock file with explicit messages naming the missing resource. Helper script (`clock-path.sh`) exits 1 on empty session_id, making the failure visible at the shell layer.
- **State lifecycle risks:**
  - `.active-clocks/` directory accumulates files if SessionEnd and launchd sweep both miss — unlikely but possible. Mitigation: sweep runs every 20:00 with on-wake catch-up; manual cleanup is cheap.
  - `CLAUDE_ENV_FILE` writes must be idempotent across SessionStart re-firings (`/resume`, `/clear`, `/compact`); dedupe lines on write.
  - Lazy migration races: two SessionStart hooks for different sessions starting at nearly the same time could both attempt to migrate legacy.json. Handled via `shutil.move` atomicity and `FileNotFoundError` tolerance.
  - Clock file for unmapped cwd still gets created (brainstorm D5) with `cluster="unassigned"` — prevents silent loss; `/co` prompts for cluster at close time.
- **API surface parity:** No external API changes. CSV schema gains one column; internal consumers (`/morning`, `/evening`, reports) must tolerate 11 columns. Verify these consumers either ignore unknown columns or explicitly accept the new schema.
- **Cross-cutting integrations:** No downstream tools currently read `.active-clock.json` (`grep` confirms only hooks and the three skills reference it). Path change has no wider blast radius.
- **Logging:** `~/.claude/hooks/auto-close.log` remains the sweep's stdout/stderr sink. SessionStart / SessionEnd hooks log diagnostics to stderr (visible in Claude Code hook-error output on failure).

## Risks & Mitigations

- **R-H1 (high): `CLAUDE_ENV_FILE` behavior changes or is removed from Claude Code.** Mitigation: D1 documents the dependency; if the future Claude Code exposes `CLAUDE_SESSION_ID` natively (issue #25642 tracks this), migration is one-line in each hook. Helper script (`clock-path.sh`) localizes the dependency to one resolution point.
- **R-H2 (high): SessionStart stdin schema shifts.** Mitigation: hook parses JSON defensively; `session_id = data.get("session_id")` with explicit error on missing key. Plan documents the Claude Code version the hooks were written against.
- **R-M1 (medium): Legacy-migration race between two concurrent SessionStart hooks.** Mitigation: `shutil.move` is atomic; `FileNotFoundError` tolerance in the second hook; second migrator just skips.
- **R-M2 (medium): SessionEnd finalizes on a `reason` value we didn't anticipate.** Mitigation: explicit whitelist of terminate-eligible reasons; any unexpected value triggers finalization (`other` catch-all) — failure mode is an auto-closed row the user corrects later, not data loss.
- **R-M3 (medium): launchd install requires interactive `crontab` edit.** Mitigation: install script prompts yes/no before editing. User can skip and remove cron manually.
- **R-M4 (medium): macOS System Settings → General → Login Items & Extensions can silently disable the LaunchAgent** (Sonoma+). Mitigation: Unit 8 solution doc calls this out as a top silent-failure cause with verification steps.
- **R-L1 (low): CSV consumers can't handle 11-column rows.** Mitigation: `/morning` and `/evening` compatibility is now a Phase 1 verification gate (Unit 1), not a post-ship follow-up. Phase 2 does not begin until they load the migrated CSV cleanly.
- **R-L2 (low): Test harness drift — hooks live outside repo so tests may not be run as part of standard `bun test`.** Mitigation: add a `make test-hooks` or `bun run test:hooks` equivalent that invokes pytest against the hook tests. Docs Plan item below.
- **R-L3 (low): User forgets to re-run install script after receiving plan.** Mitigation: Unit 7 install script is self-documenting (prints next steps on completion); Unit 8 solution doc anchors the procedure for future reference.

## Phased Delivery

### Phase 1 — CSV schema (standalone)
- **Units:** 1
- **Shippable state:** CSV has 11 columns; all writers (old and new) write 11 columns; session_id field empty for now.
- **Rollback:** revert one PR; schema expansion is harmless even if unused.

### Phase 2 — Hooks + skills + install (sequenced)
- **Units:** 2, 3, 4, 5
- **Shippable state:** Per-session clocks fully operational. Parallel conversations tracked independently. Old single-file path gone.
- **Ship sequence (one short session — minutes, not hours):**
  1. Merge the PR (skills + install script land in repo; plugin cache refreshes).
  2. Run the install script: copies new hook files into `~/.claude/hooks/`, edits `settings.json` to register `SessionStart`/`SessionEnd` and remove `UserPromptSubmit` entries, deletes `auto-clock-in.py` + `clock-reminder.sh`.
  3. Open a fresh conversation to verify (`ls .active-clocks/`, `echo $CLAUDE_SESSION_ID`).
- **Rollback (if verification fails):** Concrete steps:
  1. `git revert` the PR — skills return to legacy path.
  2. Restore `~/.claude/hooks/auto-clock-in.py` and `clock-reminder.sh` from git history of their original location (or re-create from the ports in the reverted PR).
  3. Edit `~/.claude/settings.json` to remove `SessionStart`/`SessionEnd` entries and restore `UserPromptSubmit` registrations.
  4. If a legacy `.active-clock.json` was discarded by SessionStart, it's gone. Minor data loss — at most one in-flight clock. Manually recreate via `/ci` if the session's time matters.
  5. Delete any files already written to `.active-clocks/` — they would be orphaned by the reverted code.
  This is documented in the PR description. Rollback is destructive; use only if Phase 2 verification reveals a fundamental problem.

### Phase 3 — Orphan sweep + launchd (ship after Phase 2)
- **Units:** 6, 7, 8
- **Shippable state:** Sweep handles multi-file layout; launchd catches up on wake. Old 20:00 cron removed.
- **Can lag Phase 2 briefly** — between Phase 2 ship and Phase 3 ship, the unchanged cron sweep will find `.active-clock.json` missing and exit cleanly with "no active clock, nothing to do". No regression, just no sweep coverage for the gap.
- **Rollback:** revert PR; re-install cron entry manually.

### Phase 4 — Verification + knowledge capture
- **Units:** 9, 10, 11
- **Checklist runs** after Phase 2 (steps 1–9, 12, 13) and again after Phase 3 (steps 10, 11).
- Solution docs (Unit 10) land after Phase 3; T015 closure (Unit 11) after Phase 4 checklist passes.

## Test Strategy

Three tiers; pragmatic given the Markdown-skill + external-hook mix:

1. **Python unit tests — hook logic in isolation.** New directory `plugins/command-module/tests/hooks/`. Pytest-style tests feed synthetic stdin JSON and a tmp-dir-backed filesystem to each hook. Scope: stdin parsing, env-file writes (with mocked `CLAUDE_ENV_FILE`), idempotency, migration logic, CSV writing, reason-gating. Does **not** require a running Claude Code instance. Invoke via `python3 -m pytest plugins/command-module/tests/hooks/`. Add a `bun run test:hooks` npm script wrapper for discoverability.
2. **Skill syntax tests — existing repo harness.** `bun test tests/frontmatter.test.ts` validates SKILL.md parseability. No new infrastructure; just ensure edits don't introduce unquoted colons or name/description drift.
3. **Manual parallel-session checklist — human-in-the-loop.** Unit 9 documents the ordered scenarios. There's no feasible automation for two simultaneous Claude Code conversations within this repo's test surface. Treat as acceptance gate.

**Primary:** unit tests. **Fallback:** manual checklist for behaviors that can only be observed via real conversations.

## Documentation Plan

- `docs/solutions/integrations/cwd-relative-paths-silent-miss-in-skills-2026-04-24.md` — Unit 10
- `docs/solutions/skill-design/single-file-to-per-session-state-migration-2026-04-24.md` — Unit 10
- `docs/solutions/developer-experience/launchd-replaces-cron-for-sleep-aware-scheduling-2026-04-24.md` — Unit 8
- `docs/plans/2026-04-24-001-test-checklist-per-session-clocks.md` — Unit 9
- `plugins/command-module/README.md` — update if skill descriptions change (they shouldn't; verify).
- `plugins/command-module/AGENTS.md` — no update needed; existing guidance on absolute paths / fail-loud covers the design.
- T015 task file — closure note (Unit 11).

## Deferred Work (captured for later)

Per the three-flavor deferred-work pattern (see `docs/solutions/skill-design/deferring-work-three-flavors-*.md`):

1. **Same-repo, condition-triggered** — **Version-control the `~/.claude/hooks/*.py` files.** Currently authored in-place; no git history. Move under `plugins/command-module/hooks/` or similar and wire into `install.sh`. Trigger: after this plan ships and is verified stable. Captured as a task in missioncontrol tracking (to be created on ship).
2. **Same-repo, condition-triggered** — **Add `bun run test:hooks` script.** Currently `bun test` doesn't invoke the new pytest suite. Trigger: when Phase 2 lands (Unit 2/3 tests exist). Captured as a TODO comment in the test directory's README.
3. ~~**Cross-repo follow-up** — Confirm `/morning` and `/evening` tolerate 11-column CSV.~~ **Promoted to a Phase 1 verification gate** (see Unit 1). Must pass before Phase 2 begins.

All three surface back to the user in the post-plan summary (see Phase 5 handoff).

## Sources & References

- **Origin document:** `docs/brainstorms/2026-04-20-per-session-clocks-requirements.md`
- **Claude Code hook reference:** https://code.claude.com/docs/en/hooks (SessionStart / SessionEnd stdin schemas, hookSpecificOutput.additionalContext)
- **Claude Code env vars:** https://code.claude.com/docs/en/env-vars (CLAUDE_ENV_FILE behavior)
- **SessionEnd reliability issues:** anthropics/claude-code #20197, #41577, #17885
- **CLAUDE_SESSION_ID env var feature requests:** anthropics/claude-code #25642, #13733, #17188, #44607
- **launchd `StartCalendarInterval` on-wake behavior:** Apple `launchd.plist(5)` man page
- **launchctl modern commands:** `bootstrap`/`bootout` (since macOS 10.11; `load`/`unload` deprecated)
- **Institutional learning — state machine discipline:** `docs/solutions/skill-design/git-workflow-skills-need-explicit-state-machines-2026-03-27.md`
- **Institutional learning — deferred work pattern:** `docs/solutions/skill-design/deferring-work-three-flavors-2026-04-19.md`
- **Current hook source:** `~/.claude/hooks/auto-clock-in.py`, `~/.claude/hooks/auto-close-clock.py`, `~/.claude/hooks/clock-reminder.sh`
- **Current skills:** `plugins/command-module/skills/{ci,co,wrap-up}/SKILL.md`
- **T015 task:** `/Users/esther/prog/missioncontrol/tracking/command-module/tasks/T015.md`
- **Incident evidence:** 2026-04-23 → 2026-04-24 portfoliostrategyframework stale-clock cascade, current stale clock at `/Users/esther/prog/missioncontrol/tracking/.active-clock.json` (2026-04-24T16:01:57)
