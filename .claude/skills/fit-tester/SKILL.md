---
description: モデルの実ロード可否（Fit）を検証するラボ固有ハット
name: fit-tester
---
# skill: fit-tester

AGENT.md が定義するラボ固有の役割「fit-tester」。model-onboarding のレイヤ1 **Fit**
（実ロードで対象 max_model_len において OOM が発生しないか）を検証する。

## 使い方

```
/fit-tester <model-id> <環境>
例: /fit-tester gemma4-26b-a4b mac
```

## 前提

- `registry/models.yaml` に対象モデルが revision ピン留め済みで登録されていること
- `registry/hardware.yaml` に対象環境（mac/rtx-5060ti/rtx-5070/dgx-spark）が定義されていること
- 作業ブランチは `model/<id>` を使う（`new-feature` スキル参照）

## 手順

1. `registry/models.yaml` / `registry/hardware.yaml` から対象の設定を確認する
2. 対象環境の runbook（`docs/runbooks/`）に従って推論サーバを起動する
3. 目標 max_model_len でモデルを実ロードする
4. OOM の有無・実際にロードできた max_model_len・使用VRAM/メモリを記録する
5. 結果を model-onboarding Issue のチェックリストに反映する
   - `[ ] レイヤ1 Fit` にチェックし、結果メモへ実測値を追記する
6. Fit が通らない場合、量子化・max_model_len縮小等の代替案を人間に提示する
7. Fit確認後は `speed-bencher` に引き継ぐことを人間に提案する

## 記録項目（結果メモ）

- 実ロード可否（OK / OOM）
- 実際の max_model_len
- 使用VRAM/メモリ（GB）
- 量子化設定（該当する場合）

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill fit-tester` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
