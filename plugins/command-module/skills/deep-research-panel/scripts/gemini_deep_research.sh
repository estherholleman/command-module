#!/usr/bin/env bash
# Run a Gemini Deep Research query and print the final report (Markdown) to stdout.
# Progress and status go to stderr. Requires: GEMINI_API_KEY (or GOOGLE_API_KEY), curl, jq.
#
# Usage:
#   gemini_deep_research.sh "your research prompt"
#   echo "prompt" | gemini_deep_research.sh
#
# Env:
#   GEMINI_API_KEY / GOOGLE_API_KEY  required (GEMINI_API_KEY wins)
#   DR_GEMINI_AGENT   default: deep-research-max-preview-04-2026 (maximum
#                     comprehensiveness). Set to deep-research-preview-04-2026 for
#                     a lighter, cheaper run.
#   DR_POLL_INTERVAL  seconds between status checks (default 20)
#   DR_MAX_WAIT       max seconds to wait before giving up (default 3600)
#
# Exit codes: 0 ok, 1 API error, 2 empty prompt, 3 no key, 4 timeout.
set -euo pipefail

key="${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}"
agent="${DR_GEMINI_AGENT:-deep-research-max-preview-04-2026}"
poll="${DR_POLL_INTERVAL:-20}"
max_wait="${DR_MAX_WAIT:-3600}"
base="https://generativelanguage.googleapis.com/v1beta/interactions"

if [[ -z "$key" ]]; then
  echo "gemini_deep_research: GEMINI_API_KEY (or GOOGLE_API_KEY) not set" >&2
  exit 3
fi

prompt="${1:-}"
if [[ -z "$prompt" ]]; then prompt="$(cat)"; fi
if [[ -z "$prompt" ]]; then
  echo "gemini_deep_research: empty prompt" >&2
  exit 2
fi

# Submit as a background interaction, then poll the interaction by id.
req="$(jq -n --arg a "$agent" --arg p "$prompt" '{
  agent: $a,
  input: $p,
  background: true,
  stream: false,
  agent_config: { type: "deep-research", thinking_summaries: "auto" },
  tools: [ { type: "google_search" }, { type: "url_context" } ]
}')"

resp="$(curl -sS "$base" \
  -H "x-goog-api-key: $key" \
  -H "Content-Type: application/json" \
  -d "$req")"

id="$(printf '%s' "$resp" | jq -r '.id // .name // empty')"
if [[ -z "$id" ]]; then
  echo "gemini_deep_research: submit failed:" >&2
  printf '%s\n' "$resp" >&2
  exit 1
fi
echo "gemini_deep_research: interaction $id submitted (agent $agent), polling..." >&2

waited=0
cur=""
while :; do
  cur="$(curl -sS "$base/$id" -H "x-goog-api-key: $key")"
  status="$(printf '%s' "$cur" | jq -r '.status // "unknown"')"
  case "$status" in
    completed) break ;;
    failed|cancelled)
      echo "gemini_deep_research: interaction $status" >&2
      printf '%s' "$cur" | jq -r '.error // empty' >&2
      exit 1 ;;
    *)
      if (( waited >= max_wait )); then
        echo "gemini_deep_research: timed out after ${max_wait}s (last status: $status)" >&2
        exit 4
      fi
      echo "  status=$status (${waited}s elapsed)" >&2
      sleep "$poll"
      waited=$(( waited + poll ))
      ;;
  esac
done

# Final report is the last step's text content.
out="$(printf '%s' "$cur" | jq -r '
  [ .steps[-1].content[]? | select(.text != null) | .text ] | join("\n\n")
' 2>/dev/null || true)"

if [[ -z "$out" || "$out" == "null" ]]; then
  echo "gemini_deep_research: could not locate report text; emitting raw interaction JSON" >&2
  printf '%s' "$cur" | jq '.'
else
  printf '%s\n' "$out"
fi
