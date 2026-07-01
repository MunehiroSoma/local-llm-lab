---
description: 標準ベンチ・自前タスク評価を設計/実行するラボ固有ハット
name: eval-author
---
# skill: eval-author

AGENT.md が定義するラボ固有の役割「eval-author」。model-onboarding のレイヤ3 **標準ベンチ**
とレイヤ4 **自前タスク評価**を設計・実行する。

## 使い方

```
/eval-author <model-id> <評価対象>
例: /eval-author gemma4-26b-a4b swebench
例: /eval-author gemma4-26b-a4b promptfoo
```

## 前提

- レイヤ1-2（Fit / Speed）が完了していること
- judge モデル・ゴールデンセット版は固定済みであること（変更する場合は ADR に理由を残す）
- `datasets/golden/` に実データを置く場合はコミットしない（`.gitignore` 対象、`samples/` のみ公開可）

## 手順

1. 対象用途に応じた標準ベンチ（レイヤ3）を選ぶ
   - コーディング系: SWE-bench / Aider
   - マルチモーダル: MMMU
   - 日本語: llm-jp-eval
   - 足切り基準を用途ごとに明示し、通過/不通過を判定する
2. 自前タスク評価（レイヤ4）を `harness/task/promptfoo` または `harness/task/deepeval` の設定で実行する
   - 日本語タスクを含める
   - judge モデルとゴールデンセット版を固定して実行する
3. 結果を model-onboarding Issue のチェックリストに反映する
   - `[ ] レイヤ3 標準ベンチ` `[ ] レイヤ4 自前タスク評価` にチェックし、結果メモへスコアを追記する
4. 生ログを `results/raw/`、図表を `results/reports/` に保存する
5. 評価完了後は `record-results` に引き継ぎ、`results/results.csv` への追記と採用判定を進める

## 記録項目（結果メモ）

- 標準ベンチ名・スコア・足切り通過可否
- 自前タスク評価スコア（日本語含む）
- 使用した judge モデル・ゴールデンセット版

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill eval-author` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
