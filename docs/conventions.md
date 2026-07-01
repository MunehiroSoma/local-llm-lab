# 規約・運用方針（conventions）

## ブランチ
| prefix | 用途 |
|---|---|
| `feat/*` | ハーネス等の機能 |
| `fix/*` | 修正 |
| `exp/*` | 計測ラン・実験 |
| `model/<id>` | モデル追加・検証 |
| `env/*` | 環境構築（runbook/compose） |
| `docs/*` | 資料 |
| `chore/*` | 雑務・設定 |

`main` は保護（直push禁止・PR必須・pre-commit通過）。マージは **squash**。

## コミット（Conventional Commits）
`<type>(scope): 概要`。type = feat/fix/docs/exp/model/chore/refactor/ci/build/test。

## 命名
- モデルID: kebab-case（`gemma4-26b-a4b`）。`registry/models.yaml` に宣言。
- 環境ID: `mac` / `rtx-5060ti` / `rtx-5070` / `dgx-spark`（`registry/hardware.yaml`）。

## 結果（results/results.csv）
- **追記のみ**（履歴を書き換えない）。列は固定スキーマ（research §12.10）。
- 生ログは `results/raw/`（gitignore）。図表は `results/reports/`。

## ADR
重要決定は `docs/adr/NNNN-*.md`（連番）。テンプレは `0000-template.md`。

## バージョン / タグ
- ハーネスは semver（`v0.1.0`）。
- 結果のスナップショットは `results-YYYYMMDD` タグで固定（再現・比較用）。

## 機密（公開リポジトリ）
- `datasets/golden/` の実データ（自前仕様書等）は**コミット禁止**。`samples/` のみ。
- 秘密情報は `.env`（gitignore）。詳細は [`SECURITY.md`](../SECURITY.md)。

## AI-DLC 運用（詳細は AGENT.md / ADR 0005）
- 3フェーズ: **Inception**(計画/Issue) → **Construction**(実装/PR) → **Operations**(運用/results)。**各遷移に人間承認ゲート**。
- **BOLT**: 短命ブランチ（数時間〜1日）。Unit of Work = (モデル×環境×評価) or harness機能。
- **ドキュメント先行**: 決定は ADR、根拠は `research/`、結果は `results/` に残す。
- **ハット(役割)**: ai-dev-kit スキル ＋ fit / speed / eval / review。

## ai-dev-kit スキルのプレースホルダ（本リポジトリの値）
| placeholder | 値 |
|---|---|
| `<owner>/<repo>` | `MunehiroSoma/local-llm-lab` |
| `<TEST_CMD>` | `pytest -q`（harness実装後） |
| `<LINT_CMD>` | `ruff check .` |
| `<FORMAT_CMD>` | `ruff format .` |
| `<PRECOMMIT_CMD>` | `pre-commit run --all-files` |
| `<MERGE_STYLE>` | `squash` |
