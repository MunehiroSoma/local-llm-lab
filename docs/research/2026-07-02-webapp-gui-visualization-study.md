# Webアプリ/GUI・結果可視化・レポート出力の事前調査（2026-07-02）

将来「Web画面またはスタンドアロンアプリで GUI 操作し、results をグラフで確認し、
md / pdf / csv で出力する」構想に向けて、必要な技術・規約・スキル・プラグインを棚卸しする。
本資料は Inception フェーズの入力であり、技術の最終決定は ADR で行う（ここでは決定しない）。

## 1. 要件の整理

| 要件 | 具体像 | 既存資産との関係 |
|---|---|---|
| GUI 操作 | モデル×環境×評価の実行指示・進捗確認 | `harness/`（未実装）を呼ぶフロントエンド |
| グラフ確認 | tok/s・TTFT・スコアの比較チャート、機種間比較 | `results/results.csv` が唯一のデータソース |
| md 出力 | レポートを研究ノート/PRに貼れる形式で | `results/reports/` が置き場として既存 |
| pdf 出力 | 印刷・共有用の整形済みレポート | 新規 |
| csv 出力 | 生データの切り出し（フィルタ済み） | results.csv のサブセット抽出 |

## 2. 段階アーキテクチャ案（推奨: A→B の順に小さく進める）

### Phase A: 静的レポート生成（GUI なし・最小コスト）
`results.csv` → グラフ + 表 → md / html / pdf を一括生成するバッチ。Issue #35
（results集計→reports自動生成）と同一ラインであり、**Web アプリの前段として先に作るべき**。

- 本命候補: **Quarto**（.qmd 1ソースから html / md / pdf を多形式出力。pdf は Typst 経由が現行の定石で LaTeX 不要）
- 代替: Jinja2 + Plotly（自前テンプレート。柔軟だが車輪の再発明）
- 注意: Plotly のインタラクティブ図は pdf に入らないため、pdf 用は静的画像に変換して埋め込む（kaleido）。
  最初から「html=インタラクティブ / pdf=静的画像」の二層と割り切る

### Phase B: Web ダッシュボード（GUI 操作）

2026-07-03 追記: Phase B の標準は **React + TypeScript + Vite + Tailwind CSS** に寄せる。
Streamlit / Gradio / Dash / marimo は比較対象として残すが、Phase B の実装標準ではない。

| 候補 | 向き | 本ラボでの位置づけ |
|---|---|---|
| **React + TypeScript + Vite + Tailwind CSS** | harness API を操作する Web UI、長期運用するダッシュボード | ◎ Phase B 標準 |
| Streamlit | データアプリを最速で作る。スクリプト全再実行モデル | △ PoC には有効だが標準から外す |
| Gradio | ML デモ・チャット UI。HF Spaces / MCP 連携 | △ モデル対話 UI の実験候補 |
| Dash | エンタープライズ向け。コールバック明示 | △ 本ラボには過剰 |
| marimo | リアクティブ notebook 系の新顔 | △ 情報がまだ少ない。様子見 |

- 推奨方向: **React + TypeScript + Vite + Tailwind CSS** を `web/` 配下の標準にする。
- CSS は Tailwind utility / theme / design token を主戦力にし、大量の手書きCSS、CSS Modules、
  `style` 属性、Tailwind で表現できるものの独自 class 再定義は避ける。
- frontend tooling は `web/package.json` に分離し、ESLint / Prettier / TypeScript typecheck を基本にする。

### Phase C: スタンドアロンアプリ（必要になったら）
- Tauri / Electron はビルド・署名・更新配布の運用が重く、単独ラボでは費用対効果が低い
- Streamlit をローカル起動して `localhost` をブラウザで開く運用が実質スタンドアロンとして機能する
- 判断先送りで問題ない（ADR で「採用しない理由」だけ先に記録しておく価値はある）

## 3. 必要になる規約（現状に無いもの）

| 規約 | 内容 | いつ必要 |
|---|---|---|
| Web セキュリティ規約 | バインド先は `127.0.0.1` 明示（LAN 露出禁止。CI/CDレビュー資料 §E-7 と同根）、LAN 公開時は認証必須、XSS（ユーザ入力の描画）、CORS | Phase B 開始時 |
| GUI コード規約 | React UI と harness ロジックを分離し、React は API 経由で harness 機能を呼ぶ。秘密情報は frontend bundle に入れない | Phase B 開始時 |
| レポート再現性規約 | レポート生成もツール版固定（Quarto/kaleido のバージョンピン）、生成物に元データの版とコミットSHAを刻印 | Phase A 開始時 |
| TypeScript / React 規約 | React + TypeScript + Vite を Phase B 標準にする。ESLint / Prettier / typecheck を `web/` 側で固定 | Phase B 開始時 |
| Tailwind CSS 規約 | Tailwind utility / theme / design token を主戦力にし、CSS直書き・CSS Modules主戦力化・style属性を抑制 | Phase B 開始時 |

