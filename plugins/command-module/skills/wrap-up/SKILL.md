---
name: wrap-up
description: "Wrap up this session and update all tracking files. Use when the user says 'wrap up', 'end session', 'wrap this up', or wants to finalize session state and commit changes."
---

# Wrap Up

Finalize the current session by updating tracking files and committing changes.

## Context

Tracking data lives in `/Users/esther/prog/missioncontrol/tracking/{repo-name}/` -- determine the repo name from the current working directory.

This session's clock (if any) lives at `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json`. Other conversations have their own clocks in the same directory; do not touch them.

## Workflow

### Step 1: Gather state

Read these in parallel:

- `/Users/esther/prog/missioncontrol/tracking/{repo}/tasks/index.json` -- current task state
- `/Users/esther/prog/missioncontrol/tracking/{repo}/status.json` -- current briefing
- `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` -- this session's clock (if any)
- Run `git status` -- check for uncommitted changes

If `$CLAUDE_SESSION_ID` is empty, surface a specific error and stop:

> ERROR: `CLAUDE_SESSION_ID` is empty. SessionStart hook did not set it (CLAUDE_ENV_FILE mechanism). Cannot identify this conversation's clock. Aborting.

### Step 1.5: Clock check (this session only)

If `/Users/esther/prog/missioncontrol/tracking/.active-clocks/${CLAUDE_SESSION_ID}.json` exists:

- If its `start` is `null` (armed but never started — no substantive work), there is nothing to
  clock out. Skip clock handling and proceed with the rest of wrap-up.
- Otherwise compute the **honest engaged minutes**: `end = last_activity` (fall back to now),
  `minutes = accrued_seconds/60 + (end − start)` — i.e. the closed sub-spans (`accrued_seconds`,
  default 0 when absent) plus the current open span. Idle gaps > 30 min were already excluded by the
  clock (they seal a sub-span). Use `work_start` (fall back to `start`) as the row's start time so the
  window brackets the whole session. This is first-real-action → last-real-action, **not** tab-open → now.
- **Interactive wrap-up**: tell the user "You have ~{X} min of tracked work on **{repo}** (since
  {start}). Clock out?"
  - **If yes**: run the `/co` flow — derive session_type from context, propose title and details,
    write the CSV row (`source=clock`, `session_id` populated), append to `history.jsonl`, and
    delete only this session's clock file.
  - **If no**: proceed without clocking out.
- **Automatic mode** (invoked by the idle wrap-on-return gate — see the section below): do NOT ask;
  finalize the honest span, write the entry with `source=auto-wrap`, then RESET the clock instead of
  deleting it.

If the file does not exist, no other conversation's clock is shown and no prompt is issued — wrap-up proceeds.

### Step 2: Identify changes

Scan the conversation for tasks worked on, status changes, and any uncaptured work. If there are uncaptured items, note them in the summary rather than blocking for confirmation.

### Step 3: Update tracking files

Write these in parallel:

- Update each modified task's `tasks/T00N.md` frontmatter (status, updated date)
- Update `tasks/index.json` with matching changes (and any new task entries)
- Append to `history.jsonl`: session entry + `status_change` entries + `task_created` entries
- Write `status.json`: curated briefing with summary, highlights, active/blocked/upcoming tasks

### Step 4: Commit and push

If there are uncommitted changes in the current repo, stage and commit with a clear message. Commit tracking file changes in missioncontrol separately if needed.

**Always push missioncontrol after its tracking commit:** `git -C /Users/esther/prog/missioncontrol push`. The private GitHub remote is what the cloud Flight Director reads — tracking that isn't pushed is invisible to it. If the push fails (offline, auth), mention it in the report and continue; never block wrap-up on a push. This applies ONLY to missioncontrol — never push any other repo unless the user asks.

**Parallel wrap-ups collide:** several conversations can wrap up at once in the same missioncontrol clone. If a commit fails with `Unable to create '.git/index.lock'`, wait ~3 seconds and retry once (the other wrap-up finishes fast). If the push is rejected because another session just pushed, `git -C /Users/esther/prog/missioncontrol pull --rebase` then push once more — never force-push, and never block the wrap-up on it.

### Step 5: Report

Show a brief summary of what was updated.

---

## Automatic mode (hook-triggered)

The **idle wrap-on-return gate** (`~/.claude/hooks/idle-wrap-on-return.py`, UserPromptSubmit)
injects an instruction that brings you here **without the user asking** — it fires when the user
returns to a conversation whose previous work burst ended ≥ 30 min ago (`IDLE_WRAP_MINUTES`,
env-overridable). A session boundary is real silence, never a turn-end guess, so wraps no longer
fire mid-conversation. When you arrive that way, run wrap-up in **automatic mode** — the whole
point is that Esther never has to babysit tracking or git:

1. **Wrap first, then answer.** You arrive at the START of a turn: the user's new message is
   waiting behind the wrap. Read the clock file **before any Bash/Edit call this turn** (Read does
   not advance the heartbeat) so `last_activity` still marks the true burst end. Wrap the ended
   burst even if its task is unfinished — a wrap records a **time segment**, not task completion
   (statuses simply stay `in_progress`). Only skip when `start` is `null` (nothing to wrap). After
   the one-line wrap confirmation, address the user's message normally in the same turn.

2. **Finalize the honest clock.** Read `.active-clocks/${CLAUDE_SESSION_ID}.json`. Honest engaged
   minutes = `accrued_seconds/60 + (last_activity − start)` (closed sub-spans + the open one; idle
   gaps already excluded). Row start = `work_start` (fall back to `start`), end = `last_activity`
   (**never** tab-open → now). Skip if `start` is `null`.

3. **Write the entry — with real quality, not a hook's guess.** This is why a shell hook can't do
   this itself. Derive a **specific title**, the **correct `session_type`** (execution / review /
   planning / design / maintenance — see `/co`), and a **one-line real summary** of what was
   accomplished. Append the CSV row to `reports/timesheet.csv` with `source = auto-wrap` and
   `session_id` populated, and the matching `session` entry to `history.jsonl`.

4. **Update tracking** for anything that changed this burst: task `T0NN.md` frontmatter + matching
   `index.json` entries, `status.json` (respect the caps), and any `status_change` / `task_created`
   history entries. (Steps 2–3 of the standard flow.)

5. **Commit + push** exactly per Step 4 above (commit this repo's changes with a clear message;
   commit **and push** missioncontrol tracking; never push other repos).

6. **RESET the clock, don't delete it** — so continued work in the same session opens a *fresh*
   honest span rather than re-billing what was just wrapped. Write back the same file with:
   `start = null`, `work_start = null`, `last_activity = null`, `accrued_seconds = 0`,
   `first_turn_at = null`, `turn_count = 0`, `wrapped_at = <now ISO>`, and keep `opened_at` / `repo` /
   `cluster` / `cwd` / `transcript_path`. The next substantive tool or the 2nd turn re-starts the clock.
   (If you forget a field, the clock self-heals: the next clock-in resets `work_start`/`accrued_seconds`.)

7. **Confirm in one line**, e.g. `🔄 auto-wrapped: 42 min on portbase (execution) — "…"; committed + pushed.`
   Then continue with the user's new message.

Automatic mode is unattended: never block on a question. If something is ambiguous (e.g. cluster is
`unassigned`), make the safest choice, note it in the details, and continue.

## Rules

- **Only this conversation's clock is in scope.** Sibling sessions' clock files in `.active-clocks/` are owned by their conversations.
- **Fail loud on missing `$CLAUDE_SESSION_ID`.** Do not silently treat the absence as "no clock" — that was the silent-miss bug.
