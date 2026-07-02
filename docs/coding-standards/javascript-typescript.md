# コーディング規約: JavaScript / TypeScript

- Version: 0.1 / 作成: 2026-03-25 / 最終更新: 2026-03-25
- 作成者・最終更新者: 宗廣 颯真
- 対象: JavaScript / TypeScript による開発全般（Vue / React / Node.js）
- 関連: ADR 0007（Phase B は React + TypeScript を主軸に採用） / [`web-gui.md`](web-gui.md)
- 本ページは **JavaScript / TypeScript におけるコードの書き方（コーディング規約）のみ**を扱う。
  レビュー手順・環境構築・AIレビュー・運用ルールは別ページ（[`review-checklist/`](review-checklist/)）。

## 含まれる情報
コードスタイル / 命名規則 / 型（TypeScript）の記法ルール / クラス・関数の設計方針 /
コメント・JSDoc のルール（JSDoc 出力前提） / エラーハンドリング / ログの書き方 /
セキュリティ上の注意点 / テストの命名と基本的な記述ルール / 禁止事項 /
Vue 向け補足 / React 向け補足 / Node.js（バックエンド）向け補足。

> 本リポジトリでは Phase B のバックエンドは FastAPI（Python）を採用するため（ADR 0007）、
> 「Node.js（バックエンド）向け補足」は現時点では適用対象外。将来 Node.js バックエンドを
> 採用する場合の参考として残す。

## JS と TS の使い分け方針
- 新規プロジェクトは **TypeScript を使用する**。
- 既存の JavaScript プロジェクトに対しては、段階的な TypeScript 移行を推奨する。
- 本規約は JS / TS 共通ルールを基本とし、TypeScript のみに適用されるルールは **【TS のみ】** と明記する。

## 設計書との整合性
- コードと設計書は**常に相互参照可能（双方向）**であること（[`python.md`](python.md) と同方針）。
- 設計書に登場する用語・機能名・概念名は、コードのモジュール名/クラス名/関数名/変数名へ可能な限り反映する。
- 設計書の単位（機能ID/画面ID/API名/バッチ名/ユースケース名）に対応する単位をコード上で特定可能にする。
- 設計変更時はコードと設計書の差分を放置しない（差分はチケット化し、どちらが正かを明確化する）。

## コーディング時の基本ルール
- Linter: **ESLint** / Formatter: **Prettier** / import 整形: ESLint `import` プラグイン。
- 【TS のみ】型チェックに TypeScript Compiler（`tsc --noEmit`）を推奨。
- ツールのセットアップ手順は本ページでは扱わない（Phase B 実装 Issue で pre-commit/CI に組み込む）。

## ディレクトリ構造

フロントエンド（React 想定。Vue 採用時も同構成）:
```
web/
  ├─ src/
  │   ├─ components/      # UIコンポーネント
  │   ├─ pages/            # ページ単位のコンポーネント
  │   ├─ hooks/             # ロジックの再利用（React: hooks / Vue: composables）
  │   ├─ stores/            # 状態管理
  │   ├─ services/          # API 呼び出し
  │   └─ utils/             # 汎用ユーティリティ
  ├─ tests/
  ├─ package.json
  └─ README.md
```

Node.js バックエンドを採用する場合（本リポジトリは当面 FastAPI のため参考情報）:
```
project/
  ├─ src/{application, domain, infrastructure, presentation}/
  ├─ tests/
  ├─ package.json
  └─ README.md
```

## ファイルのヘッダー
- `src/` 配下のアプリコード（ドメイン・API・バッチ・重要ユーティリティ）に適用。`tests/` は任意。
- ファイル先頭の JSDoc（`/** ... */`）をファイルヘッダーとして扱う。履歴はGitに寄せ書きすぎない。
- 設計書がある場合は設計書ID/画面ID/API-ID等で参照可能にする。機密情報は書かない。

```js
/**
 * @fileoverview <ファイルの概要を1行で>
 *
 * 目的: このファイルの責務 / 何を提供するか
 * 対象: 主な利用者（例: API層 / バッチ / CLI）
 * 関連: 設計書ID / チケットID / 画面ID / API-ID など
 *
 * @author 氏名
 * @since YYYY-MM-DD
 */
```

