# 観点: 基本品質

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**（既存実装への指摘はしない）。
> 想定モデル: 軽量モデル（規約・フォーマット系の機械的チェックが中心）。

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | 未使用変数・未使用importが残っていない | 自動 | Must | ruff F401/F841 |
| 2 | デバッグ用の出力（print/pprint等）が残っていない | 自動 | Must | ruff T201 |
| 3 | マジックナンバーが定数化されている | 手動 | Should | ruff PLR2004（一部） |
| 4 | コメントとコードの実装内容が一致している | 手動 | Must | |
| 5 | 不要なコメントアウトコードが残っていない | 手動 | Nits | |
| 6 | ruff check が通過している（E/W/F/I/N/D/ANN/UP/B/S/T20/C90/PL） | 自動 | Must | pre-commit ruff --fix |
| 7 | ruff format が適用されている（blackの代替） | 自動 | Must | pre-commit ruff-format |
| 8 | import整形が適用されている（標準→サードパーティ→自プロジェクト順） | 自動 | Should | ruff I |
| 9 | mypy --strict が通過している | 自動 | Should | pre-commit mypy |
| 10 | 型ヒントが適切に記載されている（関数引数・戻り値すべて） | 手動 | Should | ruff ANN — `Any` の乱用に注意 |
| 11 | 公開関数・クラスに Google 形式 Docstring が記載されている | 手動 | Should | ruff D — Google convention |
| 12 | ログが構造化されており trace_id 等のコンテキストを含んでいる | 手動 | Should | |
| 13 | 命名がコーディング規約に沿っている（snake_case/PascalCase等） | 自動/手動 | Should | ruff N |
| 14 | `pyproject.toml` の ruff/mypy 設定が規約の最低限を満たしている | 手動 | Should | line-length=120, select 不要な削除なし |

> 自動区分（pre-commit/CI で担保される項目）は green であればスキップ可。手動区分のみ観点特化エージェントの主対象とする。
