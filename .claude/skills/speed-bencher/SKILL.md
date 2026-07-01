---
description: モデルの速度（tok/s・TTFT等）を計測するラボ固有ハット
name: speed-bencher
---
# skill: speed-bencher

AGENT.md が定義するラボ固有の役割「speed-bencher」。model-onboarding のレイヤ2 **Speed**
（単発 tok/s・TTFT・(マルチモーダル時)前処理時間）を計測する。

## 使い方

```
/speed-bencher <model-id> <環境>
例: /speed-bencher gemma4-26b-a4b rtx-5070
```

## 前提

- レイヤ1 Fit（`fit-tester`）が完了し、実ロード可能な設定が確定していること
- 作業ブランチは `exp/*` または `model/<id>` を使う

## 手順

1. Fit確認済みの設定（max_model_len・量子化）でサーバを起動する
2. 単発推論で以下を計測する
   - tok/s（生成速度）
   - TTFT（Time To First Token）
   - マルチモーダル入力がある場合は前処理時間（画像/音声のエンコード時間）
3. 複数回計測し、ばらつき（min/max/median）を確認する
4. 結果を model-onboarding Issue のチェックリストに反映する
   - `[ ] レイヤ2 Speed` にチェックし、結果メモへ実測値を追記する
5. 生ログを `results/raw/` に保存する
6. 計測完了後は `eval-author` （標準ベンチ・自前タスク評価）に引き継ぐことを人間に提案する

## 記録項目（結果メモ）

- tok/s（median、min-max）
- TTFT（median、min-max）
- 前処理時間（該当する場合）
- 計測条件（プロンプト長・出力長・バッチサイズ）

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill speed-bencher` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
