# harness/speed — Layer 2 Speed

OpenAI 互換サーバに concurrency=1 の単発リクエストを複数回送り、中央値の `tok_s` と `ttft_ms`
を `results/results.csv` に追記する。

```bash
python3 -m harness.speed.openai \
  --model qwen3-8b \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --repeats 3 \
  --warmups 1 \
  --append-results
```

測定方針:

- streaming 対応サーバでは最初の content delta を TTFT とする。
- usage の `completion_tokens` が返る場合はそれを使う。返らない場合は簡易推定で補う。
- 画像・音声・動画の前処理時間は `--mm-preprocess-ms` で別指標として記録する。
