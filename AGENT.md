# AGENT.md — local-llm-lab エージェント運用ガイド

AIエージェント（Claude Code / Cursor / Copilot 等）が本リポジトリで作業する際の規範。
人間向けは [README](README.md) / [CONTRIBUTING](CONTRIBUTING.md)、決定は [docs/adr](docs/adr/)、
詳細規約は [docs/conventions.md](docs/conventions.md)。

## プロジェクト
自分のハード群（Mac M4 Pro / RTX 5060 Ti / RTX 5070 / DGX Spark）で、ローカルLLM・
マルチモーダル(omni)推論の「フレームワーク選定 → モデル比較 → PoC → 継続評価」を行うラボ。
原典: [`docs/research/local-llm-multimodal-study.md`](docs/research/local-llm-multimodal-study.md)。

## 開発方式: AI-DLC（AI駆動開発ライフサイクル）＋ GitHub Flow
AWS の **AI-DLC** を単独開発向けに軽量化して採用（ADR 0005）。
中核: **ドキュメント先行・フェーズゲート・人間承認・短いBOLT・ハット(役割)**。

### 3フェーズ（各遷移に人間承認ゲート）
| フェーズ | 本ラボでの意味 | 生成物 | ゲート(人間承認) |
|---|---|---|---|
| **Inception**（意図→計画 / Mob Elaboration） | 何を評価/実装するか。モデル追加計画・評価設計 | Issue(model-onboarding) / ADR / research 更新 | **計画Issueを承認してから着手** |
| **Construction**（設計→実装→テスト） | harness実装・eval設定・実験(BOLT)実行 | `harness/` `envs/` PR / results | **PRレビュー+pre-commit+テスト通過** |
| **Operations**（運用・継続検証） | サーバ運用(`envs/`/runbooks)・results追記・回帰検知 | `results/` reports / タグ | **結果受け入れ承認 → モデル採用** |

### BOLT / Unit of Work
- 1 BOLT = 短命ブランチ（`exp/*` `model/<id>` `feat/*`）で数時間〜1日。
- Unit of Work = 「1(モデル×環境×評価)」または「harness の1機能」。

### ハット(役割) = スキル / サブエージェント
- ai-dev-kit スキル: `start` `new-feature` `create-issue` `sync-main` `ship` `review` `test-check` `long-run`。
- ラボ固有の役割: **fit-tester / speed-bencher / eval-author / reviewer**（Claude Code サブエージェント可）。

## 鉄則（ガードレール）
1. **人間承認なしにフェーズを進めない**（Inception→Construction→Operations）。
2. **`datasets/golden/` に実データを入れない**（公開リポ。samples のみ）。
3. **push / PR / 破壊的操作は人間の指示があるときのみ**。`main` へ直 push しない。
4. **`results/results.csv` は追記のみ**。judge モデル・ゴールデンセット版は固定。
5. 決定は ADR に、根拠は `research/` に残す（ドキュメント先行）。

## 標準フロー（1 BOLT）
1. **Inception**: `create-issue` で計画を粒度化 → 人間承認
2. `new-feature`（`main` からブランチ）
3. **Construction**: 実装/実験 → `test-check`
4. `pre-commit run --all-files`
5. `ship`（commit[Conventional Commits] → push → PR）→ `review` → squash merge（人間承認）
6. **Operations**: `results/` 追記・回帰確認

## コマンド
| 目的 | コマンド |
|---|---|
| 環境確認 | `bash scripts/check_env.sh` |
| 候補モデル抽出 | `bash scripts/whichllm_scan.sh <profile>` |
| 検証 | `make validate` / `pre-commit run --all-files` |
| ヘルプ | `make help` |

## 参考
- AWS AI-DLC: https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/
- awslabs/aidlc-workflows: https://github.com/awslabs/aidlc-workflows ／ https://ai-dlc.dev/
