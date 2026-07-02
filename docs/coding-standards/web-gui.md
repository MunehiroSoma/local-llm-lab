# Web / GUI コーディング規約

- Version: 1.1 / 作成: 2026-07-02 / 最終更新: 2026-07-02
- 対象: React + TypeScript フロントエンド + FastAPI バックエンド（ADR 0007 Phase B）
- 本ページは **Web/GUI 実装固有のルールのみ**を扱う。
  フロントエンドのコード書式は [`javascript-typescript.md`](javascript-typescript.md)、
  バックエンド（FastAPI）は [`python.md`](python.md) をそれぞれ継承する。
- 関連: ADR 0007（技術選定） / [`review-checklist/07-web-security.md`](review-checklist/07-web-security.md)

## 適用条件
`web/`（React）配下、および `harness/` 等を薄くラップする FastAPI の API コードを
追加・変更する PR にのみ適用する。非GUIコードには適用しない。

## 構成
- フロントエンド: `web/`（React + TypeScript + Vite）。ディレクトリ構成は
  [`javascript-typescript.md`](javascript-typescript.md) の「ディレクトリ構造」節に従う。
- バックエンド: FastAPI で `harness/` の機能を薄くラップした API を提供する。
  ビジネスロジック・集計・harness 呼び出しは `harness/` 側に置き、API 層（`presentation`/`routers`
  相当）は「リクエストの受け取り→`harness/`呼び出し→レスポンス整形」のみに責務を絞る。
  React からロジックを直接呼ぶことはしない（必ず API 経由）。

## バインド先・公開範囲
- 開発・単独利用時は **FastAPI / Vite dev server ともに `127.0.0.1`（localhost）に明示バインド**する。
  `0.0.0.0` での起動は禁止。
  - FastAPI: `uvicorn app:app --host 127.0.0.1`
  - Vite: `vite --host 127.0.0.1`
- **LAN/外部公開が必要な場合は認証必須**（本ラボの推論サーバに関する CI/CD 総点検資料 §E-7 と
  同じ理由: 認証なしのサーバは誰でも操作できてしまう）。無認証での LAN 公開は禁止。
- **CORS はオリジンを明示的に許可リスト化**する（開発時の `http://127.0.0.1:5173` 等）。
  `allow_origins=["*"]` の使用は禁止。
- 公開範囲の変更（127.0.0.1 → LAN/外部）は ADR 相当の重い変更として扱い、
  レビュー時に必ず確認する（[`review-checklist/07-web-security.md`](review-checklist/07-web-security.md)）。

## 状態管理（フロントエンド）
- まずコンポーネントローカルの state（`useState`/`useReducer`）を優先する。
- 複数コンポーネント間で共有が必要な状態のみ、Context API 等の軽量な仕組みを使う
  （大規模な状態管理ライブラリは実際に必要になってから導入する。YAGNI）。
- グローバルなミュータブル変数での状態保持は禁止。

## 秘密情報の管理
- **フロントエンド（React ビルド成果物）に秘密を一切埋め込まない**。ビルド後の JS はブラウザに
  配信され誰でも読めるため、API キー等をフロント側の環境変数（`VITE_*` 等）に置かない。
- 秘密が必要な外部呼び出しは必ず FastAPI 側から行い、React はバックエンドAPI経由でのみ結果を得る。
- バックエンドの秘密は `.env`（gitignore）で管理する（[`python.md`](python.md) のセキュリティ規約を継承）。

## ユーザー入力の描画（XSS）
- React はデフォルトで JSX 出力をエスケープするが、`dangerouslySetInnerHTML` の使用を禁止する。
  どうしても必要な場合は信頼できるサニタイズライブラリを通す。
- `results.csv` の `notes` 列等、外部/過去データ由来の文字列を描画する場合も同様に扱う。

## a11y（アクセシビリティ）・UI一貫性
- チャート実装時は `dataviz` スキルの色・形式規約に従う（色のみに依存しない、コントラスト確保）。
- 同一アプリ内でのラベル・ボタン文言・レイアウトパターンは既存画面と揃える
  （初期実装時点では強制力のあるルールは設けず、レビュー時の目視確認とする）。

## 依存関係
- フロントエンド依存（react/typescript/vite/eslint/prettier/vitest等）は `web/package.json` に
  バージョンピンで追加する。
- バックエンド依存（fastapi/uvicorn等）は `pyproject.toml` の `api` optional-dependencies
  グループに追加し、バージョンピンする。
- いずれも追加時は CI/CD レビュー資料 C-1・C-5（実在確認・メンテ状況確認）を先に済ませる。