## コードスタイル
- インデント: スペース2（Prettierデフォルト） / 行長: 100文字以内 / 文字コード: UTF-8。
- 文字列リテラル: シングルクォート `'` を使用。テンプレートリテラルは文字列補完が必要な場合のみ。
- セミコロン: **あり**（Prettierデフォルト）に統一。
- import 順序: 標準（Node.js） → サードパーティ（React等） → アプリ内部（`@/`エイリアス等）。未使用importは残さない。

## 命名規則
| 対象 | 規則 | 例 |
|---|---|---|
| 変数 / 関数 | camelCase | `userName`, `fetchUser` |
| クラス | PascalCase | `UserService` |
| 定数 | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |
| ファイル名（スクリプト） | camelCase | `userService.ts` |
| ファイル名（コンポーネント） | PascalCase | `UserCard.tsx` |
| 型 / インタフェース【TSのみ】 | PascalCase | `UserResponse` |
| Enum【TSのみ】 | PascalCase | `UserRole` |

## 型（TypeScript のみ）【TS のみ】
- `any` の使用を禁止。どうしても必要な場合は `unknown` を使い、型を絞り込んでから使用する。
- 関数の引数と返り値には必ず型を付ける。型推論で明らかな変数宣言は型注釈を省略してよい。
- `strictNullChecks`（`strict`モード）を有効化。`null`/`undefined`はプロジェクト内で統一
  （推奨: `undefined`。`null`は外部APIレスポンス等避けられない場合のみ許容）。
- オブジェクトの型定義は `interface`、Union型・交差型・プリミティブのエイリアスは `type`。

```ts
// OK
function fetchUser(userId: number): Promise<User> { ... }
// NG（any の使用）
function fetchUser(userId: any): any { ... }
```

## 非同期処理
- `Promise` ベースの処理は `async / await` を使う。callback スタイルは原則禁止（既存ライブラリのI/Fを除く）。
- エラーハンドリングは `try / catch` で行い、`.catch()` のみへの依存を避ける。

## クラスと関数の設計
- 関数の責務は「単一」。ネスト（if/for）は3段以内。複雑な処理は別関数に分離。過度な抽象化は禁止。
- フロントエンドでは**クラスよりも関数コンポーネント / Hooks を優先する**。

## コメントと JSDoc
- コメントは "Why"（なぜ）を書く。"What" の羅列は避ける。
- 処理単位コメントは短い体言止めで粒度を揃える（入力検証→取得→変換→保存 等の段階が追える場合に付与）。
- `/** ... */` は JSDoc 専用。`// ...` は実装上の補足（Why）。`/* ... */` は一時的なコメントアウトのみ（コミット時には残さない）。
- JSDoc はセクション: 1行目に要約 → `@param` → `@returns` → `@throws`。型は【TSのみ】シグネチャに一本化し `@type`/`@param {型}` を重複記載しない。

```ts
/**
 * ユーザー ID を指定してユーザー情報を取得する。
 *
 * @param userId - 対象ユーザー ID。正の整数であること。
 * @returns ユーザーエンティティ。見つからない場合は `undefined`。
 * @throws {UserNotFoundError} 指定した ID のユーザーが存在しない場合。
 */
async function fetchUser(userId: number): Promise<User | undefined> { ... }
```

## エラーハンドリング
- 禁止: 空の `catch` / `catch (e) {}` による握りつぶし / `console.error` だけ出力して何もしない /
  Promise の `.catch()` を付けずに放置（unhandled rejection）。
- 推奨: 想定例外型を捕捉しコンテキストをログに残す。握りつぶさず上位へ伝播（必要ならラップ）。
  エントリポイントで未処理例外を一箇所でハンドリングする。
- ビジネス例外は `Error` を継承したカスタムクラスとして定義する。

```ts
export class UserNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UserNotFoundError";
  }
}
```

## ログ出力
- Node.js バックエンド採用時は **winston** または **consola**。ブラウザは `console` を開発時限定にし、本番では無効化。
- JSON形式（構造化ログ）推奨。`userId`/`traceId`/`requestId` を含める。デバッグ用 `console.log` はコミットしない。機密情報をログに含めない。

| レベル | 使いどころ |
|---|---|
| error | 予期しないシステムエラー・業務継続不能な障害 |
| warn | 業務上の異常（ユーザー未存在・バリデーション違反等） |
| info | 正常系の業務イベント |
| debug | 開発・調査用途（本番では原則OFF） |

