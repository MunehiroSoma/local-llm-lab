#!/usr/bin/env bash
set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: envs/mac is for macOS only." >&2
  exit 1
fi

if [ "$(uname -m)" != "arm64" ]; then
  echo "ERROR: Apple Silicon arm64 is required. Rosetta shells are not supported." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is not installed." >&2
  exit 1
fi

MLX_VLM_VENV_VALUE="${MLX_VLM_VENV:-${HOME}/.venv-mlxvlm}"
MLX_VLM_PACKAGE_VALUE="${MLX_VLM_PACKAGE:-mlx-vlm}"

uv venv --python 3.12 "${MLX_VLM_VENV_VALUE}"
# shellcheck disable=SC1091
source "${MLX_VLM_VENV_VALUE}/bin/activate"
uv pip install "${MLX_VLM_PACKAGE_VALUE}"

python -c 'import platform; print("python:", platform.python_version(), platform.machine())'
python -c 'import mlx_vlm; print("mlx_vlm: import ok")'

echo "venv: ${MLX_VLM_VENV_VALUE}"
