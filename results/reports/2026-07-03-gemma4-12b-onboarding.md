# gemma4-12b onboarding report

Date: 2026-07-03
Model issue: #26
Environment: `mac`

## Scope

#26 の Mac baseline として、`gemma4-12b` を Ollama と MLX-VLM の両方で確認した。
RTX / DGX / CUDA vLLM はこの作業環境から触れないため対象外。

対象モデル:

- Registry id: `gemma4-12b`
- Source repo: `google/gemma-4-12b-it`
- Source revision: `5926caa4ec0cac5cbfadaf4077420520de1d5205`
- Ollama model: `gemma4:12b`
- Ollama alias: `gemma4-12b`
- Ollama ID: `4eb23ef187e2`
- MLX-VLM repo: `mlx-community/gemma-4-12b-it-4bit`
- MLX-VLM revision: `73bcf09092aa277861d5a191b989b666f7f32e8f`
- MLX-VLM: `0.6.3`

## Layer 1 Fit

Both runtimes loaded on the MacBook Pro.

| Runtime | Fit | Evidence |
|---|---:|---|
| `ollama` | yes | `python3 -m harness.task.vlm.screenshot_eval --model gemma4-12b --base-url http://127.0.0.1:11434/v1 ...` |
| `mlx-vlm` | yes | `python -m mlx_vlm.generate --model mlx-community/gemma-4-12b-it-4bit --revision 73bcf09092aa277861d5a191b989b666f7f32e8f ...` |

MLX-VLM の `--max-kv-size 128000` smoke also returned `OK`.

## Layer 2 Speed

Ollama uses the live OpenAI-compatible screenshot evaluator, so TTFT is available. MLX-VLM CLI does not expose
OpenAI-style TTFT; the result records prompt and generation throughput instead.

| Runtime | Prompt tok/s | Generation tok/s | TTFT | Peak memory |
|---|---:|---:|---:|---:|
| `ollama` | n/a | `28.952` | `1745.514ms` | n/a |
| `mlx-vlm` | `237.824` | `33.105` | n/a | `7.518 GB` |

MLX-VLM speed was measured as a cached 3-run median on `synthetic-code-review.png`:

| Metric | Values | Median |
|---|---|---:|
| Prompt throughput | `237.824`, `237.377`, `245.437` tok/s | `237.824` |
| Generation throughput | `33.105`, `33.100`, `33.142` tok/s | `33.105` |
| Peak memory | `7.518`, `7.518`, `7.518` GB | `7.518` |

## Layer 3 Standard Benchmark

Ollama text endpoint was evaluated with the same local official `llm-jp-eval` v2.1.5 setup used by the other Mac
onboarding runs.

- Tool: `llm-jp-eval` v2.1.5, commit `5067fe7bcd33797643835573505d5ec06858ea34`
- Dataset: `jcommonsenseqa`
- Split: `test`
- Samples: `1119`
- Setting: full split, `max_num_samples=-1`, 4-shot dataset default, `max_tokens=8`, `max_concurrent=1`
- Metric: `exact_match`
- Score: `0.0`
- Empty outputs: `1119 / 1119`
- Raw: `results/raw/gemma4-12b/2026-07-03-gemma4-12b-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`

Compatibility note: Ollama native `/api/chat` returns content when `think=false` is supplied, but the OpenAI-compatible
`/v1/chat/completions` path used by the fixed benchmark returns reasoning with empty `content` for this model. The
Layer 3 result is therefore recorded as an execution result and harness/runtime compatibility blocker, not as evidence
that the model lacks Japanese commonsense capability.

MLX-VLM standard VLM benchmarks such as MMMU / VLMEvalKit / llm-jp-eval-mm were not run because this repository does
not yet have a fixed MLX-VLM standard benchmark runner. The synthetic screenshot set below remains Layer 4.

## Layer 4 Custom Task Evaluation

Task set:

- `harness/task/vlm/screenshot_tasks.yaml`
- Name: `vlm-screenshot-task-set`
- Version: `v1`
- Images: public synthetic SVG samples rasterized to PNG under `results/raw/gemma4-12b/`
- Scorer: deterministic marker scorer

Aggregate:

| Runtime | Passed / total | Mean score |
|---|---:|---:|
| `ollama` | `10 / 10` | `0.98` |
| `mlx-vlm` | `9 / 10` | `0.87` |

MLX-VLM missed `synthetic-chart-tooltip` because it omitted the June `27` value required by the marker set.

## Result Row Candidates

Append these rows to `results/results.csv` only after Operations approval.

```csv
gemma4-12b,5926caa4ec0cac5cbfadaf4077420520de1d5205,ollama,mac,vlm-screenshot,q4_k_m,yes,128000,28.952,1745.514,,0,0.98,,2026-07-03,hold; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; openai_compat_content_empty=1119/1119; task=vlm-screenshot-task-set-v1; pass=10/10; ollama_id=4eb23ef187e2; raw=results/raw/gemma4-12b/2026-07-03-gemma4-12b-ollama-screenshot-scores.json
gemma4-12b,5926caa4ec0cac5cbfadaf4077420520de1d5205,mlx-vlm,mac,vlm-screenshot,4bit,yes,128000,33.105,,,,0.87,,2026-07-03,hold; bench=not-run-mlx-vlm-standard-bench-missing; task=vlm-screenshot-task-set-v1; pass=9/10; prompt_tok_s=237.824; peak_memory_gb=7.518; mlx_repo=mlx-community/gemma-4-12b-it-4bit; mlx_revision=73bcf09092aa277861d5a191b989b666f7f32e8f; raw=results/raw/gemma4-12b/2026-07-03-gemma4-12b-mlx-vlm-screenshot-scores.json
```

## Verdict Proposal

Proposal: `hold`.

Reasons:

- Keep: both Ollama and MLX-VLM fit on Mac and pass most or all public synthetic screenshot tasks.
- Prefer Ollama for screenshot/OCR quality today: `10 / 10`, mean `0.98`, matching the prior Gemma4 26B screenshot score
  while using a smaller local model.
- Prefer MLX-VLM when generation throughput matters: `33.105 tok/s` versus Ollama `28.952 tok/s` on the same
  code-review screenshot smoke.
- Hold rather than adopt because the fixed Layer 3 text benchmark path currently records empty content for all 1119
  samples, and a fixed MLX-VLM standard VLM benchmark path is not in the repository yet.

## Raw Evidence

Local raw files:

- `results/raw/gemma4-12b/2026-07-03-gemma4-12b-ollama-screenshot-scores.json`
- `results/raw/gemma4-12b/2026-07-03-fit-smoke-mlx-vlm.txt`
- `results/raw/gemma4-12b/2026-07-03-fit-max-kv-128000-mlx-vlm.txt`
- `results/raw/gemma4-12b/2026-07-03-speed-repeats-mlx-vlm.txt`
- `results/raw/gemma4-12b/2026-07-03-gemma4-12b-mlx-vlm-screenshot-outputs.json`
- `results/raw/gemma4-12b/2026-07-03-gemma4-12b-mlx-vlm-screenshot-scores.json`
- `results/raw/gemma4-12b/2026-07-03-gemma4-12b-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`
- `results/raw/gemma4-12b/2026-07-03-gemma4-12b-llm-jp-eval-jcommonsenseqa-full.console.log`

`results/raw/` is intentionally ignored by git.
