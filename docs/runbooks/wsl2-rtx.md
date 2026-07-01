# Runbook: ② RTX 5060 Ti 16GB / ③ RTX 5070 12GB（Windows + WSL2）

役割: ② 載せやすいNVIDIA機（ローカルomni副ホスト） / ③ VLM・コーディングの単発最速機。

## 前提（GPUパススルー）
```bash
# Windows側: 新しめの NVIDIA ドライバ（WSL対応）
wsl --version
# WSL内
nvidia-smi --query-gpu=name,memory.total,compute_cap,driver_version --format=csv
# Docker経路の場合: nvidia-container-toolkit 必須
docker run --rm --gpus all nvidia/cuda:13.0-base nvidia-smi
```

## ランタイム
- **vLLM / vLLM-Omni**（FP8がBlackwell本命）。**②③とも WSL2 で揃える**（オーバーヘッド条件を統一）。
- Ollama を共通基準ラインに。

## セットアップ（vLLM 例）
```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install vllm --torch-backend auto     # sm_120対応版・CUDA/torchは要確認
vllm serve Qwen/Qwen2.5-VL-7B-Instruct --quantization fp8 --dtype bfloat16 \
  --max-model-len 8192 --gpu-memory-utilization 0.90 --limit-mm-per-prompt image=2 \
  --seed 0 --served-model-name bench-model --host 127.0.0.1 --port 8000 --trust-remote-code
```

## PoC 手順
1. Fit: 目標モデル×量子化が OOM しないか（②16GB / ③12GB の境界を確定）
2. Speed: 単発 tok/s・TTFT（③は帯域672で最速のはず）
3. ② で omni（MiniCPM-o 4.5 / Qwen2.5-Omni-7B）が載るか。③はVLM主体。

## 計測
- `nvidia-smi --query-gpu=timestamp,power.draw,utilization.gpu,memory.used,temperature.gpu --format=csv -l 1`
- `vllm bench serve ... --max-concurrency 1`（単発主）
