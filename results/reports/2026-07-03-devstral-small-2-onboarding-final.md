# devstral-small-2 onboarding final report

Date: 2026-07-03
Model issue: #65
Environment: `mac`
Runtime: `ollama`
Endpoint: `http://127.0.0.1:11434/v1`

## Scope

#65 の残り作業として、MacBook Pro で実測可能な Layer 3 標準ベンチと Layer 4 自前タスク評価を揃えた。
RTX / DGX / CUDA / vLLM-Omni は対象外。

対象モデル:

- Registry id: `devstral-small-2`
- Runtime model: `devstral-small-2:latest`
- Source revision: `c599e8e56f3f9110e97f0dc0450ce248e3334d84`
- Ollama model id: `24277f07f62d`
- Quantization: `q4_k_m`

## Existing Fit and Speed

Issue #65 の既存実測値:

| Layer | Result |
|---|---:|
| Layer 1 Fit | `fit=yes` |
| Layer 2 Speed | `tok_s=16.1549`, `ttft_ms=208.567` |

Layer 4 の再計測時は別作業後の Ollama model switch / residual load と見られる TTFT 悪化があったため、速度判断は
既存 Layer 2 値を基準にする。

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
  --config configs/local_ollama_devstral_small_2_jcommonsenseqa.yaml
```

The local `/tmp` copy used the same ChatOpenAI-to-Ollama patch recorded in earlier `llm-jp-eval` runs. Official prompt
construction, dataset preprocessing, answer extraction, and scoring paths were unchanged.

Result:

| Metric | Value |
|---|---:|
| `jcommonsenseqa_exact_match` | `0.9472743521000894` |
| `CR` | `0.9472743521000894` |
| `AVG` | `0.9472743521000894` |
| `ool` | `0.0` |
| Correct / total | `1060 / 1119` |

`harness.capability.run` normalized the representative score as `std_bench=0.947274`.

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
  --model devstral-small-2 \
  --runtime ollama \
  --env mac \
  --profile coding \
  --output-json results/raw/devstral-small-2-coding-agent-public-v1.json
```

Initial result:

| Metric | Value |
|---|---:|
| `task_score` / mean score | `1.0` |
| Passed / total | `2 / 2` |
| Median tok/s | `16.22044685197696` |
| Median TTFT | `5053.714207999292 ms` |

Re-run after the user noted possible parallel workload:

| Metric | Value |
|---|---:|
| `task_score` / mean score | `1.0` |
| Passed / total | `2 / 2` |
| Median tok/s | `14.242257879003887` |
| Median TTFT | `30791.414896000788 ms` |

The re-run confirmed task quality (`2 / 2`, `task_score=1.0`) but not a cleaner speed measurement. Treat Layer 4
speed fields as reference only; Layer 2 remains the onboarding speed record.

Case breakdown:

| Case | Score | Passed | Notes |
|---|---:|---:|---|
| `slug-normalizer` | `1.0` | yes | Schema, file path, markers, and public pytest all passed. |
| `kv-parser` | `1.0` | yes | Schema, file path, markers, and public pytest all passed. |

## Result Row Candidate

`results/results.csv` is not modified yet. Append requires the Operations approval gate.

```csv
devstral-small-2,c599e8e56f3f9110e97f0dc0450ce248e3334d84,ollama,mac,coding,q4_k_m,yes,131072,16.1549,208.567,,0.947274,1,,2026-07-03,adopt; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; task=coding-agent-public-v1; judge=deterministic-json-files-pytest-rubric-v1; pass=2/2; ollama_id=24277f07f62d; raw=devstral-small-2-coding-agent-public-v1.json
```

## Verdict Proposal

Proposal: `adopt`.

Layer 3 is strong on the same full `llm-jp-eval` benchmark used for current Mac/Ollama onboarding, and Layer 4 completed
both public coding-agent tasks at full rubric score. It is slower than `qwen3-coder-30b-a3b`, so adoption should be for
quality-first coding-agent evaluation rather than latency-sensitive use.

## Raw Evidence

Local raw files:

- `results/raw/2026-07-03-devstral-small-2-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`
- `results/raw/2026-07-03-devstral-small-2-llm-jp-eval-jcommonsenseqa-full-v2.1.5.console.log`
- `results/raw/devstral-small-2-coding-agent-public-v1.json`
- `results/raw/devstral-small-2-coding-agent-public-v1-rerun.json`

`results/raw/` is intentionally ignored by git.

## #65 Completion Impact

Mac/Ollama で実測可能な 4 階層評価は揃った。残りは human Operations approval gate 後の
`results/results.csv` append-only 追記、PR merge 後の #65 close。
