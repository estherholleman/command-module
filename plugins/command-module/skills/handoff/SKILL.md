---
name: handoff
description: 'Generate a self-contained starter prompt for a fresh conversation, write it to docs/prompts/, and display it in chat. Use at any workflow transition point (brainstorm to plan, plan to work, strategy to concept, etc.) when starting fresh in a new conversation will produce better results than continuing here. Triggers: "/handoff", "hand off", "hand off to a new conversation", "write me a starter prompt", "starter prompt", "fresh conversation", "set up a fresh conversation", "new conversation prompt".'
argument-hint: "[optional: topic next-action]"
---

# /handoff -- Generate a Starter Prompt for a Fresh Conversation

Generate a short, self-contained markdown prompt that a fresh conversation can use to pick up where this one ended. The prompt captures the next action, the files the new conversation must read, and any decisions or context it needs. Output is always both: a file in `docs/prompts/` and the same content displayed in chat.

**When NOT to use this skill:** if the question is "should I continue here or hand off at all?", load the `here-or-there` skill instead -- that skill assesses the conversation and routes into /handoff only when handing off is the right call. Invoking /handoff directly skips that assessment and assumes the user has already decided to hand off.

**What /handoff does not solve:** context bloat in the source conversation. A prompt generated inside a degraded conversation inherits that degradation. If generated prompts feel "off," that signals the source conversation degraded earlier -- not a /handoff bug.

## Phase 0 -- Ground

Read `$ARGUMENTS`. If present:
- First whitespace-separated token is the **topic**.
- Remaining tokens are the **next-action**.
- Skip Phase 1.5 confirmation (the caller has already chosen the names).

If `$ARGUMENTS` is absent, infer **topic** and **next-action** from the conversation transcript:
- **Topic** = the subject matter the new conversation will work on (e.g. `handoff-skill`, `auth-rewrite`).
- **Next-action** = the verb/skill the new conversation will run (e.g. `plan`, `build`, `review`, `concept`).

While reading the transcript, also collect the raw material the prompt will need:
- What was just decided or finished
- What the natural next step is
- File paths the next conversation must read (use only paths visible verbatim in the transcript -- no invented paths)
- Any non-goals or out-of-scope items the user explicitly named

**Ask-vs-infer threshold.** Ask the user to supply topic and next-action via the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini; chat fallback otherwise) when **any** of the following hold:
1. Fewer than 2 prior user turns in the conversation.
2. Zero file paths visible in the transcript that the inferred topic could anchor to.
3. The inferred topic and next-action together total fewer than 4 non-stopword tokens.

Otherwise infer without asking. The Phase 1.5 confirmation step is the safety net for borderline inferences.

## Phase 1 -- Generate

Assemble the prompt body using this template. Keep it short -- the goal is a brief that fits on one screen:

```markdown
# <Title naming the next action, e.g. "Plan: /handoff skill">

Run `/<next-skill>` with this context: (or "What to do" header for non-skill handoffs)

## What to <plan|build|review|...>

<1-3 lines describing the work>

## Origin / requirements doc

- <full path>  (only when one exists; use the verbatim path from the transcript)

## Key context

- <bullet with file path and one-line reasoning>
- <bullet with strategic context, decisions, or constraints>
- <additional bullets as needed -- keep tight>

## Out of scope (optional)

- <non-goals when scope could drift>
```

**Rules for the body:**
- File paths must be verbatim from the transcript. Do not invent paths or guess at file names.
- The "Run `/<skill>` with this context" line is for handoffs into a known skill; use a "What to do" header instead when the next conversation is freeform.
- Include "Origin / requirements doc" only when the transcript shows one. Omit the section otherwise.
- Include "Out of scope" only when scope could plausibly drift. Omit otherwise.
- Aim for 15-30 lines of prompt body. If the brief grows past that, the source conversation is leaking too much context -- the new conversation does not need everything, only what is load-bearing.

## Phase 1.5 -- Confirm

Skip this phase if `$ARGUMENTS` was provided.

Show the user a single-line preview via the platform's blocking question tool:

> Writing `docs/prompts/<topic>-<next-action>.md` for `/<next-skill>` -- proceed? [Y / n / edit / keep going here]

Resolution:
- **Y** -- proceed to Phase 2.
- **n** or **keep going here** -- abort cleanly. Reply: "no handoff written -- staying in this conversation." Do not write a file. Do not loop.
- **edit** -- accept a corrected topic and/or next-action from the user, re-render the preview, and re-confirm.

This single-keystroke confirmation closes the gap between "user invoked /handoff directly" and "user actually wanted to hand off" until /here-or-there ships as the upstream asker. Once /here-or-there is the routine caller, this confirmation is redundant -- callers pass `$ARGUMENTS` and the step is skipped automatically.

## Phase 2 -- Write and display

**Resolve target directory:**

Run a single bash command to find the repo root:

```bash
git rev-parse --show-toplevel
```

- On success: target directory is `<repo-root>/docs/prompts/`.
- On failure (not a git repo, or git unavailable): fall back to `docs/prompts/` relative to the current working directory and **explicitly state the fallback in the closing summary** so the user knows where the file landed.

**Create directory if missing.** Use the native file-write tool (e.g. Write in Claude Code) -- it will create parent directories as needed.

**Derive filename.** Format: `<topic>-<next-action>.md`, kebab-case. If the file already exists, append a numeric suffix: `<topic>-<next-action>-2.md`, `-3.md`, and so on, until a free name is found. Use the native file-search/glob tool (e.g. Glob in Claude Code) to detect existing collisions -- do not shell out for this.

**Write the file.** On write failure (permission denied, disk full, read-only filesystem), surface the error verbatim and the resolved target path so the user can act. Do not silently swallow.

**Display the result.** Print the resolved path and the full prompt content in chat using the closing template below.

## Closing

```
Prompt written to <resolved-path>.
[fallback notice only if cwd fallback was used:
"Note: not in a git repo, wrote to <cwd>/docs/prompts/ instead of repo root."]

---

[full prompt content, fenced or rendered]

---

Paste into a fresh conversation when ready.
```

## Calling from another skill

Other skills and agents can load this skill with optional arguments:
- `<topic> <next-action>` -- positional, whitespace-separated. First token is topic, rest is next-action.
- When arguments are provided, Phase 1.5 confirmation is skipped (the caller is responsible for the names).
- Everything else (decisions, files, context) is inferred by reading the conversation transcript -- callers do not pass content.

This is the integration shape for /here-or-there (T011) and the future handoff-phase replacements in /brainstorm, /implementation-plan, and /ideate.
