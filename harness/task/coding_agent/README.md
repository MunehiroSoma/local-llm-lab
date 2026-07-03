# harness/task/coding_agent — Spec-Driven Coding Agent Eval

coding profile の Layer 4 用に、公開 synthetic spec から小さな Python patch を生成させる評価。
外部 Aider / OpenHands には依存せず、OpenAI互換 API の coding model を直接評価できる。

## 評価軸

task set は `coding-agent-public-v1`。公開サンプルは
`datasets/golden/samples/coding-agent-public-v1.yaml` に固定する。

モデルは JSON のみを返す。

```json
{"files":[{"path":"relative/path.py","content":"full file content"}],"notes":"optional"}
```

scorer は各 task を一時ディレクトリに展開し、次の固定 rubric を同じ重みで `task_score` に変換する。

| 軸 | 内容 |
|---|---|
| schema | `files[].path/content` の JSON schema を満たす |
| files | 必須ファイル名が揃っている |
| markers | 必須関数名や実装上の marker を含む |
| tests | task に同梱した公開 pytest が成功する |

raw 証跡は `--output-json results/raw/...json` に保存できる。`results/raw/` は gitignore 対象なので commit しない。
`--append-results` を付けた場合だけ `results/results.csv` に追記する。

## 後採点

モデル実行済み output を採点する。

```bash
python3 -m harness.task.coding_agent.run_case \
  --outputs results/raw/qwen3-coder-30b-a3b-coding-agent-outputs.json \
  --model qwen3-coder-30b-a3b \
  --runtime mlx \
  --env mac \
  --output-json results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

`--outputs` は task id から文字列への mapping、または `[{ "id": "...", "output": "..." }]` を受け付ける。

## OpenAI互換 API 実行

MacBook Pro で OpenAI互換 endpoint が動いている場合だけ実測する。

```bash
python3 -m harness.task.coding_agent.run_case \
  --base-url http://127.0.0.1:11434/v1 \
  --model qwen3-coder-30b-a3b \
  --runtime ollama \
  --env mac \
  --profile coding \
  --output-json results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

`devstral-small-2` も同じ物差しで実行する。

```bash
python3 -m harness.task.coding_agent.run_case \
  --base-url http://127.0.0.1:11434/v1 \
  --model devstral-small-2 \
  --runtime ollama \
  --env mac \
  --profile coding \
  --output-json results/raw/devstral-small-2-coding-agent-public-v1.json
```

Operations approval gate 前に `results/results.csv` へ追記しない。追記する場合は、生成される row を先に提示して承認を取る。
