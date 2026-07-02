# 観点: セキュリティ

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**（既存実装への指摘はしない）。
> 想定モデル: 上位モデル（誤検知コストが高いため）。

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | Secret情報がハードコードされていない | 自動 | Must | detect-private-key (pre-commit) |
| 2 | ユーザー入力が安全に扱われている（SQLインジェクション対策） | 手動 | Must | ruff S608 |
| 3 | ログに機密情報が出力されていない | 手動 | Must | |
| 4 | `eval()` / `exec()` を使用していない | 自動 | Must | ruff S307 |
| 5 | `requests` 呼び出しに `timeout=` が設定されている | 手動 | Must | ruff S113 |
| 6 | SQL が ORM またはプレースホルダを使用している（f-string結合不可） | 手動 | Must | ruff S608 |

> 自動区分は pre-commit/CI が green であればスキップ可。
