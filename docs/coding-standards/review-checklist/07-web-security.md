# 観点: Web セキュリティ

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**（既存実装への指摘はしない）。
> 想定モデル: 上位モデル（誤検知コストが高いため）。
> **起動条件: Streamlit/Gradio 等の Web/GUI 実装を含む差分のときのみ起動する**（ADR 0007 Phase B以降）。
> 関連規約: [`web-gui.md`](../web-gui.md)

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | サーバのバインド先が `127.0.0.1` に明示されている（`0.0.0.0` になっていない） | 手動 | Must | `web-gui.md` §バインド先 |
| 2 | LAN/外部公開する場合に認証が設定されている | 手動 | Must | `web-gui.md` §バインド先 |
| 3 | ユーザー入力・外部データを `unsafe_allow_html=True` 等で無サニタイズ描画していない（XSS） | 手動 | Must | `web-gui.md` §XSS |
| 4 | API キー等の秘密が `st.secrets` / `.env` 経由で管理され、コードに直書きされていない | 手動 | Must | `.streamlit/secrets.toml` が `.gitignore` 対象か確認 |
| 5 | GUI 層（`app.py` 等）に集計/推論ロジックを直接書かず `harness/` から import している | 手動 | Should | `web-gui.md` §UIとロジックの分離 |
| 6 | 状態管理が `st.session_state` を使い、グローバル変数で状態保持していない | 手動 | Should | `web-gui.md` §state管理 |
| 7 | 依存追加（streamlit/gradio/plotly/kaleido等）が `viz` optional-dependencies にバージョンピンされている | 手動 | Should | ADR 0007 |

> 自動区分は pre-commit/CI が green であればスキップ可（現時点で Web/GUI 固有の自動チェックは未整備）。
