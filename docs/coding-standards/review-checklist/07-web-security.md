# 観点: Web セキュリティ

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**（既存実装への指摘はしない）。
> 想定モデル: 上位モデル（誤検知コストが高いため）。
> **起動条件: React(`web/`)/FastAPI 等の Web/GUI 実装を含む差分のときのみ起動する**（ADR 0007 Phase B以降）。
> 関連規約: [`web-gui.md`](../web-gui.md) / [`javascript-typescript.md`](../javascript-typescript.md)

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | サーバのバインド先が `127.0.0.1` に明示されている（FastAPI/Vite dev serverとも `0.0.0.0` になっていない） | 手動 | Must | `web-gui.md` §バインド先 |
| 2 | LAN/外部公開する場合に認証が設定されている | 手動 | Must | `web-gui.md` §バインド先 |
| 3 | CORS の `allow_origins` が明示的な許可リストであり `["*"]` になっていない | 手動 | Must | `web-gui.md` §バインド先 |
| 4 | API キー等の秘密がフロントエンド（`web/`）に埋め込まれず、バックエンド経由でのみ扱われている | 手動 | Must | `web-gui.md` §秘密情報の管理。`VITE_*` 環境変数への秘密混入に注意 |
| 5 | `dangerouslySetInnerHTML` を使用していない、または使用時にサニタイズを通している（XSS） | 手動 | Must | `web-gui.md` §XSS |
| 6 | API 層（FastAPI ルータ）にビジネスロジックを直接書かず `harness/` から呼び出している | 手動 | Should | `web-gui.md` §構成 |
| 7 | フロントエンドの状態管理がコンポーネントローカル優先で、グローバルミュータブル変数を使っていない | 手動 | Should | `web-gui.md` §状態管理 |
| 8 | 依存追加（react/vite/fastapi等）が `web/package.json` または `pyproject.toml` の `api` グループにバージョンピンされている | 手動 | Should | ADR 0007 |

> 自動区分は pre-commit/CI が green であればスキップ可（Web/GUI 固有の ESLint/Prettier 等の
> pre-commit 組み込みは Phase B 実装 Issue で行う）。
