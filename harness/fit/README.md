# harness/fit — Layer 1 Fit

目標 `max_model_len` で起動済みの OpenAI 互換サーバに短い推論を投げ、ロード可否を記録する。
OOM 系のエラーは `fit=oom`、その他の通信・推論エラーは `fit=error` として扱う。

```bash
python3 -m harness.fit.openai \
  --model qwen3-8b \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --append-results
```

注意:

- サーバ起動時の `max_model_len` / 量子化 / ランタイム条件を固定してから実行する。
- マルチモーダルモデルは、実入力を使った追加 probe を別途実行する。
- 結果は `results/results.csv` に追記する。既存行は変更しない。
