# 観点: harness / eval / registry（本リポジトリ固有）

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**。ただし `registry/models.yaml` 変更時は関連 ADR も参照する。
> 想定モデル: 上位モデル（harness/eval ロジックの整合性判断が必要なため）。

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | `status: onboarded` のモデルで `revision` がピン留めされているか | 自動 | Must | pre-commit check-jsonschema（`registry/schema/models.schema.json`） |
| 2 | `results/results.csv` への追記が既存行を書き換えていないか（追記のみ） | 自動 | Must | pre-commit/CI `guard_results_append_only.sh`（鉄則4） |
| 3 | eval設定（promptfoo/DeepEval等）のゴールデンセット版が固定されているか | 手動 | Must | |
| 4 | `datasets/golden/` に実データ（samples以外）を含めていないか | 自動 | Must | pre-commit/CI `guard_golden.sh` |
| 5 | 重要な決定が ADR (`docs/adr/`) に残っているか | 手動 | Should | |
