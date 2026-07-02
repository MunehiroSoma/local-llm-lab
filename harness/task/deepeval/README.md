# harness/task/deepeval — G-Eval / Agent Metrics

DeepEval や LLM-as-judge の実行結果 JSON から、ケース単位スコアを平均して `task_score` にする。
rubric は固定し、judge モデルを変える場合は過去結果と比較しない。

```bash
python3 -m harness.task.deepeval.rubric \
  --report results/raw/deepeval-report.json \
  --metric-key score
```

想定 JSON:

```json
{
  "testCases": [
    {"name": "concierge-001", "score": 0.8},
    {"name": "concierge-002", "score": 0.6}
  ]
}
```
