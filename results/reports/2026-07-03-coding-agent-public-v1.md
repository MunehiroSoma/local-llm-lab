# coding-agent-public-v1 design report

## Context

Issue #13 adds a Layer 4 coding profile evaluation for public, repeatable model onboarding.
Recent Fit/Speed work for `qwen3-coder-30b-a3b` and `devstral-small-2` can reuse this
same scorer later, but this report does not record those model results.

## Scope

- Task set: `coding-agent-public-v1`
- Sample location: `datasets/golden/samples/coding-agent-public-v1.yaml`
- Runner: `python3 -m harness.task.coding_agent.run_case`
- Judge: `deterministic-json-files-pytest-rubric-v1`
- Data class: public synthetic toy specs only

The runner does not require Aider, OpenHands, Langfuse, CUDA, RTX, DGX, or vLLM-Omni.
It directly evaluates an OpenAI-compatible coding model, or scores saved raw outputs.

## Rubric

Each task requires a JSON object with `files[].path` and `files[].content`.
The scorer writes generated files and public pytest files to a temporary directory.

`task_score` is the mean of four deterministic components:

| Component | Weight | Check |
|---|---:|---|
| schema | 0.25 | output parses as the fixed JSON patch schema |
| files | 0.25 | required relative file paths are present |
| markers | 0.25 | required function/implementation markers are present |
| tests | 0.25 | bundled pytest command exits successfully |

The v1 set contains two small Python tasks:

- `slug-normalizer`: implement `to_slug` in `slugify_utils.py`
- `kv-parser`: implement `parse_kv_lines` in `kv_config.py`

## Commands

Score saved outputs:

```bash
python3 -m harness.task.coding_agent.run_case \
  --outputs results/raw/qwen3-coder-30b-a3b-coding-agent-outputs.json \
  --model qwen3-coder-30b-a3b \
  --runtime mlx \
  --env mac \
  --output-json results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

Run a live OpenAI-compatible endpoint:

```bash
python3 -m harness.task.coding_agent.run_case \
  --base-url http://127.0.0.1:11434/v1 \
  --model devstral-small-2 \
  --runtime ollama \
  --env mac \
  --profile coding \
  --output-json results/raw/devstral-small-2-coding-agent-public-v1.json
```

Do not pass `--append-results` until the Operations approval gate has approved the
exact `results/results.csv` row.

## Validation

This design is complete when unit tests, `make validate`, and pre-commit pass on MacBook Pro.
No raw evidence or `results/results.csv` row is required for Issue #13.
