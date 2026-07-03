# Results summary report

## Metadata

- Generated date: `2026-07-03`
- Source data: `results/results.csv`
- Source rows: `8`
- Representative rows: `7`
- Git commit: `fc1f0153b487aac06eebb8dbd94a5599a0c9888d`
- Command: `python3 -m harness.reporting.results_summary --input results/results.csv --output results/reports/2026-07-03-results-summary.md`
- Python: `3.11.9`
- Quarto: `not installed`
- Plotly: `6.2.0`
- kaleido: `1.0.0`

## Representative Results

| model | runtime | env | profile | fit | tok_s | ttft_ms | std_bench | task_score | date | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| devstral-small-2 | ollama | mac | coding | yes | 16.1549 | 208.567 | 0.947274 | 1 | 2026-07-03 | adopt |
| qwen3-coder-30b-a3b | ollama | mac | coding | yes | 78.0234 | 111.398 | 0.913315 | 0.96875 | 2026-07-03 | hold |
| lfm2.5-1.2b-jp-202606 | ollama | mac | summarize | yes | 225.426 | 57.7791 | 0.743521 | 0.484444 | 2026-07-03 | reject |
| llm-jp-4-8b-instruct | ollama | mac | summarize | yes | 48.7303 | 185.477 | 0.959786 | 1 | 2026-07-03 | adopt |
| gemma4-26b-a4b | ollama | mac | vlm | yes | 59.3692 | 389.411 |  | 1 | 2026-07-02 | hold |
| mlx-community/gemma-3-4b-it-4bit | mlx-vlm | mac | vlm | yes | 88.794 |  |  | 1 | 2026-07-02 | hold |
| gemma4-26b-a4b | ollama | mac | vlm-screenshot | yes | 62.4738 | 1681.96 |  | 0.98 | 2026-07-02 | hold |

## Speed Chart

Text bar chart for `tok_s` among representative rows with numeric speed data.

- `lfm2.5-1.2b-jp-202606 / ollama / mac` ############################## `225.426 tok/s`
- `mlx-community/gemma-3-4b-it-4bit / mlx-vlm / mac` ############ `88.794 tok/s`
- `qwen3-coder-30b-a3b / ollama / mac` ########## `78.0234 tok/s`
- `gemma4-26b-a4b / ollama / mac` ######## `62.4738 tok/s`
- `gemma4-26b-a4b / ollama / mac` ######## `59.3692 tok/s`
- `llm-jp-4-8b-instruct / ollama / mac` ###### `48.7303 tok/s`
- `devstral-small-2 / ollama / mac` ## `16.1549 tok/s`

## Notes

- This report reads `results/results.csv` only.
- `results/raw/` is not an input and remains local evidence only.
- `results/results.csv` remains append-only; this command does not modify it.
