---
name: deep-research-panel
description: Run one research question through Claude, Gemini, and ChatGPT deep research and save all three cited reports to a research/ folder in the current repo. Uses the Gemini and OpenAI Deep Research APIs when API keys are set, otherwise drives the free web accounts via browser automation. Use when the user wants the same question researched by multiple AI models, says 'run this through all three', 'gemini and chatgpt deep research too', 'triple deep research', 'multi-model research', or wants to compare deep-research reports across models.
---

# Deep Research Panel

Run a single research question through three deep-research engines and save three independent, cited reports side by side:

- **Local (Claude)** -- the native deep-research capability; no API key or external account required.
- **Gemini** -- the Gemini Deep Research API when `GEMINI_API_KEY` is set, otherwise the free Gemini web account via browser automation.
- **ChatGPT** -- the OpenAI Deep Research API when `OPENAI_API_KEY` is set, otherwise the free ChatGPT web account via browser automation.

All three reports land in `research/<date>-<slug>/` inside the repository the skill is invoked from, alongside the shared prompt and an index.

## Mechanism selection

Per engine, prefer the API and fall back to the browser:

| Engine | If API key present | Otherwise |
|--------|--------------------|-----------|
| ChatGPT | `OPENAI_API_KEY` -> `scripts/openai_deep_research.sh` | browser automation on chatgpt.com |
| Gemini | `GEMINI_API_KEY` or `GOOGLE_API_KEY` -> `scripts/gemini_deep_research.sh` | browser automation on gemini.google.com |

API legs are unlimited, robust, and cost roughly $1-4 per engine per run. Browser legs are free but rate-limited on free tiers and periodically fragile. Details: `references/api-legs.md` and `references/browser-automation.md`.

The API legs default to the **best** available deep-research models (`o3-deep-research` for OpenAI, `deep-research-max` for Gemini). The OpenAI script self-retries transient failures -- a per-minute rate-limit spike, or org verification still propagating right after verifying; a single job's token rate cannot be throttled from the client, so retry is the only remedy. Set `DR_OPENAI_MODEL` / `DR_GEMINI_AGENT` to override for a cheaper run.

## Steps

### 1. Refine the question and build one shared prompt

If the question is underspecified (missing scope, timeframe, region, or decision criteria), ask 2-3 clarifying questions before spending a research run. Use the platform blocking-question tool -- `AskUserQuestion` (Claude Code), `request_user_input` (Codex), `ask_user` (Gemini CLI). Where no such tool exists, present a numbered list of options and wait for a reply.

Compose one prompt that will be sent verbatim to all three engines so the reports are comparable. Keep it self-contained: each engine sees only this text, with no prior conversation.

### 2. Create the output directory

Resolve the repo root (`git rev-parse --show-toplevel`, falling back to the current directory) and the date (`date +%F`). Create `research/<date>-<slug>/`, where `<slug>` is a short kebab-case form of the question. Save the shared prompt to `prompt.md` in that folder.

### 3. Detect capability per engine

Check the environment once. `OPENAI_API_KEY` decides the ChatGPT mechanism; `GEMINI_API_KEY` or `GOOGLE_API_KEY` decides the Gemini mechanism. Record which mechanism each engine will use -- it goes in the index.

### 4. Start the two remote legs first

Remote deep research runs server-side for 5-45 minutes, so start Gemini and ChatGPT before doing local work, then reclaim that latency.

- **API mechanism:** run the engine's script in the background, writing its report straight to the target file:
  ```bash
  bash scripts/openai_deep_research.sh "$(cat research/<dir>/prompt.md)" > research/<dir>/chatgpt.md 2> research/<dir>/chatgpt.log &
  bash scripts/gemini_deep_research.sh "$(cat research/<dir>/prompt.md)" > research/<dir>/gemini.md 2> research/<dir>/gemini.log &
  ```
  Use the platform's background-execution facility (e.g. `run_in_background` in Claude Code) so the local leg proceeds meanwhile.
- **Browser mechanism:** follow `references/browser-automation.md` to open the site on the logged-in session, enable Deep Research, submit the prompt, and confirm the run started. Harvesting happens in step 6.

### 5. Run the local (Claude) leg

Run a full deep-research pass on the shared prompt using the platform's native capability:
- In Claude Code, invoke the `deep-research` skill with the shared prompt.
- On any platform without it, perform an equivalent pass -- fan out web searches, fetch and read primary sources, verify key claims, and synthesize a cited Markdown report.

Save the result to `claude-report.md`. (Do not use the bare name `claude.md`: on case-insensitive filesystems such as macOS it collides with `CLAUDE.md`, so the harness loads the report as project instructions.)

### 6. Harvest the remote legs

- **API mechanism:** wait for the background scripts to finish. A non-empty `*.md` containing prose is success. If a script exited non-zero (check the matching `*.log`), record the failure at the top of that engine's file and move on -- one engine failing must not sink the run.
- **Browser mechanism:** poll the page until the report is complete, then extract the report text/Markdown into the target file, per `references/browser-automation.md`. If the account shows a rate-limit or quota message, drop to the assisted fallback: leave the prompt loaded and ask the user (via the blocking-question tool) to run it and paste the report back, or write a short stub noting the engine was unavailable and why. Never fail the whole skill because one free-tier leg is capped.

### 7. Write the index

Create `research/<date>-<slug>/README.md` linking the three reports and `prompt.md`, and noting for each engine: mechanism used (API vs browser), model/agent, and completion status. Report all file paths back to the user.

## Notes

- Reports are durable outputs and belong in `research/`, not `.context/`. Raw API JSON and browser logs are transient; keep them beside the report (e.g. `*.log`) only while useful.
- API keys are read from the environment only. Never write a key into a report, the index, a committed file, or a shared transcript.
- Costs and exact request shapes: `references/api-legs.md`. Browser drive-and-harvest recipes and the assisted fallback: `references/browser-automation.md`.
