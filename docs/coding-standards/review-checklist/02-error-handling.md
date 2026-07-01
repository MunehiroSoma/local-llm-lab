# 観点: エラー処理

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**（既存実装への指摘はしない）。
> 想定モデル: 軽量モデル（パターン検出中心）。ロジック複雑度が高い差分は上位モデルへ切替を検討。

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | 例外を握りつぶしていない（空の except / reraise なし） | 手動 | Must | ruff BLE001 |
| 2 | 裸の `except:` や `except Exception:` の乱用がない | 手動 | Must | ruff BLE001 / B001 |
| 3 | 過度な if-else ネストになっていない | 自動 | Should | ruff C901 (max-complexity=10) |

> 自動区分は pre-commit/CI が green であればスキップ可。
