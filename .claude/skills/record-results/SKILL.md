---
description: Operations フェーズの結果を results/results.csv に記録し、受け入れ承認ゲートを通す
name: record-results
---
# skill: record-results

AI-DLC の **Operations** フェーズ（運用・継続検証）に対応するスキル。
Construction で得られた計測結果を `results/results.csv` に追記し、回帰確認と
「結果受け入れ承認 → モデル採用」の人間承認ゲートを通す。

## 使い方

```
/record-results <対象 model-id or harness機能>
例: /record-results gemma4-26b-a4b
```

## 前提

- Construction フェーズ（PR merge）が完了していること
- `results/results.csv` は**追記のみ**（既存行の書き換え・削除は禁止）
- judge モデル・ゴールデンセット版は固定済みであること（変更が必要な場合は先に ADR に記録する）

## 手順

1. 対象の計測結果（fit / tok_s / ttft / task_score 等）を確認する
   - model-onboarding の場合は Issue チェックリスト（レイヤ1〜4）が全て埋まっているか確認する
2. `results/results.csv` の固定スキーマ（research §12.10）に沿って1行を組み立てる
3. 既存行と比較し、回帰（大幅な性能劣化・スコア低下）がないか確認する
   - 回帰がある場合は原因を人間へ報告し、追記前に判断を仰ぐ
4. 追記予定の行を人間へ提示する
   ```
   追記予定行: <CSV行>
   比較対象: <直近の同条件行、あれば>
   回帰の有無: <あり/なし、ありの場合は詳細>
   ```
5. **人間承認ゲート（必須）**: 「採用 / 保留 / 不採用」の判定を人間に確認する
   - 承認が出るまで `results/results.csv` に書き込まない
6. 承認後、`results/results.csv` に追記する
   ```bash
   echo "<CSV行>" >> results/results.csv
   ```
7. 生ログを `results/raw/`、図表を `results/reports/` に保存する（該当する場合）
8. model-onboarding Issue がある場合、判定結果と理由をコメントで残しクローズする
9. 大きな結果スナップショットが必要な場合は `results-YYYYMMDD` タグを打つことを人間に提案する

## 回帰検知の目安

| 指標 | 回帰とみなす目安 |
|---|---|
| task_score | 直近の同条件比で明確な低下 |
| tok/s | 同一環境・同一量子化での大幅な低下 |
| fit (OOM有無) | 同一 max_model_len で新たに OOM |

明確な閾値が定義されていない場合は、判断根拠を人間に提示して都度確認する。

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill record-results` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
