#!/usr/bin/env bash
# WhichLLM で候補モデルを機械抽出（当たり付け）。要 uv。
# 参考: https://github.com/Andyyyy64/whichllm （research §7）
set -u
PROFILE="${1:-coding}"
echo "== WhichLLM scan (profile=${PROFILE}) =="
uvx whichllm@latest hardware 2>/dev/null || echo "(hardware 検出に失敗)"
uvx whichllm@latest --profile "${PROFILE}" --min-speed 20 2>/dev/null \
  || echo "whichllm 未導入/失敗。'uvx whichllm@latest' を確認してください。"
echo
echo "注意: Apple Silicon は GGUF のみ / 推定速度＋公開ベンチであり自前タスク性能ではない。"
echo "確証は harness/task の自前タスク評価で（research §7, §12.9）。"
