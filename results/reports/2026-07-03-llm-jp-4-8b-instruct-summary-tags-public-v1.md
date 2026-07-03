# llm-jp-4-8b-instruct summary/tag custom task evaluation

Date: 2026-07-03
Model issue: #64
Environment: `mac`
Runtime: `ollama`

## Scope

Layer 4 自前タスク評価として、公開可能な架空サンプルだけを使う要約・タグ付け golden task set を実行した。
smoke ではなく、複数ケースの golden input と固定 marker rubric で schema / summary / tags を採点する。

- Task set: `datasets/golden/samples/summary-tags-public-v1.yaml`
- Task set version: `summary-tags-public-v1`
- Judge / rubric: `deterministic-marker-rubric-v1`
- Tasks: 3 public synthetic cases
- Runtime model: `llm-jp-4-8b-instruct:latest`
- Stop sequence: `<|end|>`
- Runner: `harness.task.promptfoo.summary_tags_eval`

## Command

```bash
PYTHONPATH=. python3 -m harness.task.promptfoo.summary_tags_eval \
  --base-url http://127.0.0.1:11434/v1 \
  --model llm-jp-4-8b-instruct \
  --stop '<|end|>' \
  --output-json results/raw/2026-07-03-llm-jp-4-8b-instruct-summary-tags-public-v1.json
```

## Result

| Metric | Value |
|---|---:|
| `task_score` / mean score | `1.0` |
| Passed / total | `3 / 3` |
| Median tok/s | `48.008572410685474` |
| Median TTFT | `392.4070829998527 ms` |
| Schema weight | `0.2` |
| Summary rubric weight | `0.4` |
| Tags rubric weight | `0.4` |

Case breakdown:

| Case | Score | Passed |
|---|---:|---|
| `local-llm-eval-ops` | `1.0` | yes |
| `results-governance` | `1.0` | yes |
| `four-layer-onboarding` | `1.0` | yes |

## Row Candidate

`results/results.csv` へはまだ追記しない。Operations approval gate で承認された場合の final/revised row 候補は次の通り。

```csv
llm-jp-4-8b-instruct,7ae4da12cee2f109509cb8e1d01cf8a0f1a5fbc1,ollama,mac,summarize,q4_k_m,yes,65536,48.7303,185.477,,0.959786,1,,2026-07-03,adopt-candidate; stop=<|end|>; bench=llm-jp-eval-jcommonsenseqa-full-v2.1.5; task=summary-tags-public-v1; judge=deterministic-marker-rubric-v1; pass=3/3; ollama_id=d5bf362b9fd8; raw=2026-07-03-llm-jp-4-8b-instruct-summary-tags-public-v1.json
```

## Raw Evidence

Local raw file:

- `results/raw/2026-07-03-llm-jp-4-8b-instruct-summary-tags-public-v1.json`

`results/raw/` は gitignore 対象なので、raw はローカル証跡として残し、この report には集計結果だけを commit する。

## #64 Completion Impact

Layer 4 は golden / rubric 水準で完了した。Layer 3 も official `llm-jp-eval` dataset full split で完了済み。
残りは human Operations approval gate で final/revised row の `results/results.csv` 追記可否と最終
`adopt` / `hold` / `reject` verdict を決めること。
