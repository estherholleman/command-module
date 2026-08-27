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
#   DR_OPENAI_MODEL   default: o3-deep-research-2025-06-26 (best quality). Set to
#                     o4-mini-deep-research-2025-06-26 for a cheaper, faster run.
#   DR_POLL_INTERVAL  seconds between status checks (default 20)
#   DR_MAX_WAIT       max seconds to wait per attempt before giving up (default 3600)
#   DR_MAX_RETRIES    attempts when a run fails on a transient error: a per-minute
#                     rate-limit spike, or org verification still propagating (default 3)
#   DR_RETRY_WAIT     seconds to wait between retries (default 60)
#
# Notes:
#   - The best deep-research models (o3, o4-mini) require a VERIFIED OpenAI org.
#     Just after verifying, access can take ~15 min to propagate and may flip
#     between "ok" and "must be verified"; the retry loop rides that out.
#   - A single deep-research job can briefly burst over the org's tokens-per-minute
#     limit during synthesis. That happens server-side and cannot be throttled from
#     the client, so the only remedy here is to retry; the spike is usually transient.
#
# Exit codes: 0 ok, 1 API error, 2 empty prompt, 3 no key, 4 timeout.
set -uo pipefail

model="${DR_OPENAI_MODEL:-o3-deep-research-2025-06-26}"
poll="${DR_POLL_INTERVAL:-20}"
max_wait="${DR_MAX_WAIT:-3600}"
max_retries="${DR_MAX_RETRIES:-3}"
retry_wait="${DR_RETRY_WAIT:-60}"

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
# reasoning.summary is intentionally omitted: it is gated behind org verification
# and is not needed to retrieve the final report.
req="$(jq -n --arg m "$model" --arg p "$prompt" '{
  model: $m,
  background: true,
  tools: [ { type: "web_search_preview" } ],
  input: [ { role: "user", content: [ { type: "input_text", text: $p } ] } ]
}')"

# Rate-limit spikes and still-propagating org verification are treated as transient.
is_transient() { printf '%s' "$1" | grep -qE 'rate_limit_exceeded|must be verified|model_not_found'; }

cur=""
attempt=0
while :; do
  attempt=$(( attempt + 1 ))

  resp="$(curl -sS https://api.openai.com/v1/responses \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$req")"

  id="$(printf '%s' "$resp" | jq -r '.id // empty')"
  if [[ -z "$id" ]]; then
    if is_transient "$resp" && (( attempt < max_retries )); then
      echo "openai_deep_research: submit failed (transient), attempt $attempt/$max_retries; retrying in ${retry_wait}s..." >&2
      sleep "$retry_wait"; continue
    fi
    echo "openai_deep_research: submit failed:" >&2
    printf '%s\n' "$resp" >&2
    exit 1
  fi
  echo "openai_deep_research: job $id submitted (model $model, attempt $attempt), polling..." >&2

  waited=0
  jobstatus=""
  while :; do
    cur="$(curl -sS "https://api.openai.com/v1/responses/$id" \
      -H "Authorization: Bearer $OPENAI_API_KEY")"
    status="$(printf '%s' "$cur" | jq -r '.status // "unknown"')"
    case "$status" in
      completed) jobstatus="completed"; break ;;
      failed|cancelled|incomplete) jobstatus="$status"; break ;;
      *)
        if (( waited >= max_wait )); then jobstatus="timeout"; break; fi
        echo "  status=$status (${waited}s elapsed)" >&2
        sleep "$poll"
        waited=$(( waited + poll ))
        ;;
    esac
  done

  [[ "$jobstatus" == "completed" ]] && break

  errtext="$(printf '%s' "$cur" | jq -r '.error // .incomplete_details // empty' 2>/dev/null)"
  if [[ "$jobstatus" != "timeout" ]] && is_transient "$errtext" && (( attempt < max_retries )); then
    echo "openai_deep_research: job $jobstatus (transient), attempt $attempt/$max_retries: $errtext" >&2
    echo "  retrying in ${retry_wait}s..." >&2
    sleep "$retry_wait"; continue
  fi

  if [[ "$jobstatus" == "timeout" ]]; then
    echo "openai_deep_research: timed out after ${max_wait}s (last status polled)" >&2
    exit 4
  fi
  echo "openai_deep_research: job $jobstatus" >&2
  printf '%s\n' "$errtext" >&2
  exit 1
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
