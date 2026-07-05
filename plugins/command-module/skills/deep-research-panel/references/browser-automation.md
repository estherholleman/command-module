# Browser legs: driving free Gemini and ChatGPT accounts

Used only when no API key is set for that engine. This reproduces what a person
does by hand -- open the site already logged in, turn on Deep Research, paste the
prompt, wait, and copy the report -- using the `agent-browser` CLI. It is the
fragile path: heavy SPAs, shifting selectors, bot checks, and hard free-tier
limits. Prefer the API mechanism whenever possible.

Load the `agent-browser` skill for the full command reference. The rules below
are what make deep research specifically work.

## Golden rules

- **Reuse the real logged-in session; never script a fresh login.** A real
  profile with real cookies looks like a normal browser and avoids most bot
  detection. Import the running browser's auth, or use a persistent profile:
  ```bash
  agent-browser --auto-connect state save ./.dr-auth.json   # from the user's open, logged-in Chrome
  agent-browser --state ./.dr-auth.json open https://chatgpt.com
  ```
  Add any `*-auth.json` / `state.json` to `.gitignore` and delete it after the run.
- **Discover refs every run; do not hardcode CSS selectors.** Run
  `agent-browser snapshot -i` (add `-C` to include clickable non-form elements)
  and locate targets by their visible role/label in the snapshot. The UI changes
  often, so re-snapshot after every navigation or DOM change and adapt.
- **One engine per browser session** to keep state clean. Finish or submit one,
  then move to the next.

## Drive sequence (same shape for both sites)

Sites: ChatGPT at `https://chatgpt.com`, Gemini at `https://gemini.google.com/app`.

1. Open the site on the authenticated session and wait for the composer:
   `agent-browser open <url> && agent-browser wait --load networkidle && agent-browser snapshot -i`.
2. Enable Deep Research **before** sending. In the snapshot, find the tool/mode
   control near the composer -- a "Deep research" button, a tools/plus menu that
   contains it, or a mode toggle -- and click it so the composer shows deep
   research is active. Re-snapshot to confirm the active state.
3. Fill the composer with the exact shared prompt and submit:
   `agent-browser fill @<composer> "<prompt>" && agent-browser click @<send>`.
   Some builds first return a short clarifying/plan step -- if so, accept or
   confirm it (e.g. a "Start research" / "Go" button) to begin the actual run.
4. Confirm the run started (a progress/researching indicator appears). The remote
   job now runs on its own; harvesting is a separate step.

## Harvesting the finished report

Deep research takes 5-45 minutes. Poll, do not block:

- Re-open the conversation and `snapshot -i` on an interval (e.g. every 60-120s).
  The run is done when the progress indicator is gone and a full report with a
  copy/share/export affordance is present.
- Extract the report as text. Prefer a copy/export control if present; otherwise
  read the report container's text content:
  ```bash
  agent-browser text -s "<report-container-selector>"   # scope to the report region from the snapshot
  ```
  Save it to the engine's `.md` file. Clean up obvious UI chrome (e.g. a trailing
  "Copy"/"Sources" button label) but keep the body and citations intact.

## Rate limits and the assisted fallback

Free tiers allow only a few deep-research runs before showing an "upgrade" or
"limit reached" message, and may silently downgrade to a lighter model.

- If a limit/quota message appears at submit or harvest time, do **not** fail the
  whole skill. Switch that engine to the assisted fallback:
  1. Leave the site open with the prompt already filled (and Deep Research on).
  2. Ask the user, via the platform blocking-question tool (`AskUserQuestion` in
     Claude Code, `request_user_input` in Codex, `ask_user` in Gemini CLI; else a
     numbered prompt), to either run it on their account and paste the report back,
     or skip this engine.
  3. If they paste a report, save it verbatim to the engine's `.md` file. If they
     skip, write a one-line stub in that file noting the engine was unavailable and
     why (e.g. "Gemini free-tier deep-research limit reached").
- Record "browser (assisted)" as the mechanism for that engine in the index.

## When to give up on a leg

If two harvest attempts fail to find a completed report, or a bot check blocks
the session, stop retrying, write a stub explaining the failure, and continue.
A single broken browser leg must never sink the Claude and API legs.
