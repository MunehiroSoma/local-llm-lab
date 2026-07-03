#!/usr/bin/env bash
set -euo pipefail

LLAMA_CPP_REF="${LLAMA_CPP_REF:-b9850}"
LLAMA_CPP_DIR="${LLAMA_CPP_DIR:-${HOME}/.local/src/llama.cpp}"
LLAMA_CPP_BUILD_DIR="${LLAMA_CPP_BUILD_DIR:-${LLAMA_CPP_DIR}/build}"

if [ "$(uname -s)" != "Darwin" ] || [ "$(uname -m)" != "arm64" ]; then
  echo "ERROR: llama.cpp Metal setup requires macOS arm64." >&2
  exit 1
fi

if ! command -v cmake >/dev/null 2>&1; then
  echo "ERROR: cmake is required. Install it with: brew install cmake" >&2
  exit 1
fi

mkdir -p "$(dirname "${LLAMA_CPP_DIR}")"
if [ ! -d "${LLAMA_CPP_DIR}/.git" ]; then
  git clone --depth 1 --branch "${LLAMA_CPP_REF}" https://github.com/ggml-org/llama.cpp.git "${LLAMA_CPP_DIR}"
else
  git -C "${LLAMA_CPP_DIR}" fetch --depth 1 origin "tag ${LLAMA_CPP_REF}" || true
  git -C "${LLAMA_CPP_DIR}" checkout "${LLAMA_CPP_REF}"
fi

cmake -S "${LLAMA_CPP_DIR}" -B "${LLAMA_CPP_BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON
cmake --build "${LLAMA_CPP_BUILD_DIR}" --config Release -j "${LLAMA_CPP_JOBS:-10}"

"${LLAMA_CPP_BUILD_DIR}/bin/llama-cli" --version
"${LLAMA_CPP_BUILD_DIR}/bin/llama-bench" --list-devices
