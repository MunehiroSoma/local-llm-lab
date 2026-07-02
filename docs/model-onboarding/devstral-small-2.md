# devstral-small-2 onboarding record

Parent issue: #4
Model issue: #65
Date: 2026-07-02
Environment: `mac`

## Registry and runtime

- Registry id: `devstral-small-2`
- Source repo: `mistralai/Devstral-Small-2-24B-Instruct-2512`
- Source repo HEAD: `c599e8e56f3f9110e97f0dc0450ce248e3334d84`
- Runtime model: `devstral-small-2`
- Local Ollama alias: `devstral-small-2`
- Ollama model id: `24277f07f62d`
- Quantization: `Q4_K_M`
- Ollama reported architecture: `mistral3`
- Ollama reported parameters: `24.0B`
- Ollama reported capabilities: `completion`, `vision`, `tools`
- Ollama reported context length: `393216`
- Registry max_model_len for this run: `131072`

## Commands

```bash
ollama pull devstral-small-2
python3 -m harness.run_onboarding \
  --model devstral-small-2 \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --profile coding \
  --quantization q4_k_m \
  --revision c599e8e56f3f9110e97f0dc0450ce248e3334d84 \
  --max-model-len 131072 \
  --max-tokens 128 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 240
```

## Layer results

| Layer | Status | Result |
|---|---|---|
| 1 Fit | done | `fit=yes` through Ollama OpenAI-compatible API |
| 2 Speed | done | median `tok_s=16.1549`, median `ttft_ms=208.567` |
| 3 Standard benchmark | not run | benchmark harness selection is still pending |
| 4 Custom task evaluation | not run | golden set / promptfoo task run is still pending |

## Proposed results row

This row is not appended yet because `results/results.csv` append and adopt/hold/reject are Operations approval gates.

```csv
devstral-small-2,c599e8e56f3f9110e97f0dc0450ce248e3334d84,ollama,mac,coding,q4_k_m,yes,131072,16.1549,208.567,,,,,2026-07-02,onboarding fit+speed; ollama_id=24277f07f62d
```

## Verdict

Hold for now. Fit and speed are confirmed on Mac, but standard benchmark, custom task evaluation, results append, and Operations acceptance are still open.
