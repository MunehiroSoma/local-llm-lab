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
  --stop '<|end|>' \
  --max-tokens 128 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 180
python3 -m harness.capability.run \
  --model llm-jp-4-8b-instruct \
  --env mac \
  --runtime ollama \
  --profile summarize \
  --quantization q4_k_m \
  --revision 7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1 \
  --max-model-len 65536 \
  --bench llm-jp-eval-smoke-ja-qa-public-v1 \
  --score 1.0
python3 -m harness.task.promptfoo.evaluate_json \
  --output '{"summary":"ローカリアルLMの評価は同一条件下で実施し、結果をCSV形式で記録します。","tags":["ローカリアルLM","評価","CSV"]}'
```

## Layer results

| Layer | Status | Result |
|---|---|---|
| 1 Fit | done | `fit=yes` through Ollama OpenAI-compatible API |
| 2 Speed | done | median `tok_s=48.7303`, median `ttft_ms=185.477` with `--stop '<|end|>'` |
| 3 Standard benchmark | done | `llm-jp-eval-smoke-ja-qa-public-v1=1.0`; public one-question Japanese QA smoke, not full official `llm-jp-eval` |
| 4 Custom task evaluation | done | `summary-tags-schema-public-v1=1.0`; schema-only summary/tag JSON score |

## Results row

This row was appended to `results/results.csv` after human approval to complete #64.

```csv
llm-jp-4-8b-instruct,7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1,ollama,mac,summarize,q4_k_m,yes,65536,48.7303,185.477,,1,1,,2026-07-02,hold; stop=<|end|>; bench=llm-jp-eval-smoke-ja-qa-public-v1; task=summary-tags-schema-public-v1; ollama_id=d5bf362b9fd8
```

## Verdict

Hold. The model now completes all four onboarding layers on Mac/Ollama and remains useful as a Japanese baseline candidate, but the Layer 3 score is only a lightweight public smoke rather than a full official `llm-jp-eval` run. The summary/tag schema passed, but the generated label text contained a minor typo (`ローカリアルLM`), so this should not be adopted as a production summarization model without a fuller Japanese eval.
