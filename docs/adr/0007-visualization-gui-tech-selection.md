# ADR 0007: 可視化/GUI 技術選定（Phase A 静的レポート方針）

- ステータス: accepted
- 日付: 2026-07-03
- 入力: [`docs/research/2026-07-02-webapp-gui-visualization-study.md`](../research/2026-07-02-webapp-gui-visualization-study.md)
- 関連: #35（results集計→reports自動生成）, #40, #42（GUI検証プラグイン整備）

## 背景 / 課題

将来「Web画面/GUI操作で results をグラフ確認し、md / pdf / csv で出力する」構想がある。
research ノートでは段階アーキテクチャとして、Phase A: 静的レポート、Phase B: Webダッシュボード、
Phase C: スタンドアロンを棚卸しした。

ただし現時点で必要なのは、Issue #35 が着手できるだけの Phase A 方針である。Phase B/C の詳細技術を
先に決めると、まだ存在しない UI 要件に引きずられて #35 の実装が重くなる。したがって本ADRでは
`results/results.csv` から再現可能な静的レポートを生成する方針だけを accepted とする。

## 決定

### Phase A: 静的レポート生成

`results/results.csv` を入力にして、比較表とチャートを含むレポートをバッチ生成する。GUIは持たない。

出力先は既存の `results/reports/` とする。`results/raw/` はローカル証跡専用であり、レポート生成の入力に
しない。

### Quarto vs Jinja2 + Plotly

Phase A の第一候補は **Quarto** とする。

理由:

- 1つの `.qmd` から HTML / Markdown / PDF を生成できる。
- Python 実行、表、Plotly 図、静的文書の組み合わせを既製の文書生成フローで扱える。
- Jinja2 + Plotly の自前テンプレートより、目次・メタデータ・複数形式出力・PDF 経路の保守負担が小さい。

Jinja2 + Plotly は採用しない。Quarto が導入できない環境、または #35 の最小実装で Quarto CLI を固定する
コストが過大と判明した場合だけ、後続ADRまたは #35 の実装判断で再検討する。

### HTML / PDF の二層方針

HTML と PDF は同じ見た目・同じ操作性を目指さない。

- HTML: Plotly のインタラクティブ図を許可する。
- PDF: 静的画像化した図を埋め込む。Plotly 図を使う場合は `kaleido` で画像化する。
- Markdown: PR や research note に貼れる静的な要約・表を主用途とする。

PDF 生成は Typst 経由を既定候補とする。LaTeX 前提にはしない。

### 版固定と生成物メタデータ

レポート生成も eval と同じく再現性の対象に含める。

Phase A の生成物には、少なくとも次を刻印する。

- 入力データ: `results/results.csv`
- 入力データの範囲: 全件、または抽出条件
- 生成時の git commit SHA
- 生成日
- レポート生成コマンド
- 使用した主要ツールのバージョン（Quarto / Python / Plotly / kaleido など）

Quarto CLI と Python パッケージのバージョンは、導入時に runbook または `pyproject.toml` / lockfile 側で固定する。

### Issue #35 の実装境界

#35 は次の最小実装に絞る。

- `results/results.csv` を読み込む。
- model / runtime / env / profile ごとの代表値を集計する。
- `tok_s`, `ttft_ms`, `std_bench`, `task_score` の比較表を生成する。
- 少なくとも1つのチャートを生成する。
- 生成物に commit SHA と入力データ情報を刻印する。
- `results/raw/` を入力にも出力にも使わない。
- `results/results.csv` の append-only ルールを変更しない。

Phase A では Webサーバ、GUI操作、リアルタイム更新、認証、ユーザー管理、スタンドアロン配布を実装しない。

### Phase A の report-gen スキル方針

#35 の実装後、`make report-results` と `python3 -m harness.reporting.results_summary` が
Phase A の標準コマンドになった。#42 では新しいレポート生成エンジンを増やさず、既存コマンドを
定型化する薄い `report-gen` スキルを追加する。

`report-gen` は読み取り専用の運用スキルであり、次を必須ルールにする。

- 入力は `results/results.csv` のみとし、`results/raw/` を入力にしない。
- `results/results.csv` を変更しない。WhichLLM の候補抽出やレポート生成だけでは
  `results.csv` に追記しない。
- 生成物は `results/reports/` に置き、commit SHA、入力パス、入力範囲、生成日、生成コマンド、
  主要ツール版を刻印する。
- `record-results` の人間承認ゲートを迂回しない。

### Phase B の Playwright MCP 方針

Playwright MCP は Phase A の静的レポート生成には導入しない。Phase B で
React + TypeScript + Vite の Web UI 実装を開始し、ブラウザ操作を伴う E2E 検証が必要になった時点で
導入候補にする。

Phase B では Tailwind CSS を前提に UI を実装し、ESLint / Prettier / TypeScript typecheck とあわせて
Playwright を E2E 検証候補として接続する。導入時は `web/` 側の frontend tooling として管理し、
Python 側の ruff / mypy / pre-commit とは責務を分ける。

## 理由 / 代替案

### Jinja2 + Plotly

却下。柔軟だが、テンプレート構造、複数形式出力、PDF 変換、メタデータ埋め込みを自前で保守する必要がある。
Phase A の目的は可視化基盤を作り込むことではなく、results から再現可能な代表レポートを出すことである。

### Streamlit / Gradio / Dash / React

Phase A では採用しない。これらは GUI または Web アプリの選択肢であり、#35 の静的レポート生成には不要。
Phase B の要件が具体化した時点で、別ADRまたは本ADRの改訂で比較する。

### Tauri / Electron

Phase A では採用しない。スタンドアロン配布の署名、更新、ビルド運用は現時点の課題ではない。Phase C が
必要になった時点で再検討する。

## 影響

- #35 は本ADRに従い、静的レポート生成の最小実装として進める。
- `results/reports/` に生成物を置く場合、生成物だけを見ても入力データと commit SHA が分かるようにする。
- `results/results.csv` は引き続き append-only とし、レポート生成は既存データの読み取り専用処理にする。
- `results/raw/` は引き続き commit しない。
- Phase B のフロントエンド標準は React + TypeScript + Vite + Tailwind CSS とする。Playwright MCP は
  Phase B UI 実装開始時の E2E 検証候補として扱い、Phase A には持ち込まない。
