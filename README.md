# local-llm-lab

自分のハードウェア群で、ローカル LLM・マルチモーダル/omni 推論の **フレームワーク選定 → モデル比較 → 実証(PoC) → 継続評価** を回すためのラボ。

- **用途（すべて単発・自分専用）**: コーディングエージェント / AIコンシェルジュ / 要約・タグ付け
- **対象4環境**: ① Mac M4 Pro 48GB ／ ② i7-14700 + RTX 5060 Ti 16GB ／ ③ i9-14900K + RTX 5070 12GB ／ ④ NVIDIA DGX Spark 128GB
- **設計方針**: OpenAI互換APIで抽象化し、**モデル/ランタイムを差し替え自由**に（`registry/` + `docs/adr/`）。評価は **「載る→速い→賢い→自分の用途で良い」の4階層**（`docs/research/`）。

## クイックスタート

```bash
# 1) 環境確認（このマシンのGPU/RAM/ランタイム）
bash scripts/check_env.sh

# 2) 候補モデルの機械的な当たり付け（WhichLLM）
bash scripts/whichllm_scan.sh          # uvx whichllm@latest --profile coding 等

# 3) 評価ハーネス（今後実装）
make help
```

## リポジトリ構成

| パス | 役割 |
|---|---|
| `docs/research/` | 調査・設計書（本ラボの原典） |
| `docs/adr/` | 意思決定記録（Architecture Decision Records） |
| `docs/runbooks/` | 環境別セットアップ手順（mac / wsl2-rtx / dgx-spark） |
| `registry/` | **モデル・ハードのレジストリ**（`models.yaml` / `hardware.yaml`） |
| `envs/` | 環境別の起動設定（vLLM/-Omni compose、MLX/Ollama 等） |
| `harness/` | 評価ハーネス（fit / speed / capability / task） |
| `datasets/golden/` | 自前ゴールデンセット（**private=gitignore**、samplesのみ公開） |
| `results/` | 計測結果（スキーマ固定・追記で時系列比較） |
| `scripts/` | 補助スクリプト |

## ワークフロー（GitHub flow）

- `main` は常にグリーン。作業はブランチ: `feat/*` `exp/*` `model/<name>` `docs/*` `env/*` → PR → レビュー → squash merge。
- **新モデル追加** = `registry/models.yaml` に1行 → model-onboarding Issue のチェックリスト → `results/` に追記（`docs/adr/` の設計原則参照）。

## ステータス

設計フェーズ完了 → PoC 着手前。原典: [`docs/research/local-llm-multimodal-study.md`](docs/research/local-llm-multimodal-study.md)

## ライセンス

MIT（`LICENSE`）。※調査対象モデルのライセンスは各モデルに従う（本ラボ運用上は考慮外）。
