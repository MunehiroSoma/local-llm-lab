# Python コーディング規約

- Version: 1.2 / 作成: 2025-12-25 / 最終更新: 2026-02-17
- 作成者・最終更新者: 宗廣 颯真
- 対象: Python による開発全般（Web / バッチ / スクリプト）
- 本ページは**コードの書き方のみ**を扱う（レビュー手順・環境構築・AIレビュー・運用は別ページ）。
- **機械化方針**: 本規約のうち機械判定可能な項目は **ruff** で強制（末尾「ruff適用マッピング」）。型検査は **mypy strict**。

## 設計書との整合性
- コードと設計書は**双方向に相互参照可能**であること（設計書→コード／コード→設計書）。
- 設計書の用語・機能名・概念名を、モジュール/クラス/関数/変数名へ可能な限り反映。
- 設計書の単位（機能ID/画面ID/API名/バッチ名/ユースケース名）に対応する単位をコード上で特定可能に。
- 設計変更時はコードと設計書の差分を放置しない（差分はチケット化し、どちらが正かを明確化）。

## 基本ルール / ツール
- Linter: **ruff**（pylint 併用可）／整形: **ruff format**（black 相当）／import 整形: **ruff (isort)**／型: **mypy** 推奨。
- ※本リポジトリでは black/isort を **ruff に一本化**（`pyproject.toml`）。

## ディレクトリ構造（アプリ開発時）
```
project/
  ├─ src/{app, domain, infrastructure, utils}/
  ├─ tests/
  ├─ pyproject.toml
  └─ README.md
```

## ファイルヘッダー（src/ 配下のアプリコード）
- モジュール docstring を最上部（import より前）に置く。履歴は Git に寄せ、書きすぎない。
- 設計書ID/画面ID/API-ID/バッチID で参照可能に。機密情報は書かない。

```python
"""
<ファイルの概要を1行で>

- 目的: <責務 / 何を提供するか>
- 対象: <主な利用者（API層 / バッチ / CLI 等）>
- 関連: <設計書ID / チケットID / 画面ID / API-ID>

作成者: <氏名>
作成日: YYYY-MM-DD
最終更新者: <氏名>
最終更新日: YYYY-MM-DD
"""
```
最終更新日/者は運用が回らなければ省略可（作成者・概要・関連だけでも価値あり）。

## コードスタイル
- インデント: スペース4（タブ禁止） / 行長: 120文字以内 / 文字コード: UTF-8。
- import 順序: 標準ライブラリ → サードパーティ → アプリ内部。

## 命名規則
| 対象 | 規則 | 例 |
|---|---|---|
| 変数 | snake_case | `user_name` |
| 関数 | snake_case | `fetch_user` |
| クラス | PascalCase | `UserService` |
| 定数 | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |
| ファイル名 | snake_case | `user_service.py` |

## 型ヒント
- すべての関数に型を明記（引数・返却値）。戻り値なしは `-> None` を明記。
- Union は `|` 記法（Python 3.10+）。

## 括弧 `(` と空白（PEP 8・最終整形は ruff format が正）
1. 関数名と `(` の間は空白禁止（定義/呼び出し共通）: `fetch_user(user_id)`
2. `(` 直後・`)` 直前は空白禁止: `f(x, y)`
3. 区切り `,` の後ろは空白1、前は空白禁止: `f(x, y, z)`
4. 型注釈 `:` は前空白禁止・後空白1: `user_id: int`
5. 返却型 `->` は前後空白1: `def f(x: int) -> int:`
6. デフォルト引数 `=`: 型注釈なしは前後空白なし `def f(limit=10):`／型注釈ありは前後空白 `def f(limit: int = 10) -> None:`
7. 呼び出しのキーワード引数 `=` は前後空白なし: `fetch_user(user_id=1, include_profile=True)`

## クラス / 関数の設計
- 関数の責務は「単一」。ネスト（if/for）は**3段以内**。複雑な処理は private に分離。過度な抽象化は禁止。

