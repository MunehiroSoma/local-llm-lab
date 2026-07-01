#!/usr/bin/env bash
# このマシンの環境確認（読み取り専用）。research §8.2 / §12.5。
set -u
echo "=== OS / arch ==="
uname -a

if [ "$(uname)" = "Darwin" ]; then
  echo "=== Mac (Apple Silicon) ==="
  system_profiler SPHardwareDataType 2>/dev/null | grep -Ei "Chip|Memory|Model Name|Total Number of Cores"
  python3 -c "import platform;print('python arch:',platform.machine())" 2>/dev/null
  if command -v ollama >/dev/null 2>&1; then ollama --version; ollama list 2>/dev/null | head; else echo "(no ollama)"; fi
else
  echo "=== NVIDIA / Linux(WSL2) ==="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,compute_cap,driver_version --format=csv
  else echo "(no nvidia-smi)"; fi
  python3 -c "import torch;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),torch.version.cuda)" 2>/dev/null || echo "(torch not importable)"
  [ -f /etc/os-release ] && head -2 /etc/os-release
fi

command -v uv >/dev/null 2>&1 && uv --version || echo "(no uv)"
