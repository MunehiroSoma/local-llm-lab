# lfm2.5-1.2b-jp-202606 onboarding record

Parent issue: #4
Model issue: #62
Date: 2026-07-02
Environment: `mac`

## Registry and runtime

- Registry id: `lfm2.5-1.2b-jp-202606`
- Source repo: `LiquidAI/LFM2.5-1.2B-JP-202606`
- Source repo HEAD: `52b8b4475311a63bf839c6494f78f8ad59d13515`
- Runtime repo: `LiquidAI/LFM2.5-1.2B-JP-202606-GGUF`
- Runtime revision: `8c74801fdfe71394c59d3f519b86de305ff49f00`
- Runtime model: `hf.co/LiquidAI/LFM2.5-1.2B-JP-202606-GGUF:Q4_K_M`
- Local Ollama alias: `lfm2.5-1.2b-jp-202606`
- Ollama model id: `cb967c9bd843`
- Quantization: `Q4_K_M`
- Ollama reported context length: `128000`
- Registry max_model_len for this run: `32768`

## Commands

```bash
ollama pull hf.co/LiquidAI/LFM2.5-1.2B-JP-202606-GGUF:Q4_K_M
ollama cp hf.co/LiquidAI/LFM2.5-1.2B-JP-202606-GGUF:Q4_K_M lfm2.5-1.2b-jp-202606
python3 -m harness.run_onboarding \
  --model lfm2.5-1.2b-jp-202606 \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --profile summarize \
  --quantization q4_k_m \
  --revision 8c74801fdfe71394c59d3f519b86de305ff49f00 \
  --max-model-len 32768 \
  --max-tokens 128 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 180
```

## Layer results

| Layer | Status | Result |
|---|---|---|
| 1 Fit | done | `fit=yes` through Ollama OpenAI-compatible API |
| 2 Speed | done | median `tok_s=237.348`, median `ttft_ms=53.5736` |
| 3 Standard benchmark | done | `llm-jp-eval-jcommonsenseqa-full-v2.1.5=0.743521`; 832 / 1119 correct |
| 4 Custom task evaluation | done | `summary-tags-public-v1=0.484444`; pass `0/3` |

## Proposed results row

This preliminary row was not appended because Layer 3/4 were still open at the time.

```csv
lfm2.5-1.2b-jp-202606,8c74801fdfe71394c59d3f519b86de305ff49f00,ollama,mac,summarize,q4_k_m,yes,32768,237.348,53.5736,,,,,2026-07-02,onboarding fit+speed; ollama_id=cb967c9bd843
```

## Verdict

Hold for now. Fit and speed are strong on Mac, but standard benchmark, custom task evaluation, results append, and Operations acceptance are still open.

## 2026-07-03 Layer 3/4 follow-up

#62 の残り作業として、MacBook Pro 上の Ollama endpoint で Layer 3 と Layer 4 を実測した。

Layer 3 は #64 と同じ標準ベンチ条件に合わせ、公式 `llm-jp-eval` v2.1.5 の `jcommonsenseqa` test full
split を実行した。

- Tool: `llm-jp-eval` v2.1.5, commit `5067fe7bcd33797643835573505d5ec06858ea34`
- Dataset: `jcommonsenseqa`
- Split: `test`
- Samples: 1119
- Setting: full split, `max_num_samples=-1`, 4-shot dataset default
- Metric: `exact_match`
- Score: `0.743521000893655`
- Correct / total: `832 / 1119`
- Wrong: `287`
- Raw: `results/raw/2026-07-03-lfm2.5-1.2b-jp-202606-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`
- Report: `results/reports/2026-07-03-lfm2.5-1.2b-jp-202606-onboarding.md`

Layer 4 は公開可能な架空サンプルだけを使う `summary-tags-public-v1` golden task set と固定
`deterministic-marker-rubric-v1` で実行した。

- Task set: `datasets/golden/samples/summary-tags-public-v1.yaml`
- Runner: `harness.task.promptfoo.summary_tags_eval`
- Score: `0.48444433333333337`
- Passed / total: `0 / 3`
- Median tok/s: `243.0804970364031`
- Median TTFT: `130.639709001116 ms`
- Raw: `results/raw/2026-07-03-lfm2.5-1.2b-jp-202606-summary-tags-public-v1.json`
- Report: `results/reports/2026-07-03-lfm2.5-1.2b-jp-202606-onboarding.md`

`harness.run_onboarding` で生成した final/revised row candidate:

```csv
lfm2.5-1.2b-jp-202606,8c74801fdfe71394c59d3f519b86de305ff49f00,ollama,mac,summarize,q4_k_m,yes,32768,225.426,57.7791,,0.743521,0.484444,,2026-07-03,reject; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; task=summary-tags-public-v1; judge=deterministic-marker-rubric-v1; pass=0/3; ollama_id=cb967c9bd843; raw=2026-07-03-lfm2.5-1.2b-jp-202606-onboarding-final-row.json
```

この row は Operations approval gate 未承認のため、まだ `results/results.csv` には追記していない。

Verdict proposal: `reject`. Fit/Speed は Mac/Ollama で良好だが、Layer 3 は同条件の
`llm-jp-4-8b-instruct` baseline より低く、Layer 4 は JSON schema は満たすものの固定 rubric の重要語を落として
`0/3` だった。要約・タグ用途の onboarding 候補としては採用しない判断が妥当。
