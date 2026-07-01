## 目的
<!-- 何を・なぜ -->

## 種別
- [ ] feat (harness/機能)  - [ ] exp (計測ラン)  - [ ] model (モデル追加)
- [ ] docs  - [ ] env (環境構築)  - [ ] fix

## チェック
- [ ] `main` は壊さない（設計・確定結果のみ）
- [ ] registry を変えた場合: `make validate` が通る
- [ ] 結果を追加した場合: `results/results.csv` のスキーマ準拠
- [ ] **自前ゴールデンセットの実データをコミットしていない**（`datasets/golden/` は samples のみ）
- [ ] 関連 ADR / research を更新（必要な場合）

## 関連 Issue
