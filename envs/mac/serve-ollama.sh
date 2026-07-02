#!/usr/bin/env bash
set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: envs/mac is for macOS only." >&2
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: ollama is not installed." >&2
  exit 1
fi

OLLAMA_HOST_VALUE="${OLLAMA_HOST:-127.0.0.1:11434}"
OLLAMA_MODEL_VALUE="${OLLAMA_MODEL:-gemma4:e4b}"
OLLAMA_LOG_VALUE="${OLLAMA_LOG:-/tmp/local-llm-lab-ollama.log}"
OLLAMA_API_URL="http://${OLLAMA_HOST_VALUE}/api/version"

if curl --fail --silent --max-time 2 "${OLLAMA_API_URL}" >/dev/null 2>&1; then
  echo "ollama: already reachable at ${OLLAMA_API_URL}"
else
  echo "ollama: starting server on ${OLLAMA_HOST_VALUE}"
  OLLAMA_HOST="${OLLAMA_HOST_VALUE}" nohup ollama serve >"${OLLAMA_LOG_VALUE}" 2>&1 &
  echo "ollama_pid: $!"
  echo "ollama_log: ${OLLAMA_LOG_VALUE}"

  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if curl --fail --silent --max-time 2 "${OLLAMA_API_URL}" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

curl --fail --silent --show-error --max-time 5 "${OLLAMA_API_URL}" >/dev/null
echo "ollama_api: ok"

echo "ollama: pulling ${OLLAMA_MODEL_VALUE}"
OLLAMA_HOST="${OLLAMA_HOST_VALUE}" ollama pull "${OLLAMA_MODEL_VALUE}"

echo "openai_base_url: http://${OLLAMA_HOST_VALUE}/v1"
echo "model: ${OLLAMA_MODEL_VALUE}"
