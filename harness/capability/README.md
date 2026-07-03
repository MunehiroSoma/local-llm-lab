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

`--metric-key` を省略した場合は、`--bench` 名から以下の代表スコアを推定する。

| bench | 既定の読み取り |
|---|---|
| `lm-eval*` / `mmlu*` / `gsm8k` / `hellaswag` | `results.<task>.acc_norm`、なければ `acc` / `exact_match` / `f1` の平均 |
| `llm-jp*` | `score` / `accuracy` / `summary.*` / `results.*`、または case 列の平均 |
| `vlmeval*` | `score` / `accuracy` / `overall` 系、または case 列の平均 |
| `aider*` | `pass_rate` / `percent_cases_passed` / `solved_rate` 系 |

明示的に固定したい場合は従来通り `--metric-key results.mmlu_pro.acc_norm` を指定する。

標準ベンチは採用判断の足切り・参考値であり、最終判断は `harness/task/` の自前タスク評価で行う。