## コメント / Docstring（Sphinx napoleon / Google スタイル前提）
- コメントは **Why**（なぜ）を書く。**What** の羅列は避ける。処理単位コメントは短い体言止めで粒度を揃える。
- `""" """` は Docstring 専用（コメント目的で使わない）。行末コメントは最小限。
- Docstring は **Google スタイル**。型は Docstring に重複記載せず**型ヒントへ一本化**。
- セクション順序: `Args:` → `Returns:` → `Raises:` → `Examples:`。
- `dict[str, Any]` 等で抽象的な場合は、型名でなく**期待キー/構造（必須/任意/制約）**を記述。

```python
def fetch_user(user_id: int) -> User:
    """ユーザーIDを指定してユーザー情報を取得する。

    Args:
        user_id: 対象ユーザーID。正の整数であること。

    Returns:
        ユーザーエンティティ。

    Raises:
        UserNotFound: 指定したIDのユーザーが存在しない場合。
        ValueError: user_id が正の整数でない場合。
    """
```

## エラーハンドリング
- 禁止: 空の `except:` / `except Exception:` の乱用 / ログなしで例外を握りつぶす。
- 推奨: 想定例外型を捕捉しコンテキストをログに残す。握りつぶさず上位へ伝播（必要ならラップ）。

```python
try:
    user = repo.get(id)
except UserNotFound:
    logger.warning("User not found", user_id=id)
    raise
```

## ログ出力
- JSON形式推奨。`user_id` / `trace_id` を含める。`print` デバッグ禁止。`logging` または `structlog`。

## セキュリティ
- `eval` / `exec` 禁止。Secrets 直書き禁止。`requests` は `timeout` 必須。SQL は ORM か安全なプレースホルダ。

## テスト
- テスト名: `test_functionName_expectedBehavior`。正常系・異常系の両方。Mock は必要最小限。

## 禁止事項
- 未使用変数・未使用import / マジックナンバー / print デバッグ / コメントとコードの不一致 /
  例外の握りつぶし / 過度な if-else ネスト / グローバル変数の乱用。

---

## ruff 適用マッピング（本規約 → 機械化）
`pyproject.toml [tool.ruff]` で強制。⚠️ は ruff 対象外（レビュー / mypy）。

| 規約項目 | ruff ルール | 自動 |
|---|---|---|
| 行長120 / 文字コード | `E501`, format | ✅ 整形 |
| インデント4・タブ禁止 | `W191`, `E101` | ✅ |
| import 順序 | `I` (isort) | ✅ fix |
| 命名(snake/Pascal/UPPER) | `N` | ✅ 検出 |
| 型ヒント必須 / `-> None` | `ANN` | ✅ 検出 |
| `\|` union 記法 | `UP` | ✅ fix |
| 括弧/`=`/`,`/`:`/`->` の空白(1–7) | `E2xx` + format | ✅ 整形 |
| ネスト3段/複雑度 | `C90` (max-complexity) | ✅ 検出 |
| Docstring(Google/Sphinx) | `D` + convention=google | ✅ 検出 |
| print 禁止 | `T20` | ✅ 検出 |
| eval/exec 禁止 | `S307`, `S102` | ✅ 検出 |
| requests timeout 必須 | `S113` | ✅ 検出 |
| 未使用 import/変数 | `F401`, `F841` | ✅ fix |
| マジックナンバー | `PLR2004` | ✅ 検出 |
| 空 except / 握りつぶし | `E722`, `BLE001`, `S110` | ✅ 検出 |
| 型検査(mypy strict) | ruff外 → **mypy** | ✅ mypy |
| テスト命名 / 正常・異常系 | ⚠️ レビュー | — |
| 設計書↔コード 相互参照 | ⚠️ レビュー | — |
| ログJSON/trace_id | ⚠️ structlog/レビュー | — |
| ファイルヘッダー docstring | ⚠️ レビュー(将来カスタムhook可) | — |
