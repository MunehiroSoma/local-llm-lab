# VLM screenshot custom eval set

Date: 2026-07-02
Parent issue: #4
BOLT: #73

## Scope

This report defines a first public/synthetic Layer 4 screenshot task set for VLM evaluation. It is separate from
Layer 3 standard benchmarks such as lm-eval, VLMEvalKit, and llm-jp-eval.

## Tracked task set

- Task definition: `harness/task/vlm/screenshot_tasks.yaml`
- Scoring CLI: `python3 -m harness.task.vlm.screenshot_eval`
- Sample images: `datasets/golden/samples/vlm/screenshots/*.svg`
- Data policy: all images are synthetic public samples. No real product, personal, household, or work screenshots are
  committed.

## Task coverage

| Category | Task ID |
|---|---|
| CI error reading | `synthetic-ci-failure` |
| Login / error state | `synthetic-login-error` |
| Calendar conflict | `synthetic-calendar-conflict` |
| Dashboard KPI | `synthetic-dashboard-kpi` |
| Table OCR / filtering | `synthetic-data-table-filter` |
| Settings state | `synthetic-settings-permissions` |
| Checkout warning | `synthetic-checkout-warning` |
| Mobile notifications | `synthetic-mobile-notifications` |
| Code review UI | `synthetic-code-review` |
| Chart tooltip | `synthetic-chart-tooltip` |

## Usage

Score an existing JSON output file:

```bash
python3 -m harness.task.vlm.screenshot_eval \
  --outputs results/raw/sample-vlm-screenshot-outputs.json \
  --output-json results/raw/sample-vlm-screenshot-scores.json
```

Run a live OpenAI-compatible endpoint:

```bash
python3 -m harness.task.vlm.screenshot_eval \
  --model gemma4-26b-a4b \
  --base-url http://127.0.0.1:11434/v1 \
  --env mac \
  --runtime ollama \
  --raster-dir results/raw/vlm-screenshot-v1-png \
  --output-json results/raw/2026-07-02-vlm-screenshot-gemma4-baseline.json
```

Use `--append-results` only after the Operations approval gate.

## Current status

The deterministic task set and scorer are implemented. Ollama rejects SVG data URLs with `invalid image input`, so the
live baseline path uses `--raster-dir` to render the synthetic SVG samples to PNG files under ignored `results/raw/`.

## Gemma4/Ollama baseline

Raw output:

- `results/raw/2026-07-02-vlm-screenshot-gemma4-baseline.json`
- Rendered PNGs: `results/raw/vlm-screenshot-v1-png/*.png`

Conditions:

- Model: `gemma4-26b-a4b`
- Runtime: Ollama OpenAI-compatible API
- Environment: `mac`
- Task set: `vlm-screenshot-task-set` v1
- `max_tokens=220`, streaming enabled

Aggregate:

| Model | Tasks | Pass | Mean score | Median tok/s | Median TTFT |
|---|---:|---:|---:|---:|---:|
| `gemma4-26b-a4b` | 10 | 10 | `0.98` | `62.4738` | `1681.963ms` |

Per-task status:

| Task | Category | Status | Marker score |
|---|---|---|---:|
| `synthetic-ci-failure` | CI error reading | pass | `1.00` |
| `synthetic-login-error` | Login / error state | pass | `1.00` |
| `synthetic-calendar-conflict` | Calendar conflict | pass | `1.00` |
| `synthetic-dashboard-kpi` | Dashboard KPI | pass | `1.00` |
| `synthetic-data-table-filter` | Table OCR / filtering | pass | `1.00` |
| `synthetic-settings-permissions` | Settings state | pass | `1.00` |
| `synthetic-checkout-warning` | Checkout warning | pass | `1.00` |
| `synthetic-mobile-notifications` | Mobile notifications | pass | `1.00` |
| `synthetic-code-review` | Code review UI | pass | `1.00` |
| `synthetic-chart-tooltip` | Chart tooltip | pass | `0.80` |

## Appended results row

After human Operations approval, the representative result row below was appended to `results/results.csv` with a
`hold` decision. This is a separate `vlm-screenshot` profile from the earlier public-image `vlm` smoke row.

```csv
gemma4-26b-a4b,,ollama,mac,vlm-screenshot,q4_k_m,yes,128000,62.4738,1681.963,,,0.98,,2026-07-02,hold; synthetic screenshot task set v1; pass=10/10; task=vlm-screenshot-task-set-v1; svg_rasterized_to_png; raw=2026-07-02-vlm-screenshot-gemma4-baseline.json
```