review-checklist への観点追加候補: **Web セキュリティ / アクセシビリティ(a11y) / UI 一貫性**。
既存6観点はいずれもカバーしない（CI/CDレビュー資料 §F の表に追記されるべき項目）。

## 4. 必要になるスキル・プラグイン

| 種別 | 名称 | 状態 | 用途 |
|---|---|---|---|
| Claude Code スキル | `dataviz` | **導入済み**（環境に既存） | チャート設計の規約（色・形式・a11y）。グラフ実装時に自動適用される |
| Claude Code スキル | `run` / `verify` | **導入済み** | アプリ起動確認・変更の実動作検証。Streamlit 起動確認に使える |
| 新規スキル | `report-gen` | #42 で追加 | 既存 `make report-results` / `harness.reporting.results_summary` の定型手順。`results.csv` は変更せず、`results/raw/` を入力にしない |
| プラグイン | Playwright MCP | Phase B UI 実装開始時に導入検討 | React + Vite UI のブラウザ自動操作による E2E 検証候補。Phase A 静的レポート生成には不要 |
| frontend tooling | ESLint / Prettier / TypeScript typecheck / Tailwind CSS | Phase B | `web/package.json` 配下で Python 側 ruff/mypy と分離して管理する |

## 5. 依存関係の見込み（pyproject 追加候補）

```toml
[project.optional-dependencies]
viz = [
    # "pandas",       # results.csv 集計
    # "plotly",       # インタラクティブ図 (html)
    # "kaleido",      # plotly → 静的画像 (pdf 埋め込み用)
    # "streamlit",    # Phase B
]
# Quarto は Python パッケージではなく CLI（brew install quarto 等）。版は runbook に固定明記
```

- 追加時は CI/CD レビュー資料 C-1（uv.lock）/ C-5（依存追加時の実在・メンテ状況確認）を先に済ませること

## 6. リスク・先回りの注意

1. **results.csv がスキーマレスのまま可視化を作ると壊れやすい** — 列定義の JSON Schema 化
   （CI/CD資料 B-4）を可視化実装より先にやる方が手戻りが少ない
2. **Streamlit を `0.0.0.0` で起動すると認証なしで LAN に露出** — 規約（§3）を実装前に文書化する
3. **pdf 出力を後回しにすると図の作り直しが発生** — Phase A の時点で「html=動的 / pdf=静的」の
   二層方針を決めておく（Plotly 図は pdf に直接入らない）
4. **judge・ゴールデンセット固定と同様、レポート生成ツールも版固定** — しないと過去レポートが再現不能になる

## 7. Issue 化する作業項目（本資料から起こすもの）

1. 可視化/GUI 技術選定 ADR + Phase A 方針（Issue #35 と接続）
2. Web/GUI 向け規約整備（コーディング規約 + review-checklist 観点追加）
3. Web 検証ツール・プラグイン整備（Playwright MCP、report-gen スキル検討）

（CI/CD 総点検資料からの Issue: リポジトリ設定強化 / 再現性・サプライチェーン /
ガード自動化 / review-checklist 観点補強 — 詳細は同資料の優先順位表を参照）

## Sources
- [Streamlit vs Dash (usedatabrain, 2026)](https://www.usedatabrain.com/blog/streamlit-vs-dash)
- [Streamlit vs Gradio vs Dash (modern-datatools, 2026)](https://www.modern-datatools.com/compare/streamlit-vs-gradio-vs-dash)
- [Gradio vs Streamlit vs Dash vs Flask (Towards Data Science)](https://towardsdatascience.com/gradio-vs-streamlit-vs-dash-vs-flask-d3defb1209a2/)
- [Quarto: Plotly graph in HTML and PDF output](https://examples.quarto.pub/py-plotly-in-pdf/)
- [Quarto: Parameterized reports with the jupyter engine](https://quarto.org/docs/blog/posts/2025-07-24-parameterized-reports-python/)
- [Quarto for the Python user (Jumping Rivers)](https://www.jumpingrivers.com/blog/quarto-for-python-users/)
