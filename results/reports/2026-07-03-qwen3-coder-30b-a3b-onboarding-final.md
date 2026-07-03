# qwen3-coder-30b-a3b onboarding final report

Date: 2026-07-03
Model issue: #63
Environment: `mac`
Runtime: `ollama`
Endpoint: `http://127.0.0.1:11434/v1`

## Scope

#63 の残り作業として、MacBook Pro で実測可能な Layer 3 標準ベンチと Layer 4 自前タスク評価を揃えた。
RTX / DGX / CUDA / vLLM-Omni は対象外。

対象モデル:

- Registry id: `qwen3-coder-30b-a3b`
- Runtime model: `qwen3-coder-30b-a3b:latest`
- Source revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`
- Ollama model id: `06c1097efce0`
- Quantization: `q4_k_m`

## Existing Fit and Speed

Issue #63 の既存実測値:

| Layer | Result |
|---|---:|
| Layer 1 Fit | `fit=yes` |
| Layer 2 Speed | `tok_s=78.0234`, `ttft_ms=111.398` |

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
  --config configs/local_ollama_qwen3_coder_jcommonsenseqa.yaml
```

The local `/tmp` copy used the same ChatOpenAI-to-Ollama patch recorded in earlier `llm-jp-eval` runs. Official prompt
construction, dataset preprocessing, answer extraction, and scoring paths were unchanged.

Result:

| Metric | Value |
|---|---:|
| `jcommonsenseqa_exact_match` | `0.9133154602323503` |
| `CR` | `0.9133154602323503` |
| `AVG` | `0.9133154602323503` |
| `ool` | `0.0` |
| Correct / total | `1022 / 1119` |

`harness.capability.run` normalized the representative score as `std_bench=0.913315`.

## Layer 4 Custom Task Evaluation

`coding-agent-public-v1` を実行した。

- Task set: `datasets/golden/samples/coding-agent-public-v1.yaml`
- Judge / rubric: `deterministic-json-files-pytest-rubric-v1`
- Tasks: 2 public synthetic coding cases
- Runner: `harness.task.coding_agent.run_case`

Command:

```bash
python3 -m harness.task.coding_agent.run_case \
  --base-url http://127.0.0.1:11434/v1 \
  --model qwen3-coder-30b-a3b \
  --runtime ollama \
  --env mac \
  --profile coding \
  --output-json results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

Result:

| Metric | Value |
|---|---:|
| `task_score` / mean score | `0.96875` |
| Passed / total | `1 / 2` |
| Median tok/s | `76.37836650834119` |
| Median TTFT | `4791.938749998735 ms` |

Case breakdown:

| Case | Score | Passed | Notes |
|---|---:|---:|---|
| `slug-normalizer` | `0.9375` | no | Public pytest passed, but fixed marker `re.sub` was missing. |
| `kv-parser` | `1.0` | yes | Schema, file path, markers, and public pytest all passed. |

## Result Row Candidate

`results/results.csv` is not modified yet. Append requires the Operations approval gate.

```csv
qwen3-coder-30b-a3b,b2cff646eb4bb1d68355c01b18ae02e7cf42d120,ollama,mac,coding,q4_k_m,yes,262144,78.0234,111.398,,0.913315,0.96875,,2026-07-03,hold; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; task=coding-agent-public-v1; judge=deterministic-json-files-pytest-rubric-v1; pass=1/2; ollama_id=06c1097efce0; raw=qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

## Verdict Proposal

Proposal: `hold`.

Fit and speed are strong on Mac/Ollama, and Layer 3 is high enough for a coding-profile candidate. Layer 4 passed all
public pytest checks but missed one deterministic marker in `slug-normalizer`, so this model should remain a strong
candidate rather than an adopted default until another coding task set confirms robustness.

## Raw Evidence

Local raw files:

- `results/raw/2026-07-03-qwen3-coder-30b-a3b-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`
- `results/raw/2026-07-03-qwen3-coder-30b-a3b-llm-jp-eval-jcommonsenseqa-full-v2.1.5.console.log`
- `results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json`

`results/raw/` is intentionally ignored by git.

## #63 Completion Impact

Mac/Ollama で実測可能な 4 階層評価は揃った。残りは human Operations approval gate 後の
`results/results.csv` append-only 追記、PR merge 後の #63 close。
