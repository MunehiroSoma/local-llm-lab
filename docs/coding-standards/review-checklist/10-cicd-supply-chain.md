# 観点: CI/CD・サプライチェーン

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**。
> 想定モデル: 上位モデル。
> **起動条件: `.github/workflows/` の変更、または依存関係（`pyproject.toml`/`uv.lock`/`web/package.json`等）の
> 追加・更新を含む差分のときのみ起動する**（Issue #46。CI/CD総点検資料 §F）。

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | GitHub Actions の `uses:` がコミットSHAでピン留めされている（タグ参照でない） | 手動 | Must | サプライチェーン攻撃対策。actionlintは構文チェックのみでSHA固定は検出しない |
| 2 | workflow の `permissions` が必要最小限に設定されている | 手動 | Should | |
| 3 | 新規依存追加時に実在性・メンテ状況・ライセンスを確認している | 手動 | Should | typosquatting対策 |
| 4 | ロックファイル（`uv.lock`/`web/package-lock.json`等）の更新が `pyproject.toml`/`package.json` の変更と整合している | 手動 | Should | |
| 5 | workflow に `timeout-minutes` / `concurrency` が設定されている | 手動 | Nits | |

> `.github/workflows/` の構文/設定ミスは pre-commit の actionlint（自動）でも一部検出される。
