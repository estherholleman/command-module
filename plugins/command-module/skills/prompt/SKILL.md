---
name: prompt
description: "Draft a task-grounded starter prompt by combining missioncontrol task tracking with the target repo's own context, so the prompt carries both the task's origin/history and the repo's file layout, patterns, and available tooling. Writes the prompt to docs/prompts/ and displays it. Use when the user says '/prompt', 'draft a prompt for T042', 'write me a prompt for this task', 'prompt this task', 'turn this task into a prompt', or wants an execution-ready prompt for a tracked task."
argument-hint: "[task ID like T042, or a short task description] [optional: --draft]"
---

# /prompt -- Draft a Task-Grounded Prompt

Produce a self-contained starter prompt for a tracked task, grounded in **both** halves of the context that usually live apart:

- **Task context** from missioncontrol tracking -- the task's description, status, `origin`, related tasks, milestone, and the project's current picture. This is what a prompt written ad-hoc inside the target repo usually misses.
- **Repo context** from the working directory -- file layout, existing patterns, conventions, and the skills/agents available here. This is what a prompt written inside missioncontrol (where there is task context but no repo code) usually misses.

Neither place alone produces a strong first-pass prompt. This skill runs **in the target repo** and reads cross-repo into missioncontrol, so the prompt it writes carries both. Output is always a file in `docs/prompts/` plus the same content shown in chat.

**Relationship to `/handoff`:** `/handoff` writes a starter prompt from *this conversation's transcript* at a workflow transition -- it captures what was just decided here. `/prompt` writes an execution prompt from *tracking data* for a task that may never have been discussed in this conversation. Different inputs, different intent -- keep them separate. When the drafted prompt turns out to be research-shaped, point the reader at `/research` to dispatch it with the durable research preferences applied.

## Phase 0 -- Ground

1. **Resolve the repo.** Run `git rev-parse --show-toplevel` to find the repo root; the repo name is its basename (this is the `{repo}` key under missioncontrol tracking). On failure (not a git repo), use the current directory name and note it in the closing summary.

2. **Parse `$ARGUMENTS`.**
   - A token matching `T\d+` (e.g. `T042`) is a **task ID**.
   - `--draft` (anywhere in the arguments) turns on the interactive shaping pass in Phase 2. Default is one-shot.
   - Anything else is treated as a **freeform task description** -- there is no tracked task yet, so Phase 1 reads only repo context and the prompt is grounded in that plus the freeform framing. Offer to `/capture` the task afterward so it gets an ID and an `origin`.
   - If `$ARGUMENTS` is empty, read `missioncontrol/tracking/{repo}/tasks/index.json` and ask the user which task to draft for, using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini; chat fallback otherwise).

