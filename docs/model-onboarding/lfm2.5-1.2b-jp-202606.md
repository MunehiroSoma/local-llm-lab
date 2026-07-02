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
| 3 Standard benchmark | not run | benchmark harness selection is still pending |
| 4 Custom task evaluation | not run | golden set / promptfoo task run is still pending |

## Proposed results row

This row is not appended yet because `results/results.csv` append and adopt/hold/reject are Operations approval gates.

```csv
lfm2.5-1.2b-jp-202606,8c74801fdfe71394c59d3f519b86de305ff49f00,ollama,mac,summarize,q4_k_m,yes,32768,237.348,53.5736,,,,,2026-07-02,onboarding fit+speed; ollama_id=cb967c9bd843
```

## Verdict

Hold for now. Fit and speed are strong on Mac, but standard benchmark, custom task evaluation, results append, and Operations acceptance are still open.
