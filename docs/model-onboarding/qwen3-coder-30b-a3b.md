# qwen3-coder-30b-a3b onboarding record

Parent issue: #4
Model issue: #63
Date: 2026-07-02
Environment: `mac`

## Registry and runtime

- Registry id: `qwen3-coder-30b-a3b`
- Source repo: `Qwen/Qwen3-Coder-30B-A3B-Instruct`
- Source repo HEAD: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`
- Runtime model: `qwen3-coder:30b`
- Local Ollama alias: `qwen3-coder-30b-a3b`
- Ollama model id: `06c1097efce0`
- Quantization: `Q4_K_M`
- Ollama reported architecture: `qwen3moe`
- Ollama reported parameters: `30.5B`
- Ollama reported context length: `262144`
- Registry max_model_len for this run: `262144`

## Commands

```bash
ollama pull qwen3-coder:30b
ollama cp qwen3-coder:30b qwen3-coder-30b-a3b
python3 -m harness.run_onboarding \
  --model qwen3-coder-30b-a3b \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --profile coding \
  --quantization q4_k_m \
  --revision b2cff646eb4bb1d68355c01b18ae02e7cf42d120 \
  --max-model-len 262144 \
  --max-tokens 128 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 240
```

## Layer results

| Layer | Status | Result |
|---|---|---|
| 1 Fit | done | `fit=yes` through Ollama OpenAI-compatible API |
| 2 Speed | done | median `tok_s=78.0234`, median `ttft_ms=111.398` |
| 3 Standard benchmark | not run | benchmark harness selection is still pending |
| 4 Custom task evaluation | not run | golden set / promptfoo task run is still pending |

## Proposed results row

This row is not appended yet because `results/results.csv` append and adopt/hold/reject are Operations approval gates.

```csv
qwen3-coder-30b-a3b,b2cff646eb4bb1d68355c01b18ae02e7cf42d120,ollama,mac,coding,q4_k_m,yes,262144,78.0234,111.398,,,,,2026-07-02,onboarding fit+speed; ollama_id=06c1097efce0
```

## Verdict

Hold for now. Fit and speed are confirmed on Mac, but standard benchmark, custom task evaluation, results append, and Operations acceptance are still open.