Tracking lives under `missioncontrol/tracking/{repo}/` (missioncontrol is in every repo's additionalDirectories). If that relative path is not resolvable from the current working directory, fall back to the absolute missioncontrol tracking root and note it.

## Phase 1 -- Gather context

### Task side (skip if freeform with no task ID)

1. Read `missioncontrol/tracking/{repo}/tasks/T0NN.md` for the task. Capture: the `task` line, `status`, `priority`, `deadline`, `tags`, and especially **`origin`** (the trigger/why the task exists) and the freeform notes body. Origin and notes are what make the prompt accurate rather than generic -- treat them as load-bearing.
2. Read `missioncontrol/tracking/{repo}/tasks/index.json` for related tasks: anything this task references, its milestone, and sibling tasks in the same milestone or tag cluster. Pull only what is relevant -- do not dump the backlog.
3. Read `missioncontrol/tracking/{repo}/status.json` for the project's current picture: highlights, the `linchpin` block, and any `upcoming` deadline flags. If the task is peripheral work while the project's linchpin is still `unproven`, say so in the prompt as a caution rather than silently framing the peripheral work as the main event.

If `origin` is missing or generic on the target task, ask the user for the real trigger before drafting (same bar as `/capture`) -- do not paper over it. A prompt built on a vague origin inherits the vagueness.

### Repo side

4. Read the repo's `CLAUDE.md` / `AGENTS.md` for conventions the prompt must respect.
5. Scan `docs/prompts/` for existing prompt files and match their format and tone.
6. Note the skills and agents available in this repo (and this plugin) that the task's work would plausibly use -- name them in the prompt so the execution conversation reaches for the right tool instead of reinventing it.
7. Look at the actual code/files the task touches (layout, the modules or patterns it will extend) enough to name real paths in the prompt. Use only paths you have verified -- never invent a path.

## Phase 2 -- Shape (optional, `--draft` only)

Skip this phase unless `--draft` was passed. When on, run one short interactive pass before composing:

- **Prompt type** -- is this a *research*, *build*, *exploration*, or *review* prompt? The type is not a rigid taxonomy; it sets which defaults apply (research prompts get the research-preferences block below; build prompts get repo-pattern grounding and a verification expectation; review prompts get the review scope). If the type is obvious from the task, state your inference and let the user correct it rather than asking cold.
- **Any non-default preferences for this one** -- constraints, must-read files, or scope the user wants baked in that the tracking data would not reveal.

One-shot mode (the default) infers the type from the task's tags and description and proceeds without asking. `--draft` exists for tasks where a lazy inferred framing would be costly.

## Phase 3 -- Compose

Assemble a self-contained prompt. Structure adapts to the prompt type, but every prompt carries:

```markdown
# <Title naming the task and the action, e.g. "Build: /prompt skill (T022)">

> Task: {repo}/T0NN -- <one-line task summary>   (omit the ID line for freeform prompts)

## What to do

<2-5 lines. What the execution conversation should accomplish, grounded in the task and its origin.>

## Why this task exists

<The task's origin, restated so a fresh conversation understands the trigger without reading tracking.>

## Key context

- <Verified repo path + one line on why it matters>
- <Related task / milestone / linchpin note, only when load-bearing>
- <Convention from CLAUDE.md the work must respect>
- <Available skill or agent this work should use, named explicitly>

## Out of scope (optional)

- <Non-goals, when scope could drift>
```

**Defaults to bake in:**
- **Task-ID reference at the top** for traceability (except freeform prompts, which have no ID yet).
- **Origin baked in** as the "Why this task exists" section -- never drop it.
- **For research-shaped prompts, apply the durable research preferences** (comprehensive, no length/time caps, don't pre-impose structures, "find all" over "top N", build-up-over-time as valid scope). These are the same preferences the `/research` skill owns -- for a research prompt, prefer pointing the reader at `/research T0NN` to dispatch it rather than re-stating the whole preference block inline, and keep the prompt itself focused on the actual research questions.
- **Citation requirements** wherever the prompt asks for external facts or sources.

**Rules for the body:**
- File paths are verbatim and verified. Do not invent or guess names.
- Keep it self-contained and tight -- a fresh conversation should be able to start from this alone. If the brief runs long, cut context that is not load-bearing rather than inlining tracking wholesale.
- Do not restate the entire task file; distil it. The prompt is an execution brief, not an archive.

## Phase 4 -- Write and display

1. **Resolve the target directory** to `<repo-root>/docs/prompts/` (fall back to `docs/prompts/` under the current directory if not in a git repo, and state the fallback). Create it if missing using the native file-write tool.
2. **Derive the filename** `prompt-<slug>.md`, kebab-case from the task title or freeform topic. On collision, append `-2`, `-3`, ... using the native glob tool -- do not overwrite an existing prompt.
3. **Write the file.** On write failure, surface the error and the resolved path verbatim; do not swallow it.
4. **Display** the resolved path and the full prompt content in chat.

## Closing

```
Prompt written to <resolved-path>.
[fallback notice only if a cwd fallback was used]

---

[full prompt content]

---

Paste into a fresh conversation when ready.
[for research-shaped prompts:] Or run `/research T0NN` to dispatch it with the research preferences applied.
[for freeform prompts:] This task has no tracked ID yet -- run `/capture` if you want one.
```

## Guardrails

- **Never fabricate task context.** Only use what the tracking files and repo actually contain. If origin is missing, ask -- do not invent a trigger.
- **Never invent file paths.** Every path in the prompt must be one you have verified in the repo.
- **Do not dump the backlog or the whole task file.** Distil to what is load-bearing for this one prompt.
- **One-shot by default; interactive only on `--draft`.** Do not add friction the user did not ask for, but do not let a lazy inferred framing ship unexamined on a task where it matters -- that is what `--draft` is for.
- **Flag pedestal-building.** If the task is peripheral work while the project's linchpin is `unproven`, name that in the prompt rather than framing the peripheral work as the main event.
