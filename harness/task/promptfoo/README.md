# harness/task/promptfoo — Summary/Tag Eval

要約・タグ付け用途の自前評価。出力 JSON の形を固定し、promptfoo の `is-json` / JavaScript assertion /
LLM rubric で評価する。

```bash
npx promptfoo@0.121.17 eval -c harness/task/promptfoo/promptfooconfig.example.yaml
```

ローカルのスキーマ準拠だけを確認する場合:

```bash
python3 -m harness.task.promptfoo.evaluate_json \
  --output '{"summary":"要約","tags":["llm"]}'
```

公開サンプル golden set と固定 marker rubric で実モデルを評価する場合:

```bash
python3 -m harness.task.promptfoo.summary_tags_eval \
  --base-url http://127.0.0.1:11434/v1 \
  --model llm-jp-4-8b-instruct \
  --stop '<|end|>' \
  --output-json results/raw/summary-tags-public-v1.json
```

実データは公開リポジトリに置かない。公開できる最小例だけを `datasets/golden/samples/` に置く。
