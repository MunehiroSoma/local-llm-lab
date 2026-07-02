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
| `task/vlm/` | ④自分の用途 | VLM スモーク評価用の軽量マーカー判定 | OpenAI互換API |

## 新モデルの通し方（run_onboarding.py で自動化予定）
`registry/models.yaml` に追加 → WhichLLM当たり付け → fit → speed → capability → task → `results/results.csv` 追記。

> judge モデルは固定（変えると過去比較が壊れる）。ゴールデンセットは版管理（datasets/）。

## CLI

OpenAI互換サーバを起動してから、同じエンドポイントを各レイヤに渡す。

```bash
make fit MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1
make speed MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1
make capability MODEL=qwen3-8b ENV=mac BENCH=llm-jp-eval SCORE=0.62
make onboard MODEL=qwen3-8b ENV=mac BASE_URL=http://127.0.0.1:11434/v1
```

- `fit`: 短い推論でロード可否を判定し、OOM系エラーを `fit=oom` として記録する。
- `speed`: concurrency=1 の単発リクエストを複数回実行し、中央値の `tok_s` と `ttft_ms` を記録する。
- VLM の Fit/Speed は `--image <path>` を直接指定できる。OpenAI互換 chat payload の
  `image_url` data URL として送るため、Ollama などの OpenAI互換 endpoint で共通計測できる。
- Ollama の thinking 対応モデルは `content` が空で `reasoning` 側に生成が入ることがあるため、
  harness は streaming / non-streaming の両方で reasoning fallback を適用する。
- `capability`: lm-eval / llm-jp-eval / VLMEvalKit など外部ベンチの代表スコアを固定スキーマへ記録する。
- `task`: promptfoo / DeepEval / coding-agent 評価の補助スクリプトを置く。実データは `datasets/golden/` に置かない。

## Issue #1 のBOLT対応

| Issue | 実装 |
|---|---|
| #7 common | `harness/common/`: OpenAI互換HTTPクライアント、計測、registry解決、results追記 |
| #8 fit | `harness/fit/openai.py`: 短い推論によるロード可否/OOM分類 |
| #9 speed | `harness/speed/openai.py`: TTFT・tok/s中央値計測 |
| #10 capability | `harness/capability/run.py`: 標準ベンチ代表スコア記録 |
| #11 promptfoo | `harness/task/promptfoo/`: 要約・タグ JSON schema/rubric 雛形 |
| #12 deepeval | `harness/task/deepeval/`: G-Eval/agent metric 集計 |
| #13 coding-agent | `harness/task/coding_agent/`: 仕様書駆動 eval case runner |
| #14 onboarding | `harness/run_onboarding.py`: fit→speed→results 追記 |
