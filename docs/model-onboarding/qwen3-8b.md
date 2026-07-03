# qwen3-8b onboarding record

Parent issue: #4
Model issue: #29
Date: 2026-07-03
Environment: `mac`

## Registry and runtime

- Registry id: `qwen3-8b`
- Source repo: `Qwen/Qwen3-8B`
- Source revision: not pinned in this run
- Runtime model: `qwen3:8b`
- Local Ollama alias: `qwen3-8b`
- Ollama model id: `500a1f067a9f`
- Quantization: `Q4_K_M`
- Ollama reported architecture: `qwen3`
- Ollama reported parameters: `8.2B`
- Ollama reported context length: `40960`
- Registry max_model_len for this run: `40960`

## Commands

```bash
ollama pull qwen3:8b
ollama cp qwen3:8b qwen3-8b
python3 -m harness.run_onboarding \
  --model qwen3-8b \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --profile summarize \
  --quantization q4_k_m \
  --max-model-len 40960 \
  --max-tokens 128 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 240 \
  --stop '<|im_start|>' \
  --stop '<|im_end|>' \
  --raw-dir results/raw \
  --output-json results/raw/2026-07-03-qwen3-8b-onboarding-fit-speed-task.json
```

Layer 3 used the local `llm-jp-eval` v2.1.5 setup already used by the other Mac onboarding runs:

```bash
cd /tmp/llm-jp-eval-v2.1.5
uv run python scripts/evaluate_llm.py eval \
  --config configs/local_ollama_qwen3_8b_jcommonsenseqa.yaml
```

## Layer results

| Layer | Status | Result |
|---|---|---|
| 1 Fit | done | `fit=yes` through Ollama OpenAI-compatible API |
| 2 Speed | done | median `tok_s=46.3565`, median `ttft_ms=163.1` |
| 3 Standard benchmark | done | `jcommonsenseqa_exact_match=0.0`; 1119/1119 outputs had empty extracted prediction |
| 4 Custom task evaluation | done | `summary-tags-public-v1` score `0.0`, pass `0/3` |

## Compatibility note

The Ollama native chat API can return content for the same model when `think=false` is supplied:

```bash
python3 - <<'PY'
import json, urllib.request
payload = {
    "model": "qwen3-8b",
    "messages": [{"role": "user", "content": "日本語でOKとだけ返してください。"}],
    "stream": False,
    "think": False,
    "options": {"num_predict": 32, "temperature": 0},
}
req = urllib.request.Request(
    "http://127.0.0.1:11434/api/chat",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
)
print(json.load(urllib.request.urlopen(req, timeout=120))["message"]["content"])
PY
```

Observed output:

```text
OK
```

However, the OpenAI-compatible endpoint used by the shared harness returned empty `content` for short smoke prompts. The
current onboarding verdict therefore reflects the supported harness path, not a claim that the native Ollama API cannot
generate text.

## Proposed results row

This row is not appended yet because `results/results.csv` append and adopt/hold/reject are Operations approval gates.

```csv
qwen3-8b,,ollama,mac,summarize,q4_k_m,yes,40960,46.3565,163.1,,0,0,,2026-07-03,reject; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; task=summary-tags-public-v1; judge=deterministic-marker-rubric-v1; pass=0/3; openai_compat_content_empty; ollama_id=500a1f067a9f; raw=2026-07-03-qwen3-8b-onboarding-fit-speed-task.json
```

## Verdict

Reject for the current Mac/Ollama harness path. Fit and token throughput are measurable, but the OpenAI-compatible API
returns empty content in this setup, which makes both Layer 3 and Layer 4 unusable for the current evaluation workflow.
