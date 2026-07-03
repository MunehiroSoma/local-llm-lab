# harness — 評価ハーネス（モデル非依存）

research §12.4–12.10 の実装場所。すべて **OpenAI互換API** 越しにモデルを叩く（ADR 0002）。

| ディレクトリ | レイヤ | 役割 | 主ツール |
|---|---|---|---|
| `common/` | 共通 | OpenAI互換クライアント・計測・結果追記 | — |
| `fit/` | ①載る | 目標 max_model_len でOOM判定（実ロード） | 各ランタイム |
| `speed/` | ②速い | 単発 tok/s・TTFT・MM前処理時間 | vllm bench / genai-perf / llama-bench / LocalScore |
| `capability/` | ③賢い(標準) | 標準ベンチ足切り | lm-eval-harness / Aider / VLMEvalKit / llm-jp-eval |
| `task/promptfoo/` | ④自分の用途 | タグ/要約（JSONスキーマ+rubric） | promptfoo |
| `task/deepeval/` | ④自分の用途 | コーディング/コンシェルジュ（G-Eval・agent指標） | DeepEval |
| `task/coding-agent/` | ④自分の用途 | 仕様書駆動開発（テスト実行+差分rubric） | Aider/OpenHands + Langfuse |
| `task/vlm/` | ④自分の用途 | VLM スモーク/スクリーンショット評価用の軽量マーカー判定 | OpenAI互換API |

## 新モデルの通し方（run_onboarding.py）
`registry/models.yaml` に追加 → WhichLLM当たり付け → fit → speed → capability → task → ResultRow 生成。

`results/results.csv` は append-only なので、通常の onboarding は row を stdout / raw report に出すだけにする。
Operations approval gate 後にだけ `--append-results` を明示して追記する。

> judge モデルは固定（変えると過去比較が壊れる）。ゴールデンセットは版管理（datasets/）。

## CLI

OpenAI互換サーバを起動してから、同じエンドポイントを各レイヤに渡す。

```bash
make fit MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1
make speed MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1
make capability MODEL=qwen3-8b ENV=mac BENCH=llm-jp-eval SCORE=0.62
make onboard MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1
make onboard MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1 \
  ONBOARD_ARGS="--capability-bench llm-jp-eval --capability-score-json results/raw/qwen3-8b-capability.json --raw-dir results/raw"
python3 -m harness.task.vlm.screenshot_eval --outputs results/raw/sample-vlm-outputs.json
python3 -m harness.task.vlm.screenshot_eval \
  --model gemma4-26b-a4b \
  --base-url http://127.0.0.1:11434/v1 \
  --raster-dir results/raw/vlm-screenshot-v1-png
python3 -m harness.task.coding_agent.run_case \
  --model qwen3-coder-30b-a3b \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --env mac \
  --output-json results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

- `fit`: 短い推論でロード可否を判定し、OOM系エラーを `fit=oom` として記録する。
- `speed`: concurrency=1 の単発リクエストを複数回実行し、中央値の `tok_s` と `ttft_ms` を記録する。
- VLM の Fit/Speed は `--image <path>` を直接指定できる。OpenAI互換 chat payload の
  `image_url` data URL として送るため、Ollama などの OpenAI互換 endpoint で共通計測できる。
- Ollama の thinking 対応モデルは `content` が空で `reasoning` 側に生成が入ることがあるため、
  harness は streaming / non-streaming の両方で reasoning fallback を適用する。
- `capability`: lm-eval / llm-jp-eval / VLMEvalKit など外部ベンチの代表スコアを固定スキーマへ記録する。
- `task`: promptfoo / DeepEval / coding-agent 評価の補助スクリプトを置く。実データは `datasets/golden/` に置かない。
- `onboard`: fit → speed → capability score 取り込み → `summary-tags-public-v1` task を 1 コマンドで集約し、
  final/revised 相当の ResultRow を JSON で stdout に出す。`--append-results` がない限り
  `results/results.csv` には追記しない。
- `task/vlm/screenshot_eval.py`: 公開サンプルの synthetic screenshot task set を OpenAI互換APIで実行し、
  marker/alias/threshold で決定論的に採点する。モデル実行済みの JSON 出力を `--outputs` で後採点することもできる。
  SVG を受け付けない endpoint では `--raster-dir results/raw/...` で PNG に変換してから実行する。
- `task/coding_agent/run_case.py`: `coding-agent-public-v1` の公開 synthetic spec から JSON patch を生成させ、
  必須ファイル、marker、公開 pytest を固定 rubric で採点する。`qwen3-coder-30b-a3b` と `devstral-small-2` は
  `--model` だけ差し替えて同じ Layer 4 coding 評価に通せる。

## Mac/Ollama onboarding

MacBook Pro では Ollama の OpenAI互換 endpoint が動いている場合だけ実測する。

```bash
make env-mac-ollama OLLAMA_MODEL=qwen3:8b
python3 -m harness.run_onboarding \
  --model qwen3-8b \
  --env mac \
  --runtime ollama \
  --profile summarize \
  --quantization q4_k_m \
  --base-url http://127.0.0.1:11434/v1 \
  --capability-bench llm-jp-eval \
  --capability-score-json results/raw/qwen3-8b-llm-jp-eval.json \
  --raw-dir results/raw
```

capability の実測 JSON がまだない場合は `--capability-bench` を省略してもよい。その場合でも fit/speed と
`summary-tags-public-v1` task の row は生成される。task をライブ実行せず既存 output だけ採点する場合は
`--task-outputs results/raw/<model>-summary-tags-outputs.json` を使う。

Operations approval gate 後に CSV へ追記する場合だけ、同じコマンドへ `--append-results` を追加する。
RTX / DGX / CUDA / vLLM-Omni の実測は MacBook Pro では完了扱いにしない。別 BOLT で対象環境上で実施する。

## Issue #1 のBOLT対応

| Issue | 実装 |
|---|---|
| #7 common | `harness/common/`: OpenAI互換HTTPクライアント、計測、registry解決、results追記 |
| #8 fit | `harness/fit/openai.py`: 短い推論によるロード可否/OOM分類 |
| #9 speed | `harness/speed/openai.py`: TTFT・tok/s中央値計測 |
| #10 capability | `harness/capability/run.py` + `harness/capability/adapters.py`: 標準ベンチ代表スコア抽出・記録 |
| #11 promptfoo | `harness/task/promptfoo/`: 要約・タグ JSON schema/rubric 雛形 |
| #12 deepeval | `harness/task/deepeval/`: G-Eval/agent metric 集計 |
| #13 coding-agent | `harness/task/coding_agent/`: 仕様書駆動 eval case runner |
| #14 onboarding | `harness/run_onboarding.py`: fit→speed→results 追記 |
