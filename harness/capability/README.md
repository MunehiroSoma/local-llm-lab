# harness/capability — Layer 3 Capability

lm-eval / llm-jp-eval / VLMEvalKit / Aider などの標準ベンチを実行したあと、代表スコアを
固定スキーマへ記録するための薄いアダプタ。

スコアを直接渡す例:

```bash
python3 -m harness.capability.run \
  --model qwen3-8b \
  --env mac \
  --bench llm-jp-eval \
  --score 0.62 \
  --append-results
```

外部ベンチの JSON から値を抜く例:

```bash
python3 -m harness.capability.run \
  --model qwen3-8b \
  --env mac \
  --bench mmlu-pro \
  --score-json results/raw/mmlu-pro.json \
  --metric-key results.mmlu_pro.acc_norm \
  --append-results
```

標準ベンチは採用判断の足切り・参考値であり、最終判断は `harness/task/` の自前タスク評価で行う。
