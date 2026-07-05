#!/usr/bin/env bash
# Run an OpenAI Deep Research query and print the final report (Markdown) to stdout.
# Progress and status go to stderr. Requires: OPENAI_API_KEY, curl, jq.
#
# Usage:
#   openai_deep_research.sh "your research prompt"
#   echo "prompt" | openai_deep_research.sh
#
# Env:
#   OPENAI_API_KEY    required
#   DR_OPENAI_MODEL   default: o4-mini-deep-research-2025-06-26 (cheaper; use
#                     o3-deep-research-2025-06-26 for higher-quality synthesis)
#   DR_POLL_INTERVAL  seconds between status checks (default 20)
#   DR_MAX_WAIT       max seconds to wait before giving up (default 3600)
#
# Exit codes: 0 ok, 1 API error, 2 empty prompt, 3 no key, 4 timeout.
set -euo pipefail

model="${DR_OPENAI_MODEL:-o4-mini-deep-research-2025-06-26}"
poll="${DR_POLL_INTERVAL:-20}"
max_wait="${DR_MAX_WAIT:-3600}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "openai_deep_research: OPENAI_API_KEY not set" >&2
  exit 3
fi

prompt="${1:-}"
if [[ -z "$prompt" ]]; then prompt="$(cat)"; fi
if [[ -z "$prompt" ]]; then
  echo "openai_deep_research: empty prompt" >&2
  exit 2
fi

# Deep research models require the web_search tool; run in background mode so a
# long job does not hit request timeouts, then poll the response by id.
req="$(jq -n --arg m "$model" --arg p "$prompt" '{
  model: $m,
  background: true,
  reasoning: { summary: "auto" },
  tools: [ { type: "web_search_preview" } ],
  input: [ { role: "user", content: [ { type: "input_text", text: $p } ] } ]
}')"

resp="$(curl -sS https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$req")"

id="$(printf '%s' "$resp" | jq -r '.id // empty')"
if [[ -z "$id" ]]; then
  echo "openai_deep_research: submit failed:" >&2
  printf '%s\n' "$resp" >&2
  exit 1
fi
echo "openai_deep_research: job $id submitted (model $model), polling..." >&2

waited=0
cur=""
while :; do
  cur="$(curl -sS "https://api.openai.com/v1/responses/$id" \
    -H "Authorization: Bearer $OPENAI_API_KEY")"
  status="$(printf '%s' "$cur" | jq -r '.status // "unknown"')"
  case "$status" in
    completed) break ;;
    failed|cancelled|incomplete)
      echo "openai_deep_research: job $status" >&2
      printf '%s' "$cur" | jq -r '.error // .incomplete_details // empty' >&2
      exit 1 ;;
    *)
      if (( waited >= max_wait )); then
        echo "openai_deep_research: timed out after ${max_wait}s (last status: $status)" >&2
        exit 4
      fi
      echo "  status=$status (${waited}s elapsed)" >&2
      sleep "$poll"
      waited=$(( waited + poll ))
      ;;
  esac
done

# Final report is the last message item's output_text.
out="$(printf '%s' "$cur" | jq -r '
  [ .output[]? | select(.type=="message") ] | last
  | ( .content[]? | select(.type=="output_text") | .text )
' 2>/dev/null || true)"

if [[ -z "$out" || "$out" == "null" ]]; then
  echo "openai_deep_research: could not locate report text; emitting raw response JSON" >&2
  printf '%s' "$cur" | jq '.'
else
  printf '%s\n' "$out"
fi
