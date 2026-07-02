# llm-jp-4-8b-instruct onboarding record

Parent issue: #4
Model issue: #64
Date: 2026-07-02
Environment: `mac`

## Registry and runtime

- Registry id: `llm-jp-4-8b-instruct`
- Source repo: `llm-jp/llm-jp-4-8b-instruct`
- Source repo HEAD: `098f2b2cf33021eba19a6d3582aa3d071ccc0aff`
- Runtime repo: `mmnga-o/llm-jp-4-8b-instruct-gguf`
- Runtime revision: `7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1`
- Runtime model: `hf.co/mmnga-o/llm-jp-4-8b-instruct-gguf:Q4_K_M`
- Local Ollama alias: `llm-jp-4-8b-instruct`
- Ollama model id: `d5bf362b9fd8`
- Quantization: `Q4_K_M`
- Ollama reported context length: `65536`
- Registry max_model_len for this run: `65536`

## Commands

```bash
ollama pull hf.co/mmnga-o/llm-jp-4-8b-instruct-gguf:Q4_K_M
ollama cp hf.co/mmnga-o/llm-jp-4-8b-instruct-gguf:Q4_K_M llm-jp-4-8b-instruct
python3 -m harness.run_onboarding \
  --model llm-jp-4-8b-instruct \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --profile summarize \
  --quantization q4_k_m \
  --revision 7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1 \
  --max-model-len 65536 \
  --max-tokens 128 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 180
```

## Layer results

| Layer | Status | Result |
|---|---|---|
| 1 Fit | done | `fit=yes` through Ollama OpenAI-compatible API |
| 2 Speed | partial | median `tok_s=8.5833`; median `ttft_ms` was not reported by this run |
| 3 Standard benchmark | not run | benchmark harness selection is still pending |
| 4 Custom task evaluation | not run | golden set / promptfoo task run is still pending |

## Proposed results row

This row is not appended yet because `results/results.csv` append and adopt/hold/reject are Operations approval gates.

```csv
llm-jp-4-8b-instruct,7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1,ollama,mac,summarize,q4_k_m,yes,65536,8.5833,,,,,,2026-07-02,onboarding fit+speed; ollama_id=d5bf362b9fd8
```

## Verdict

Hold for now. Fit and tok/s are confirmed on Mac, but TTFT was not captured in this Ollama path. Standard benchmark, custom task evaluation, results append, and Operations acceptance are still open.
