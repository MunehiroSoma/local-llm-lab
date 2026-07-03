# WhichLLM coding profile 実行結果（2026-07-03）

## 目的

Issue #36 のため、現マシンで WhichLLM / LLM Checker 相当の候補抽出を行い、次に
onboarding すべき coding モデル候補と既存 issue の関係を整理する。

## 実行環境

- 実行日: 2026-07-03
- 実行マシン: MacBook Pro M4 Pro
- 検出GPU: Apple M4 Pro, 48.0 GB shared, budget 46.0 GB
- CPU: Apple M4 Pro, 14 cores
- RAM: 48.0 GB
- OS: darwin
- WhichLLM: `whichllm==0.5.14`（`@latest` は未使用）

raw log は `results/raw/2026-07-03-whichllm-*.txt` に保存した。`results/raw/` はローカル証跡のみで
commit しない。

## 実行コマンド

```bash
bash scripts/whichllm_scan.sh coding
bash scripts/whichllm_scan.sh summarize
bash scripts/whichllm_scan.sh vision
```

`summarize` は WhichLLM 0.5.14 の有効 profile ではなかった。有効 profile は
`general`, `coding`, `vision`, `math`, `any`。

## coding profile 結果

`make whichllm PROFILE=coding` 相当として、固定版スクリプト `bash scripts/whichllm_scan.sh coding` を実行した。

| rank | model | quant | fit / VRAM | speed | published | score | repo との対応 |
|---:|---|---|---|---|---|---:|---|
| 1 | `Qwen/Qwen3-Coder-30B-A3B-Instruct` | Q8_0 | Full GPU / 31.6 GB | 31.6 tok/s ? | 2025-07-31 | 83.7 | #63 で onboarding 済み |
| 2 | `rafw007/qwen36-a3b-claude-coder-llama.cpp-GGUF` | Q4_K_M | Full GPU / 20.2 GB | 73.0 tok/s ? | 2026-06-07 | 56.3 ~ | #27 の `qwen3.6-35b-a3b` と近いが、公式/配布元確認待ちのため blocked 継続 |
| 3 | `yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF` | Q3_K_M | Full GPU / 6.9 GB | 21.5 tok/s ~ | 2026-06-10 | 49.8 ~ | #26 は `gemma4-12b` だが coding 派生 GGUF ではない。別候補として扱う |
| 4 | `jica98/qwen3.5-4B-super-coder` | Q4_0 | Full GPU / 3.4 GB | 54.8 tok/s ~ | 2026-06-13 | 46.4 ~ | 既存 issue なし |
| 5 | `Qwen/Qwen2.5-Coder-7B-Instruct` | Q4_K_M | Full GPU / 5.6 GB | 28.7 tok/s ~ | 2024-09-17 | 38.8 | 既存 issue なし |

WhichLLM の出力上、Top pick confidence は Medium。#1 は direct benchmark だが speed は low-confidence、
#2/#3 は benchmark evidence が弱いという注意が出ている。

## vision profile 結果

VLM 相当として `bash scripts/whichllm_scan.sh vision` を追加実行した。

| rank | model | quant | fit / VRAM | speed | published | score | repo との対応 |
|---:|---|---|---|---|---|---:|---|
| 1 | `microsoft/Phi-3-vision-128k-instruct` | Q5_K_M | Full GPU / 4.0 GB | 40.8 tok/s ~ | 2024-05-19 | 17.9 ? | 既存 issue なし |
| 2 | `BennyDaBall/Z-Image-Engineer-V6-GGUF` | Q5_K_M | Full GPU / 3.9 GB | 42.1 tok/s ~ | 2026-06-06 | 17.7 ? | 既存 issue なし |

vision profile は direct benchmark data がなく、Top pick confidence は Low。#28 の `qwen2.5-vl-7b` は
この実行では上位候補に出ていないが、repo では VLM baseline として別途 open のまま扱う。

## 次に onboarding すべき候補

1. `Qwen/Qwen3-Coder-30B-A3B-Instruct` は #63 で onboarding 済みのため、新規 issue は不要。
2. `qwen3.6-35b-a3b` 系は WhichLLM coding #2 だが、#27 の公式/配布元確認 blocker が残る。
   blocker 解消後に #27 を再開する。
3. `gemma-4-12B-coder-fable5-composer2.5-v1-GGUF` は #26 の `gemma4-12b` とは別物として扱う。
   採用するなら #26 へ混ぜず、coding 派生候補として別 issue 化する。
4. 小型 coding 候補として `jica98/qwen3.5-4B-super-coder` と `Qwen/Qwen2.5-Coder-7B-Instruct` は
   Mac で軽量に載る候補だが、既存の #63/#65/#29 完了済み候補より優先する根拠はまだ弱い。

## blocker / 未実行範囲

- RTX 5060 Ti, RTX 5070, DGX Spark はこの実行環境から触れないため未実行。
- `summarize` profile は WhichLLM 0.5.14 に存在しないため未実行。必要なら `general` または `any` で
  代替する。
- WhichLLM は候補抽出であり、Fit / Speed / Layer 3 / Layer 4 評価ではない。したがって
  `results/results.csv` には追記しない。
- `results/raw/` はローカル証跡のみで commit しない。
