# Capability benchmark adapters

Date: 2026-07-02
Parent issue: #1
BOLT: #10

## Scope

Layer 3 standard benchmarks should be recorded through one fixed result schema even when each benchmark writes a
different JSON shape. This BOLT adds deterministic score extraction adapters while keeping the actual benchmark runners
external.

## Implemented

- `harness/capability/adapters.py`
  - explicit dot-path extraction with dict and list-index support
  - lm-eval style `results.<task>.acc_norm` / `acc` / `exact_match` / `f1` averaging
  - common scalar/case-average extraction for `llm-jp-eval` and `VLMEvalKit` style JSON
  - Aider style `pass_rate` / `percent_cases_passed` extraction
- `harness/capability/run.py`
  - `--score-json` no longer requires `--metric-key` when a known/common shape is present
  - `--metric-key` still overrides adapter inference for strict reproducibility

## Verification

```bash
PYTHONPATH=. pytest tests/test_capability_adapters.py tests/test_task_helpers.py -q

python3 -m harness.capability.run \
  --model llm-jp-4-8b-instruct \
  --env mac \
  --runtime ollama \
  --bench lm-eval-mmlu-smoke \
  --score-json <(printf '%s' '{"results":{"mmlu_pro":{"acc_norm":0.62},"gsm8k":{"exact_match":0.74}}}')

python3 -m harness.capability.run \
  --model llm-jp-4-8b-instruct \
  --env mac \
  --runtime ollama \
  --bench llm-jp-eval-smoke-ja-qa-public-v1 \
  --score-json results/raw/2026-07-02-llm-jp-4-8b-instruct-capability.json
```

Observed outputs:

- lm-eval style sample produced `std_bench=0.68`
- existing llm-jp smoke raw JSON produced `std_bench=1`

No new `results/results.csv` row was appended; Operations acceptance remains a separate gate.
