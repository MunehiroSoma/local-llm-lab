# llm-jp-4-8b-instruct llm-jp-eval jcommonsenseqa benchmark

Date: 2026-07-03
Parent issue: #10
Model issue: #64
Environment: `mac`
Runtime: `ollama`

## Scope

This run fills the Layer 3 standard benchmark gap for `llm-jp-4-8b-instruct` with one official `llm-jp-eval`
dataset instead of the earlier one-question smoke.

- Tool: `llm-jp-eval` v2.1.5, commit `5067fe7bcd33797643835573505d5ec06858ea34`
- Dataset: `jcommonsenseqa`
- Split: `test`
- Samples: 1119
- Setting: full split, `max_num_samples=-1`, 4-shot dataset default
- Metric: `exact_match`
- Runtime model: `llm-jp-4-8b-instruct:latest`
- Stop sequence: `<|end|>`

## Commands

```bash
git clone --depth 1 --branch v2.1.5 https://github.com/llm-jp/llm-jp-eval.git /tmp/llm-jp-eval-v2.1.5
cd /tmp/llm-jp-eval-v2.1.5
uv sync --frozen --no-dev
uv run python scripts/preprocess_dataset.py \
  --dataset-name jcommonsenseqa \
  --output-dir /tmp/llm-jp-eval-v2.1.5/local_files \
  --version-name 2.1.5
uv run python scripts/evaluate_llm.py eval \
  --config configs/local_ollama_llm_jp_jcommonsenseqa.yaml
```

`llm-jp-eval` v2.1.5 uses a completions client for its `vllm-openai` path. Ollama rejected the resulting prompt-array
request, so the local `/tmp` copy was patched to use `ChatOpenAI` against Ollama's OpenAI-compatible
`/v1/chat/completions` endpoint. The official prompt construction, dataset preprocessing, answer extraction, and scoring
code paths were unchanged.

## Result

| Metric | Value |
|---|---:|
| `jcommonsenseqa_exact_match` | `0.9597855227882037` |
| `CR` | `0.9597855227882037` |
| `AVG` | `0.9597855227882037` |
| `ool` | `0.0` |
| Correct / total | `1074 / 1119` |
| Wrong | `45` |
| Inference time | `501.0294s` |

`harness.capability.run` normalized the representative score as `std_bench=0.959786`:

```bash
python3 -m harness.capability.run \
  --model llm-jp-4-8b-instruct \
  --env mac \
  --runtime ollama \
  --profile summarize \
  --quantization q4_k_m \
  --revision 7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1 \
  --max-model-len 65536 \
  --bench llm-jp-eval-jcommonsenseqa-full-v2.1.5 \
  --score-json results/raw/2026-07-03-llm-jp-4-8b-instruct-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json \
  --metric-key evaluation.scores.jcommonsenseqa_exact_match
```

Layer 3 単体の row candidate（未追記）:

```csv
llm-jp-4-8b-instruct,7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1,ollama,mac,summarize,q4_k_m,yes,65536,,,,0.959786,,,2026-07-03,bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5
```

これは Layer 3 実測のみを反映した候補であり、final or revised row ではない。Layer 4 の golden / rubric 評価後、
Operations approval gate で承認された場合に限り、final or revised row を `results/results.csv` に追記する。

## Raw Evidence

Local raw files:

- `results/raw/2026-07-03-llm-jp-4-8b-instruct-llm-jp-eval-jcommonsenseqa-full-v2.1.5.json`
- `results/raw/2026-07-03-llm-jp-4-8b-instruct-llm-jp-eval-jcommonsenseqa-full-v2.1.5.console.log`

`results/raw/` is intentionally ignored by git, so this report preserves the committed summary and the raw files remain
local evidence.

## #64 Completion Impact

Layer 3 is now covered by an official `llm-jp-eval` dataset full split. #64 still needs the following before final
completion:

- Layer 4 custom task evaluation at golden/rubric level
- Human approval to append the final or revised row to `results/results.csv`
- Final `adopt` / `hold` / `reject` verdict and reasoning after comparing the full Layer 3 and Layer 4 results
