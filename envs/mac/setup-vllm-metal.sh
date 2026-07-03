#!/usr/bin/env bash
set -euo pipefail

VLLM_METAL_VENV="${VLLM_METAL_VENV:-${HOME}/.venv-vllm-metal}"

if [ "$(uname -s)" != "Darwin" ] || [ "$(uname -m)" != "arm64" ]; then
  echo "ERROR: vLLM Metal requires macOS arm64." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required." >&2
  exit 1
fi

if [ -d "${VLLM_METAL_VENV}" ]; then
  echo "venv exists: ${VLLM_METAL_VENV}"
else
  curl -fsSL https://raw.githubusercontent.com/vllm-project/vllm-metal/main/install.sh | bash
fi

"${VLLM_METAL_VENV}/bin/python" -c 'import platform; print("python:", platform.python_version(), platform.machine())'
"${VLLM_METAL_VENV}/bin/python" - <<'PY'
import importlib.metadata as metadata

for package in ("vllm", "vllm-metal", "mlx", "mlx-lm"):
    print(f"{package}: {metadata.version(package)}")
PY
