# コードレビューチェックリスト（共通 + Python）

> PRごとに使用。Must が全て ✓ になり NG 件数が 0 になってから Approve する。
> 区分「自動」は pre-commit / CI が green であればスキップ可。「手動」は必ず目視確認。
> 関連規約: [`python.md`](python.md) / ADR 0004 / ADR 0006（観点分割の背景）

**PR番号/URL**: ＿＿＿＿　**レビュー対象**: ＿＿＿＿　**レビュアー**: ＿＿＿＿　**レビュー日**: ＿＿＿＿

---

## 観点カテゴリ

`review` スキルは以下の観点ごとにサブエージェントを並列起動し、各エージェントは担当ファイルのみを読む。

| 観点 | チェックリスト | 入力範囲 | 想定モデル |
|---|---|---|---|
| 基本品質 | [`review-checklist/01-basic-quality.md`](review-checklist/01-basic-quality.md) | 差分のみ | 軽量 |
| エラー処理 | [`review-checklist/02-error-handling.md`](review-checklist/02-error-handling.md) | 差分のみ | 軽量 |
| セキュリティ | [`review-checklist/03-security.md`](review-checklist/03-security.md) | 差分のみ | 上位 |
| テスト | [`review-checklist/04-test.md`](review-checklist/04-test.md) | 差分のみ | 軽量〜中位 |
| 設計整合性 | [`review-checklist/05-design-consistency.md`](review-checklist/05-design-consistency.md) | 差分 + ADR/研究ノート | 上位 |
| harness-eval-registry | [`review-checklist/06-harness-eval-registry.md`](review-checklist/06-harness-eval-registry.md) | 差分のみ（registry変更時はADRも） | 上位 |
| Webセキュリティ（条件付き） | [`review-checklist/07-web-security.md`](review-checklist/07-web-security.md) | 差分のみ | 上位 |
| データ操作・リソース管理 | [`review-checklist/08-data-operations.md`](review-checklist/08-data-operations.md) | 差分のみ | 上位 |
| 外部API連携 | [`review-checklist/09-external-api.md`](review-checklist/09-external-api.md) | 差分のみ | 上位 |
| CI/CD・サプライチェーン（条件付き） | [`review-checklist/10-cicd-supply-chain.md`](review-checklist/10-cicd-supply-chain.md) | 差分のみ | 上位 |
| インフラ・コンテナ（条件付き） | [`review-checklist/11-infra-container.md`](review-checklist/11-infra-container.md) | 差分のみ | 上位 |

条件付き観点は常時起動せず、差分の内容に応じて起動する（下表）。

| 観点 | 起動条件 |
|---|---|
| Webセキュリティ / UI | React(`web/`)/FastAPI 等の Web/GUI 実装を含む差分のとき（ADR 0007 Phase B以降） |
| CI/CD・サプライチェーン | `.github/workflows/` の変更、または依存関係（`pyproject.toml`/`uv.lock`/`web/package.json`等）の追加・更新を含む差分のとき |
| インフラ・コンテナ | `envs/` の Docker/compose 実装を含む差分のとき |

観点特化エージェントのノイズ抑制ルール・読み取り専用権限・出力フォーマットは
[`.claude/skills/review/SKILL.md`](../../.claude/skills/review/SKILL.md) を参照。

---

## PRメタ確認（観点分割の対象外・人間が直接確認）

pre-commit/CI で機械化しにくい運用ルールのため、AIレビュー観点には含めず本チェックリストで直接確認する。

| No | カテゴリ | チェック項目 | 区分 | 重要度 | チェック | 備考 |
|---|---|---|:---:|:---:|:---:|---|
| 1 | PR運用 | PRの説明に背景・変更内容・テスト方法が記載されている | 手動 | Should | | |
| 2 | PR運用 | PRが1つの目的に絞られている（1 BOLT = 1 PR） | 手動 | Should | | |

---

## チェック結果サマリ

| 区分 | 件数 |
|---|---|
| Must — NG | |
| Should — NG | |
| Nits — 指摘 | |
| **マージ可否** | Must NG=0 かつ CI green → **Approve 可** |
