#!/usr/bin/env bash
set -euo pipefail

echo "=== mac runtime check ==="

if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: envs/mac is for macOS only." >&2
  exit 1
fi

echo "os: $(sw_vers -productName) $(sw_vers -productVersion)"
echo "kernel: $(uname -r)"
echo "arch: $(uname -m)"

if [ "$(uname -m)" != "arm64" ]; then
  echo "ERROR: Apple Silicon arm64 is required. Rosetta shells are not supported." >&2
  exit 1
fi

echo
echo "=== hardware ==="
system_profiler SPHardwareDataType 2>/dev/null | grep -Ei "Model Name|Chip|Memory|Total Number of Cores" || true

echo
echo "=== tools ==="
if command -v uv >/dev/null 2>&1; then
  uv --version
else
  echo "MISSING: uv"
fi

if command -v ollama >/dev/null 2>&1; then
  ollama --version
else
  echo "MISSING: ollama"
fi

echo
echo "=== ollama api ==="
OLLAMA_HOST_VALUE="${OLLAMA_HOST:-127.0.0.1:11434}"
OLLAMA_API_URL="http://${OLLAMA_HOST_VALUE}/api/version"
if command -v curl >/dev/null 2>&1 && curl --fail --silent --show-error --max-time 2 "${OLLAMA_API_URL}"; then
  echo
  echo "ollama_api: ok (${OLLAMA_API_URL})"
else
  echo "ollama_api: not reachable (${OLLAMA_API_URL})"
fi

echo
echo "=== mlx-vlm venv ==="
MLX_VLM_VENV="${MLX_VLM_VENV:-${HOME}/.venv-mlxvlm}"
if [ -x "${MLX_VLM_VENV}/bin/python" ]; then
  "${MLX_VLM_VENV}/bin/python" -c 'import platform; print("python:", platform.python_version(), platform.machine())'
  if "${MLX_VLM_VENV}/bin/python" -c 'import mlx_vlm' >/dev/null 2>&1; then
    echo "mlx_vlm: import ok"
  else
    echo "mlx_vlm: not importable"
  fi
else
  echo "venv: missing (${MLX_VLM_VENV})"
fi
