#!/usr/bin/env bash
# WhichLLM で候補モデルを機械抽出（当たり付け）。要 uv。
# 参考: https://github.com/Andyyyy64/whichllm （research §7）
set -u
PROFILE="${1:-coding}"
echo "== WhichLLM scan (profile=${PROFILE}) =="
WHICHLLM_VERSION="0.5.14"  # バージョン固定（過去スコアとの比較を壊さないため。CI/CDレビュー資料 C-2）
# stderrは意図的に残す（バージョン解決失敗と未導入を区別できるようにするため）
uvx "whichllm==${WHICHLLM_VERSION}" hardware || echo "(hardware 検出に失敗。上記エラーを確認してください)"
uvx "whichllm==${WHICHLLM_VERSION}" --profile "${PROFILE}" --min-speed 20 \
  || echo "whichllm 未導入/失敗。'uvx whichllm==${WHICHLLM_VERSION}' が解決できるか確認してください。"
echo
echo "注意: Apple Silicon は GGUF のみ / 推定速度＋公開ベンチであり自前タスク性能ではない。"
echo "確証は harness/task の自前タスク評価で（research §7, §12.9）。"
