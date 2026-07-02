# Runbook: ① Mac M4 Pro 48GB

役割: 画像+テキスト(+音声入力の一部)の常時手元機。フル omni は対象外。

## ランタイム
- **Ollama(MLX backend)**: 導入済み想定（`ollama --version` ≥ 0.19）。共通基準ライン。
- **MLX-VLM**: 実力ライン（arm64 Python 3.12 必須・Rosetta 不可）。

## セットアップ
```bash
# Ollama（共通基準）
ollama pull gemma4:e4b          # or qwen2.5-vl 系 / gemma4:26b 系
ollama serve                    # OpenAI互換: http://127.0.0.1:11434/v1

# MLX-VLM（実力ライン）
uv venv --python 3.12 ~/.venv-mlxvlm && source ~/.venv-mlxvlm/bin/activate
uv pip install mlx-vlm
python -m mlx_vlm.generate --model <mlx-community/...> --image <path> --prompt "..."
```

repo 内から再現する場合は [`envs/mac/`](../../envs/mac/) を使う。
`gemma4:e4b` は smoke test 用のローカル既存モデルであり、比較対象は
`envs/mac/README.md` と ADR 0008 のモデル方針に従って #4 配下の BOLT で onboarding する。

```bash
bash envs/mac/check.sh
OLLAMA_MODEL=gemma4:e4b bash envs/mac/serve-ollama.sh
MODEL=gemma4:e4b BASE_URL=http://127.0.0.1:11434/v1 bash envs/mac/smoke-ollama.sh
bash envs/mac/setup-mlx-vlm.sh
```

## PoC(Phase 0) 手順
1. Fit: 対象モデルがロードできるか（統合48GBの範囲）
2. Speed: 単発 tok/s・TTFT（画像込みの前処理時間も）
3. コーディング候補 Qwen3-Coder-30B-A3B(MoE) の単発速度（帯域273でMoEが効くか）

## 計測
- 電力: `sudo powermetrics --samplers gpu_power,cpu_power -i 1000`（SoC全体）
- 速度: MLXの内蔵計時 + OpenAI互換化して GenAI-Perf/`vllm bench` 併用可

## 注意
- vLLM本体(CUDA)は不可。omni(動画/音声出力)は不可に近い。
