# Web / GUI コーディング規約

- Version: 1.0 / 作成: 2026-07-02
- 対象: Streamlit / Gradio による Web ダッシュボード・GUI 実装（ADR 0007 Phase B 以降）
- 本ページは **Web/GUI 実装固有のルールのみ**を扱う。Python 一般の規約は [`python.md`](python.md) を継承する
  （ruff/mypy・命名・型ヒント・エラーハンドリング等はそのまま適用）。
- 関連: ADR 0007（技術選定） / [`review-checklist/07-web-security.md`](review-checklist/07-web-security.md)

## 適用条件
Streamlit / Gradio 等の Web/GUI コードを追加・変更する PR にのみ適用する。
`harness/` `scripts/` 等の非GUIコードには適用しない。

## バインド先・公開範囲
- **開発・単独利用時は `127.0.0.1`（localhost）に明示バインドする。** `0.0.0.0` での起動は禁止。
  - Streamlit: `streamlit run app.py --server.address=127.0.0.1`
  - Gradio: `demo.launch(server_name="127.0.0.1")`
- **LAN/外部公開が必要な場合は認証必須**（Streamlit の認証機能、リバースプロキシでの Basic認証等）。
  無認証での LAN 公開は禁止（本ラボの推論サーバに関する CI/CD 総点検資料 §E-7 と同じ理由:
  認証なしのサーバは誰でも操作できてしまう）。
- 公開範囲の変更（127.0.0.1 → LAN/外部）は ADR 相当の重い変更として扱い、
  レビュー時に必ず確認する（[`review-checklist/07-web-security.md`](review-checklist/07-web-security.md)）。

## UI とロジックの分離
- ビジネスロジック・データ集計・harness 呼び出しは `harness/` 側に置き、GUI コード（`app.py` 等）から
  import して使う。GUI ファイルに集計/推論ロジックを直接書かない。
- GUI 層の責務は「入力の受け取り・`harness/` の呼び出し・結果の描画」のみに限定する。
- これにより GUI なしでも `harness/` 単体でテスト・CLI 実行できる状態を保つ。

## state 管理（Streamlit）
- 画面間・再実行間で保持したい状態は `st.session_state` を明示的に使う。
  グローバル変数での状態保持は禁止（Streamlit はスクリプト全体を再実行するモデルのため、
  グローバル変数は意図せずリセットされる／共有セッション間で汚染される）。
- `session_state` のキー名は衝突を避けるため、機能プレフィックスを付ける（例: `report_selected_model`）。

## 秘密情報の管理
- API キー等の秘密は `st.secrets`（`.streamlit/secrets.toml`, gitignore対象）または `.env` で管理する。
  コード中へのハードコード禁止（[`python.md`](python.md) のセキュリティ規約を継承）。
- `.streamlit/secrets.toml` を `.gitignore` に追加すること（実装時に忘れやすいため review 時に確認）。

## ユーザー入力の描画（XSS）
- `st.markdown(..., unsafe_allow_html=True)` や `st.write` にユーザー入力・外部データを
  そのまま渡さない。HTML を許可する描画には必ずサニタイズを通す。
- `results.csv` の `notes` 列等、外部/過去データ由来の文字列を描画する場合も同様に扱う
  （自分専用ラボであっても、レポート共有時に他者が開く可能性を考慮する）。

## a11y（アクセシビリティ）・UI一貫性
- チャート実装時は `dataviz` スキルの色・形式規約に従う（色のみに依存しない、コントラスト確保）。
- 同一アプリ内でのラベル・ボタン文言・レイアウトパターンは既存画面と揃える
  （初期実装時点では強制力のあるルールは設けず、レビュー時の目視確認とする）。

## 依存関係
- Streamlit/Gradio/Plotly/kaleido 等の追加は `pyproject.toml` の `viz` optional-dependencies
  グループに追加し、バージョンピンする（ADR 0007）。追加時は CI/CD レビュー資料 C-1・C-5
  （実在確認・メンテ状況確認）を先に済ませる。
