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

## 新モデルの通し方（run_onboarding.py で自動化予定）
`registry/models.yaml` に追加 → WhichLLM当たり付け → fit → speed → capability → task → `results/results.csv` 追記。

> judge モデルは固定（変えると過去比較が壊れる）。ゴールデンセットは版管理（datasets/）。
