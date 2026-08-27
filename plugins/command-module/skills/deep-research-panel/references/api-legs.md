# API legs: models, cost, request shapes

The API mechanism is preferred whenever a key is present. Both scripts submit a
background job, poll until it completes, and print the final Markdown report to
stdout (redirect it to the engine's `.md` file). Both need `curl` and `jq`.

## ChatGPT -- OpenAI Deep Research API

- Endpoint: `POST https://api.openai.com/v1/responses` (the Responses API).
- Auth: `Authorization: Bearer $OPENAI_API_KEY`.
- Models: `o3-deep-research-2025-06-26` (default; best-quality synthesis) or
  `o4-mini-deep-research-2025-06-26` (cheaper, faster). Override with
  `DR_OPENAI_MODEL`. Both require a VERIFIED OpenAI org.
- The `web_search_preview` tool is mandatory for deep-research models; the script
  includes it. `code_interpreter` is optional and omitted by default.
- Async: submit with `background: true`, then `GET /v1/responses/{id}` until
  `status == "completed"`. Report text is the last `message` item's `output_text`.
- Cost: roughly $0.40-$2.50 per run on `o4-mini`, $1.50-$8 (occasionally more) on
  `o3`. Web search is always on and folded in. The Batch API halves cost for
  non-time-sensitive runs but is not used here.

## Gemini -- Deep Research Agent API

- Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/interactions`.
- Auth header: `x-goog-api-key: $GEMINI_API_KEY` (or `GOOGLE_API_KEY`).
- Agent id: `deep-research-max-preview-04-2026` (default; maximum
  comprehensiveness) or `deep-research-preview-04-2026` (lighter, cheaper).
  Override with `DR_GEMINI_AGENT`.
- Async: submit with `background: true`, then `GET /v1beta/interactions/{id}`
  until `status == "completed"`. Report text is the last step's text content.
- Cost: no flat per-run price. Billed as underlying Gemini model inference plus
  Google Search grounding queries (roughly $1-4 per run, variable). A free
  grounding allotment exists (e.g. thousands of grounded prompts/month on current
  models), so light usage can be cheap.

## Shared tuning knobs

- `DR_POLL_INTERVAL` (default 20s) -- seconds between status checks.
- `DR_MAX_WAIT` (default 3600s) -- give up after this long. Deep research usually
  finishes in 5-45 minutes; raise this for very large queries.
- `DR_MAX_RETRIES` (OpenAI script, default 3) -- re-attempts on a transient
  failure: a per-minute rate-limit spike, or org verification still propagating
  just after verifying.
- `DR_RETRY_WAIT` (OpenAI script, default 60s) -- wait between those retries.

## Getting keys (no credit card surprises)

- OpenAI: create a key at the OpenAI platform, then set a hard monthly spend limit
  under billing limits so a runaway query cannot overspend.
- Gemini: create a key in Google AI Studio; usage is billed to the linked Google
  Cloud project, so set a budget alert there.

## Troubleshooting

- Exit code 3 means the key is unset -- the skill should fall back to the browser
  mechanism for that engine.
- Exit code 1 with the raw JSON echoed usually means an auth, quota, or
  model-name error; read the `error` field in the `.log` file.
- `rate_limit_exceeded` means one job briefly exceeded the org's tokens-per-minute
  ceiling during synthesis. It cannot be throttled client-side, so the OpenAI
  script auto-retries (`DR_MAX_RETRIES`). Persistent limits need a higher OpenAI
  tier (platform.openai.com/account/limits).
- `model_not_found` / "organization must be verified" means the deep-research
  model needs a verified OpenAI org; right after verifying, access can take ~15 min
  to propagate. The OpenAI script auto-retries this too.
- If a report file contains raw JSON instead of prose, the response schema shifted;
  the report text field moved. Inspect the JSON, update the extraction `jq` filter
  at the end of the relevant script, and re-run.
