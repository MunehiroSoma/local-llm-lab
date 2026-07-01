# ADR 0004: 一次ゲートは pre-commit（CIは最小・任意）

- ステータス: accepted
- 日付: 2026-07-01

## 背景 / 課題
CI の従量課金を避けたい。一方で公開リポジトリでは機密データ混入を確実に防ぐ必要がある。

## 事実確認（重要）
- **Public リポジトリなら GitHub-hosted ランナーは無料・無制限**。従量課金は主に
  Private の無料枠超過・大型/GPUランナー。→ 基本CIは実質無料。
- **セルフホスト・ランナーは GitHub 利用料なし**（＝自分のマシンの電気代・保守は要）。
  ただし **Public リポでは fork PR の任意コード実行リスク**があり、原則非推奨/要制限。

## 決定
1. **ローカルの `pre-commit` を一次ゲート**にする（lint/format/yaml/機密ガード）。
2. CI は **最小の privacy guard のみ**（`guard-golden-data`）を GitHub-hosted(無料)で残す。
   pre-commit は `--no-verify` で回避可能なため、公開リポの機密防御はサーバ側にも一枚置く。
3. **セルフホストは GPU 評価ジョブ等の必要時のみ**。その際は fork PR 実行を禁止する設定を必須とする。
4. 不要なら CI ワークフローは削除してよい（pre-commit + ブランチ保護で代替）。

## 影響
`.pre-commit-config.yaml`, `.github/workflows/validate.yml`(最小化), `SECURITY.md`。
