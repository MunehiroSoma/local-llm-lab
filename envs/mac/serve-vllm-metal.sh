#!/usr/bin/env bash
set -euo pipefail

VLLM_METAL_VENV="${VLLM_METAL_VENV:-${HOME}/.venv-vllm-metal}"
VLLM_METAL_MODEL="${VLLM_METAL_MODEL:-Qwen/Qwen3-0.6B}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen3-0.6b}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8008}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-2048}"

if [ ! -x "${VLLM_METAL_VENV}/bin/vllm" ]; then
  echo "ERROR: vLLM Metal venv is missing: ${VLLM_METAL_VENV}" >&2
  echo "Run: bash envs/mac/setup-vllm-metal.sh" >&2
  exit 1
fi

export VLLM_METAL_USE_PAGED_ATTENTION="${VLLM_METAL_USE_PAGED_ATTENTION:-1}"
export VLLM_METAL_MEMORY_FRACTION="${VLLM_METAL_MEMORY_FRACTION:-0.5}"

exec "${VLLM_METAL_VENV}/bin/vllm" serve "${VLLM_METAL_MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --max-model-len "${MAX_MODEL_LEN}" \
  --served-model-name "${SERVED_MODEL_NAME}"
