# Runbook: ④ NVIDIA DGX Spark 128GB（GB10 / sm_121）

役割: 大型・フル omni の主軸ホスト。単発最速は狙わない（帯域273）。

## 重要な前提
- **sm_121 は新しく、上流stableイメージ非対応時期あり** → **CUDA 12.9+/CUDA13系・NGCコンテナ・nightly** を使用。
- ホストは ARM64（aarch64）。`uname -m` で確認。

## セットアップ（vLLM / vLLM-Omni）
```bash
uname -m                      # aarch64
nvidia-smi                    # GB10 / sm_121
# NGC もしくは CUDA13 nightly の vLLM(-Omni) コンテナを使用（要: 対応版の確認）
# 大型omni例（Qwen3-Omni）は vllm-omni の公式例に従う:
#   https://github.com/vllm-project/vllm-omni
```

## 推奨設定（コミュニティ論調）
- FP8 量子化 + KV cache FP8 + `gpu_memory_utilization` 0.85 + prefix caching
- NVFP4 の MoE がスイートスポット

## PoC 手順（omni-from-start の主戦場）
1. Fit: 大型 omni（Qwen3-Omni-30B-A3B 等）が 128GB にロードできるか
2. 疎通: 音声/動画入力 → 応答、必要なら音声出力（source/Docker build 要）
3. Speed: 単発 tok/s（活性3BのMoEが帯域273でどこまで出るか）

## 注意
- 音声"出力"は `pip` vLLM では未対応のことあり → source/Docker。
- 単発では②③に劣ることがある（帯域律速）。DGXの価値は"載る容量"。
