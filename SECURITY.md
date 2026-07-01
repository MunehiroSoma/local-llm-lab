# セキュリティ / データ取り扱い方針

本リポジトリは **Public**。以下を厳守する。

## 機密データ
- **自前ゴールデンセット（既存システムの仕様書・自分の文書など）は絶対にコミットしない。**
  - `datasets/golden/` は `.gitignore` で保護、`samples/` のみ公開。
  - 三重防御: `.gitignore` ＋ pre-commit(`guard-golden-data`) ＋ 最小CI guard。
- 秘密情報（APIキー等）は `.env`（gitignore）。`detect-private-key` フックで検知。

## セルフホスト・ランナーの注意（重要）
- **Public リポジトリでのセルフホスト・ランナーは危険**。fork からの PR が
  あなたのマシン上で**任意コードを実行**しうる。
- 使う場合は Settings → Actions で「外部コラボレータの承認必須」等で**必ず制限**し、
  信頼できる範囲（自分のPR・GPU評価ジョブ）に限定する。
- なお **Public リポジトリなら GitHub-hosted ランナーは無料・無制限**なので、
  基本チェックにセルフホストは不要（ADR 0004）。

## 報告
問題を見つけたら Issue（機密性が高い場合は非公開手段）で連絡。
