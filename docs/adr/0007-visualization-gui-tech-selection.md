# ADR 0007: 可視化/GUI 技術選定（Phase A 静的レポート方針 + 検証ツール方針）

- ステータス: accepted
- 日付: 2026-07-02
- 入力: [`docs/research/2026-07-02-webapp-gui-visualization-study.md`](../research/2026-07-02-webapp-gui-visualization-study.md)
- 関連: #35（results集計→reports自動生成）, #40, #42

## 背景 / 課題
「Web画面/GUI操作でresultsをグラフ確認し、md/pdf/csvで出力する」構想について、
research ノートで段階アーキテクチャ（Phase A: 静的レポート → Phase B: Webダッシュボード →
Phase C: スタンドアロン）の技術棚卸しを実施済み。本ADRで全体方針を確定し、
Issue #35（Phase A の実装）を着手可能にする。

あわせて Issue #42（GUI検証プラグイン・report-genスキルの要否）もこのADRで決定する
（research §7 で「ADR または research ノートに記録」とされている軽量な決定のため、
別ADRに分けずここに含める）。

## 決定

### Phase A: 静的レポート生成（GUIなし・最小コスト）— 本命: Quarto
- `.qmd` 1ソースから html / md / pdf を多形式出力する **Quarto** を採用する。
- 代替案の Jinja2 + Plotly 自前テンプレートは**却下**（車輪の再発明。Quarto で要件を満たせない
  局面が出た場合にのみ再検討する）。
- **pdf 出力は二層方針で固定する**: html はインタラクティブ（Plotly埋め込み可）、
  pdf は静的画像（kaleido で Plotly 図を画像化して埋め込み）。最初からこの前提で実装し、
  後から pdf 用に図を作り直す手戻り（research §6-3）を避ける。
- pdf 変換経路は Typst 経由（LaTeX 不要）を既定とする。

### Phase B: Web ダッシュボード（GUI操作）— Streamlit 主 / Gradio 併用
- ダッシュボード用途（results確認・比較チャート・実行指示UI）は **Streamlit** を第一候補とする。
- モデルとの対話UI（チャット等）が必要になった時点で **Gradio** を併用する。
- 両方 Python 一枚岩で完結させ、既存の ruff/mypy 規約をそのまま適用する。
- JS フロントエンド（React等）は「Python系で表現できないUI要求」が具体的に出るまで採用しない
  （規約・CI・レビュー観点が丸ごと一式増えるため）。

### Phase C: スタンドアロンアプリ — 見送り
- Tauri / Electron は採用しない。ビルド・署名・更新配布の運用コストが単独ラボの
  費用対効果に見合わない。
- Streamlit をローカル起動し `localhost` をブラウザで開く運用が実質的にスタンドアロンとして
  機能するため、Phase B で代替できる。判断は先送りではなく **不採用として確定**する
  （必要性が具体的に生じた場合のみ本ADRを再訪する）。

### レポート生成ツールの版固定規約
- judge モデル・ゴールデンセット版の固定方針（`docs/conventions.md`）と同じ思想を
  レポート生成ツールにも適用する。
- Quarto CLI のバージョンと `kaleido` パッケージのバージョンを固定し、
  `envs/` のセットアップ手順（runbook）に明記する。
- 生成物（html/md/pdf）には、元データの版（`results.csv` の対象範囲、または
  `results-YYYYMMDD` タグ）と、生成時のコミットSHAを埋め込む（フッター等）。
  これにより過去レポートの再現・検証が可能になる。

### Issue #35 実装方針との整合
- `results.csv` → Quarto バッチ生成（Phase A）で実装する。GUI要素は持たない。
- 出力先は既存の `results/reports/`。
- 実装着手前に `results.csv` の列を JSON Schema 化しておくことを推奨する
  （#45 で対応。可視化がスキーマレスなCSVに依存すると壊れやすいため、可視化実装より先が望ましい）。

### GUI検証ツール（Playwright MCP）— Phase B 開始時に導入
- Streamlit/Gradio 起動確認・ブラウザ自動操作によるGUI E2E検証に **Playwright MCP** を採用する。
- Phase A（GUIなし）では不要なため、**導入は Phase B 着手時点**とする。今は方針決定のみ。
- Phase B の `review` / `verify` スキル実行時に Playwright MCP 経由のブラウザ操作を組み込む
  余地を残す。

### report-gen スキル（仮称）— Phase A 実装後に新設する
- `results.csv` → md/pdf/csv 一括生成の定型手順は、既存スキルの拡張ではなく
  **新規スキルとして切り出す**（Issue #35 の実装完了後）。
- 理由: レポート生成はツール版固定・生成物へのSHA刻印など独自の手順・規約を持つ反復作業であり、
  `record-results`（Operations フェーズの結果追記・採否判断）とは責務が異なる。
  `record-results` の直後に呼ぶ形で接続する。
- 新設タイミングは Issue #35 実装後の別Issueとする（本ADRでは方針決定のみ）。

## 理由 / 代替案
- Jinja2 + Plotly（自前）: 却下。Quarto が同等以上の要件（多形式出力・pdf変換）を
  既製品として満たすため、自前実装の保守コストを避ける。
- Dash: 過剰（研究ノート比較表参照）。単独開発・Python一枚岩の要件に対してオーバースペック。
- marimo: 情報が少なく様子見。Phase B 開始時点で Streamlit が要件を満たせない場合の代替候補として
  記録のみ残す。
- Tauri/Electron: 上記「Phase C」参照。

## 影響
- `pyproject.toml` に `viz` optional-dependencies グループを追加する際は本ADRの技術選定に従う
  （`plotly` / `kaleido` / `streamlit`。追加時は CI/CDレビュー資料 C-1・C-5 の確認が先）。
- `results/reports/` の生成物にデータ版・コミットSHAを刻印するルールが今後の実装で必須になる。
- Issue #41（Web/GUI向け規約）は本ADRの Phase B 決定（Streamlit/Gradio採用）を前提に規約を書く。
- Issue #35 は本ADRの Phase A 決定（Quarto・二層pdf方針）に沿って実装する。
