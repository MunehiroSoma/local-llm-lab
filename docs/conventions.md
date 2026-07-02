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

## 依存関係の再現性
- `uv.lock` はコミット対象。セットアップ・CIは `uv sync --frozen` を使う（`docs/adr` 参照なし、運用ルールとして固定）。
- eval実行ツール（promptfoo/whichllm等）は `@latest` を使わない。バージョンを明示指定する
  （judge・ゴールデンセット固定と同じ理由: ツールが変わると過去スコアと比較できなくなる）。
- GitHub Actions の `uses:` はタグではなくコミットSHAでピン留めする（サプライチェーン攻撃対策）。
- pre-commit フックの rev 更新は **手動での定期 `pre-commit autoupdate`** を採用する
  （pre-commit.ci は外部GitHub Appの導入が必要なため、単独ラボでは見送り）。
  目安: 月1回、または `.pre-commit-config.yaml` を触るPRのついでに実行し、
  `pre-commit run --all-files` が通ることを確認してからコミットする。

## 機密（公開リポジトリ）
- `datasets/golden/` の実データ（自前仕様書等）は**コミット禁止**。`samples/` のみ。
- 秘密情報は `.env`（gitignore）。詳細は [`SECURITY.md`](../SECURITY.md)。

## AI-DLC 運用（詳細は AGENT.md / ADR 0005）
- 3フェーズ: **Inception**(計画/Issue) → **Construction**(実装/PR) → **Operations**(運用/results)。**各遷移に人間承認ゲート**。
- **BOLT**: 短命ブランチ（数時間〜1日）。Unit of Work = (モデル×環境×評価) or harness機能。
- **ドキュメント先行**: 決定は ADR、根拠は `research/`、結果は `results/` に残す。
- **ハット(役割)**: ai-dev-kit スキル ＋ fit / speed / eval / review。

## ドキュメント体系

| 種別 | 場所 | 用途 |
|---|---|---|
| 要件定義書（本ラボ） | [`docs/specs/01_要件定義書.md`](specs/01_要件定義書.md) | local-llm-lab プロジェクトの要件定義（記入済み） |
| 設計書テンプレート | [`docs/templates/`](templates/) | 汎用テンプレート一式（01_要件定義書〜06_機能要件定義書） |
| ヒアリングシート | [`docs/templates/ヒアリングシート.md`](templates/ヒアリングシート.md) | 要件定義フェーズ用ヒアリング項目 131 問（C01〜C11） |
| コードレビューチェックリスト | [`docs/coding-standards/review-checklist.md`](coding-standards/review-checklist.md) | PR レビュー時の確認リスト（共通 + Python） |
| Python コーディング規約 | [`docs/coding-standards/python.md`](coding-standards/python.md) | v1.2 規約本文 + ruff マッピング表 |

## ai-dev-kit スキルのプレースホルダ（本リポジトリの値）
| placeholder | 値 |
|---|---|
| `<owner>/<repo>` | `MunehiroSoma/local-llm-lab` |
| `<TEST_CMD>` | `pytest -q`（harness実装後） |
| `<LINT_CMD>` | `ruff check .` |
| `<FORMAT_CMD>` | `ruff format .` |
| `<PRECOMMIT_CMD>` | `pre-commit run --all-files` |
| `<MERGE_STYLE>` | `squash` |