## セキュリティ
- `eval()` / `new Function()` の使用を禁止。
- Secrets（APIキー/パスワード等）のソースコードへの直書き禁止（環境変数を使用）。
- 外部HTTP通信には必ずタイムアウトを設定する（`axios`/`fetch`共通）。
- ユーザー入力をそのままDOMに挿入しない（XSS防止）。`innerHTML` への直接代入を禁止し、
  フレームワークのテンプレート機能を使う（[`review-checklist/07-web-security.md`](review-checklist/07-web-security.md) と対応）。
- SQL/NoSQLクエリはORM/ドライバのプレースホルダを使用し、文字列結合によるクエリ組み立てを禁止する。

## テストの基本ルール
- テスト名の形式: `関数名_期待する結果_条件`（例: `fetchUser_returnsUser_whenUserExists`）。
- 正常系・異常系・境界値を両方作成する。
- テストフレームワーク: **Vitest**（または Jest）。Mock は `vi.mock`/`jest.mock` で外部I/O（DB・外部API）のみをモック化（過剰なMock禁止）。
- フロントエンドのコンポーネントテストは **Testing Library** を使用する。

## 禁止事項
- 未使用変数・未使用import / マジックナンバー / デバッグ用`console.log`のコミット /
  コメントとコードの不一致 / 例外の握りつぶし / 過度なif-elseネスト / `var`の使用（`const`/`let`を使う） /
  【TSのみ】`any`の使用 / `eval()`・`new Function()`の使用 / `innerHTML`へのユーザー入力の直接代入。

---

## Vue 向け補足
> Vue採用時のみ適用。基本規約と重複する部分は基本規約を優先する。

- **Composition API**（`setup()`）を使用する（Options APIは禁止）。
- コンポーネントはUI表示に専念し、ビジネスロジックはComposableに切り出す。
- `defineProps` は型引数を使った形式（TypeScript）で定義する。
- ファイル構成: `<script setup>` → `<template>` → `<style scoped>` の順。

## React 向け補足
> 本リポジトリ Phase B の主軸（ADR 0007）。基本規約と重複する部分は基本規約を優先する。

- **関数コンポーネント**を使用する（クラスコンポーネントは禁止）。
- コンポーネントはUI表示に専念し、ビジネスロジックはカスタムHooksに切り出す。

```tsx
// OK
const UserCard = ({ userId }: { userId: number }) => {
  const { user, isLoading } = useFetchUser(userId);
  return <div>{user?.name}</div>;
};
// NG（クラスコンポーネント）
class UserCard extends React.Component { ... }
```

- カスタムHooksの関数名は `use` プレフィックスを付ける。Hooksは条件分岐の中で呼び出さない（Rules of Hooks）。
- Propsの型は `interface` または `type` で明示的に定義する。

## Node.js（バックエンド）向け補足
> 本リポジトリは Phase B のバックエンドに FastAPI（Python）を採用するため当面適用対象外
> （ADR 0007）。将来 Node.js バックエンドを採用する場合の参考として残す。

- モジュール形式は **ESModules**（`import`/`export`）を使用する（CommonJSの`require`は禁止）。
- 環境変数は `process.env` から直接参照せず、設定モジュールに集約する。未定義の環境変数はアプリ起動時に検出しエラーとして扱う。

| 対象 | 命名規則 | 例 |
|---|---|---|
| Router / Controller | `〇〇Router` / `〇〇Controller` | `userRouter` |
| Service | `〇〇Service` | `userService` |
| Repository | `〇〇Repository` | `userRepository` |
| DTO（入力） | `〇〇Request` | `CreateUserRequest` |
| DTO（出力） | `〇〇Response` | `UserResponse` |
| Entity | 単純名 | `User` |
| 設定 | `〇〇Config` | `databaseConfig` |

---

## 改定履歴
| Version | 日付 | 変更者 | 変更内容 |
|---|---|---|---|
| 0.1 | 2026-03-25 | 宗廣 颯真 | 初版作成 |
| 0.1（本リポジトリ採用） | 2026-07-02 | — | ADR 0007 に伴い local-llm-lab の `docs/coding-standards/` へ導入。Node.js バックエンド節を適用対象外として明記 |
