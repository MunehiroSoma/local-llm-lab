---
name: モデル・オンボーディング
about: 新しいモデルを候補に追加し、4階層評価を通す
title: "[model] <model-id> をオンボーディング"
labels: ["model-onboarding"]
---

## モデル
- id: <registry/models.yaml の id>
- hf_repo / revision:
- modality / params(活性):
- 対象 profile:
- 対象環境: [ ] mac [ ] rtx-5060ti [ ] rtx-5070 [ ] dgx-spark

## チェックリスト（research §13.5 / §12.4）
- [ ] `registry/models.yaml` に1行追加（revision をピン留め）
- [ ] 当たり付け: WhichLLM / LLM Checker
- [ ] レイヤ1 **Fit**: 実ロード（目標 max_model_len で OOM 無し）
- [ ] レイヤ2 **Speed**: 単発 tok/s・TTFT・(MM)前処理時間
- [ ] レイヤ3 **標準ベンチ**（足切り: 用途に応じ SWE-bench/Aider/MMMU/llm-jp-eval 等）
- [ ] レイヤ4 **自前タスク評価**（promptfoo/DeepEval・日本語含む）
- [ ] `results/results.csv` に1行追記
- [ ] 判定（採用 / 保留 / 不採用）と理由

## 結果メモ
（fit / tok_s / ttft / task_score / 所感）
