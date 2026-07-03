# qwen3-8b onboarding final report

Date: 2026-07-03
Model issue: #29
Environment: `mac`
Runtime: `ollama`
Endpoint: `http://127.0.0.1:11434/v1`

## Scope

#29 の Mac/Ollama baseline として、Fit、Speed、Layer 3 標準ベンチ、Layer 4 自前タスク評価を実行した。
RTX / DGX / CUDA vLLM は対象外。#85 の llama.cpp / vLLM Metal はランタイム導入 smoke までで、同一
`qwen3-8b` 条件の比較値はこのPRでは追加していない。

対象モデル:

- Registry id: `qwen3-8b`
- Runtime model: `qwen3-8b:latest`
- Source revision: not pinned
- Ollama model id: `500a1f067a9f`
- Quantization: `q4_k_m`
- Ollama reported context length: `40960`

## Layer 1 Fit and Layer 2 Speed

Command:

```bash
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

Result:

| Layer | Result |
|---|---:|
| Layer 1 Fit | `fit=yes` |
| Layer 2 Speed | `tok_s=46.3565`, `ttft_ms=163.1` |

## Layer 3 Standard Benchmark

`llm-jp-eval` v2.1.5 の `jcommonsenseqa` test full split を実行した。

- Tool: `llm-jp-eval` v2.1.5, commit `5067fe7bcd33797643835573505d5ec06858ea34`
- Dataset: `jcommonsenseqa`
- Split: `test`
- Samples: 1119
- Setting: full split, `max_num_samples=-1`, 4-shot dataset default
- Metric: `exact_match`

Command:

```bash
cd /tmp/llm-jp-eval-v2.1.5
uv run python scripts/evaluate_llm.py eval \
  --config configs/local_ollama_qwen3_8b_jcommonsenseqa.yaml
```

Result:

| Metric | Value |
|---|---:|
| `jcommonsenseqa_exact_match` | `0.0` |
| `CR` | `0.0` |
| `AVG` | `0.0` |
| `ool` | `1.0` |
| Correct / total | `0 / 1119` |
| Non-empty extracted predictions | `0 / 1119` |

The local `/tmp` copy used the same ChatOpenAI-to-Ollama patch recorded in earlier `llm-jp-eval` runs. The result JSON
contains empty `output` and empty `pred` fields for sampled records, so this is recorded as an OpenAI-compatible API /
thinking-mode compatibility failure for the current harness path.

## Layer 4 Custom Task Evaluation

`summary-tags-public-v1` was executed through `harness.run_onboarding`.

- Task set: `datasets/golden/samples/summary-tags-public-v1.yaml`
- Judge / rubric: `deterministic-marker-rubric-v1`
- Tasks: 3 public summarization/tagging cases

Result:

| Metric | Value |
|---|---:|
| `task_score` / mean score | `0.0` |
| Passed / total | `0 / 3` |
| Median tok/s | `45.92021532998982` |
| Median TTFT | `435.2656670016586 ms` |

## OpenAI Compatibility Check

The native Ollama chat API can return content when `think=false` is supplied:

```text
OK
```

The OpenAI-compatible API smoke used by the harness returned empty `content` for short prompts against the same local
model. That makes the current shared harness path unsuitable for adopting this model without an adapter change.

## Recorded Result Row

This row was appended to `results/results.csv` after Operations approval.

```csv
qwen3-8b,,ollama,mac,summarize,q4_k_m,yes,40960,46.3565,163.1,,0,0,,2026-07-03,reject; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; task=summary-tags-public-v1; judge=deterministic-marker-rubric-v1; pass=0/3; openai_compat_content_empty; ollama_id=500a1f067a9f; raw=2026-07-03-qwen3-8b-onboarding-fit-speed-task.json
```

## Verdict

Proposal: `reject`.

Fit and speed are measurable, but both Layer 3 and Layer 4 fail through the current OpenAI-compatible evaluation path.
The model should not be adopted until the harness can pass Ollama-native `think=false` or another supported Qwen3
answer-content path into the evaluation stack.

## Raw Evidence

Local raw files:

- `results/raw/2026-07-03-qwen3-8b-onboarding-fit-speed-task.json`
- `results/raw/2026-07-03-qwen3-8b-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`
- `results/raw/2026-07-03-qwen3-8b-llm-jp-eval-jcommonsenseqa-full-v2.1.5.console.log`

`results/raw/` is intentionally ignored by git.

## #29 Completion Impact

Mac/Ollama で実測可能な 4 階層評価、verdict、`results/results.csv` append-only 追記は完了した。
残りは追記PR merge 後の #29 close。
