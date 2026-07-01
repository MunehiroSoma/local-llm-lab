# ADR 0005: AI-DLC（AI駆動開発ライフサイクル）を採用（単独開発向けに軽量化）

- ステータス: accepted
- 日付: 2026-07-01

## 背景
AIエージェント主導で開発する。AWS の AI-DLC（Inception/Construction/Operations・
Mob Elaboration・BOLT・人間承認ゲート・ドキュメント先行）を導入したい。

## 決定
AI-DLC の**原則**を採用し、本リポジトリの GitHub Flow ＋ ai-dev-kit ＋ 評価ハーネスへ写像する（[AGENT.md](../../AGENT.md)）。
- 3フェーズ = Inception(計画/Issue) → Construction(実装/PR) → Operations(運用/results)。**各遷移に人間承認ゲート**。
- BOLT = 短命ブランチ。Unit of Work = (モデル×環境×評価) or harness機能。
- ハット = ai-dev-kit スキル ＋ ラボ固有役割（fit / speed / eval / review）。
- ドキュメント先行 = research / ADR / results を一次資産に。

## スコープ（今回の構成でできる範囲）
- ✅ **できる**: ドキュメント先行、フェーズ・ゲート運用、BOLT=ブランチ、Issue/PRゲート、ADR、
  ai-dev-kit スキル、継続評価(results追記)、モデル・オンボーディングの型化。
- 〜 **部分的**: 「Mob」は単独のため「人間＋AIのペア」に縮約。Operations はローカル運用
  （推論サーバ + eval ループ）に限定。
- ❌ **対象外**: AWS 固有ツール(Amazon Q)前提の自動化、クラウド大規模 IaC デプロイ。
  必要なら `awslabs/aidlc-workflows` の steering rules を任意で採用。

## 影響
`AGENT.md`, `docs/conventions.md`(AI-DLC節), Issue テンプレ, ブランチ/PR規約。
