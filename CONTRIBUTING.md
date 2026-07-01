# Contributing / 運用ガイド

本リポジトリは **GitHub Flow**（`main` 常時グリーン → ブランチ → PR → squash merge）で運用します。
規約の詳細は [`docs/conventions.md`](docs/conventions.md)、意思決定は [`docs/adr/`](docs/adr/) を参照。

## セットアップ
```bash
uv sync                       # 依存（任意グループは pyproject.toml 参照）
pre-commit install            # ローカルの一次ゲート（ADR 0004）
bash scripts/check_env.sh     # このマシンの環境確認
```

## 作業フロー（ai-dev-kit スキルと対応）
1. `start` / `new-feature` … Issue 確認 → `main` からブランチ作成
2. 実装（`registry/` にモデル追加 or `harness/` 実装 など）
3. `pre-commit run --all-files` を通す
4. `ship` … commit（Conventional Commits）→ push → PR
5. `review` / `test-check` … レビューと完了判定
6. squash merge

## ブランチ命名
`feat/*` `fix/*` `exp/*`（計測ラン） `model/<id>`（モデル追加） `docs/*` `env/*` `chore/*`

## コミット規約（Conventional Commits）
`feat: …` `fix: …` `docs: …` `exp: …` `model: …` `chore: …` `refactor: …` `ci: …`
- 例: `model: add gemma4-26b-a4b to registry`

## モデル追加（オンボーディング）
`registry/models.yaml` に1行 → 「モデル・オンボーディング」Issue のチェックリスト
（Fit→Speed→標準ベンチ→自前タスク→`results/results.csv` 追記）。詳細は research §12〜§13.5。

## 守ること
- **`datasets/golden/` に実データを入れない**（公開リポ。`.gitignore` + pre-commit + CI guard で保護）
- `results/results.csv` は**追記**（過去を書き換えない）
- judge モデル・ゴールデンセット版は固定（過去比較の連続性）
