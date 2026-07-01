# コードレビューチェックリスト（Python）

> PRごとに使用。Must が全て ✓ になり NG 件数が 0 になってから Approve する。
> 区分「自動」は pre-commit / CI が green であればスキップ可。「手動」は必ず目視確認。
> 関連規約: [`python.md`](python.md) / ADR 0004

**PR番号/URL**: ＿＿＿＿　**レビュー対象**: ＿＿＿＿　**レビュアー**: ＿＿＿＿　**レビュー日**: ＿＿＿＿

---

## 共通（全言語）

| No | カテゴリ | チェック項目 | 区分 | 重要度 | チェック | 備考 |
|---|---|---|:---:|:---:|:---:|---|
| 1 | 基本品質 | 未使用変数・未使用importが残っていない | 自動 | Must | | ruff F401/F841 |
| 2 | 基本品質 | デバッグ用の出力（print/pprint等）が残っていない | 自動 | Must | | ruff T201 |
| 3 | 基本品質 | マジックナンバーが定数化されている | 手動 | Should | | ruff PLR2004 (一部) |
| 4 | 基本品質 | コメントとコードの実装内容が一致している | 手動 | Must | | |
| 5 | 基本品質 | 不要なコメントアウトコードが残っていない | 手動 | Nits | | |
| 6 | エラー処理 | 例外を握りつぶしていない（空の except / reraise なし） | 手動 | Must | | ruff BLE001 |
| 7 | エラー処理 | 過度な if-else ネストになっていない | 自動 | Should | | ruff C901 (max-complexity=10) |
| 8 | セキュリティ | Secret情報がハードコードされていない | 自動 | Must | | detect-private-key (pre-commit) |
| 9 | セキュリティ | ユーザー入力が安全に扱われている（SQLインジェクション対策） | 手動 | Must | | ruff S608 |
| 10 | セキュリティ | ログに機密情報が出力されていない | 手動 | Must | | |
| 11 | テスト | 正常系のテストが存在する | 手動 | Must | | |
| 12 | テスト | 異常系・境界値のテストが存在する | 手動 | Should | | |
| 13 | テスト | テストコードが CI で実行されグリーンになっている | 自動 | Must | | |
| 14 | 設計整合性 | 設計書・ADR の用語・機能名がコード上の命名に反映されている | 手動 | Must | | |
| 15 | 設計整合性 | 設計変更とコードの差分が放置されていない | 手動 | Should | | |
| 16 | 運用ルール | コードフォーマッタが通過している（ruff format） | 自動 | Must | | pre-commit ruff-format |
| 17 | 運用ルール | 命名がコーディング規約に沿っている（snake_case/PascalCase等） | 自動/手動 | Should | | ruff N |
| 18 | PR運用 | PRの説明に背景・変更内容・テスト方法が記載されている | 手動 | Should | | |
| 19 | PR運用 | PRが1つの目的に絞られている（1 BOLT = 1 PR） | 手動 | Should | | |

---

## Python 固有

| No | カテゴリ | チェック項目 | 区分 | 重要度 | チェック | 備考 |
|---|---|---|:---:|:---:|:---:|---|
| 1 | コードスタイル | ruff check が通過している（E/W/F/I/N/D/ANN/UP/B/S/T20/C90/PL） | 自動 | Must | | pre-commit ruff --fix |
| 2 | コードスタイル | ruff format が適用されている（blackの代替） | 自動 | Must | | pre-commit ruff-format |
| 3 | コードスタイル | import整形が適用されている（ruff I — 標準→サードパーティ→自プロジェクト順） | 自動 | Should | | ruff I |
| 4 | 型 | mypy --strict が通過している | 自動 | Should | | pre-commit mypy |
| 5 | 型 | 型ヒントが適切に記載されている（関数引数・戻り値すべて） | 手動 | Should | | ruff ANN — `Any` の乱用に注意 |
| 6 | ドキュメント | 公開関数・クラスに Google 形式 Docstring が記載されている | 手動 | Should | | ruff D — Google convention |
| 7 | エラー処理 | 裸の `except:` や `except Exception:` の乱用がない | 手動 | Must | | ruff BLE001 / B001 |
| 8 | ログ | ログが構造化されており trace_id 等のコンテキストを含んでいる | 手動 | Should | | |
| 9 | セキュリティ | `eval()` / `exec()` を使用していない | 自動 | Must | | ruff S307 |
| 10 | セキュリティ | `requests` 呼び出しに `timeout=` が設定されている | 手動 | Must | | ruff S113 |
| 11 | セキュリティ | SQL が ORM またはプレースホルダを使用している（f-string結合不可） | 手動 | Must | | ruff S608 |
| 12 | テスト | テスト名が `test_<対象>_<条件>_<期待結果>` 形式になっている | 手動 | Nits | | コーディング規約 §テスト |
| 13 | 設定 | `pyproject.toml` の ruff/mypy 設定が規約の最低限を満たしている | 手動 | Should | | line-length=120, select 不要な削除なし |

---

## チェック結果サマリ

| 区分 | 件数 |
|---|---|
| Must — NG | |
| Should — NG | |
| Nits — 指摘 | |
| **マージ可否** | Must NG=0 かつ CI green → **Approve 可** |
