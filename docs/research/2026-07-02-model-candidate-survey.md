# 2026-07-02 モデル候補調査メモ

## 目的

Mac M4 Pro / RTX 5060 Ti / RTX 5070 / DGX Spark で比較する候補モデルを、
提供元・地域/言語圏・パラメータ規模・量子化/ローカル実行経路の観点で整理する。
本メモは候補スナップショットであり、採用判断ではない。採用判断は `results/results.csv`
に追記した fit / speed / task の実測で行う。

## 分類軸

- **提供元の地域**: 中国系 / 英語圏・欧米系 / 日本製 / 日本語特化だが非日本製
- **用途**: coding / concierge / summarize-tagging / VLM / omni / lightweight
- **Mac 実行性**: Ollama, MLX, MLX-VLM, llama.cpp/GGUF を優先。vLLM は主に RTX/DGX 側。
- **量子化**: 公式または配布元が GGUF / MLX / ONNX / QAT / compressed 形式を提供しているか。

## 候補一覧

| 分類 | モデル | 提供元 | 規模 | 量子化/ローカル経路 | このラボでの扱い |
|---|---|---|---:|---|---|
| 日本語特化・非日本製 | `LFM2.5-1.2B-JP-202606` | Liquid AI | 1.17B | GGUF / MLX / ONNX / vLLM / SGLang | Mac 第一波。日本語軽量・構造化出力の主候補 |
| 日本製 | `llm-jp-4-8b-instruct` | LLM-jp / NII | 約8.6B | BF16。GGUF はコミュニティ変換を確認 | Mac 第二波。日本製 8B ベースライン |
| 日本製 | `Llama-3.1-Swallow-8B-v0.5` | Science Tokyo / AIST | 8B | HF weights。GGUF/MLX は別途確認 | 日本製 8B 代替候補 |
| 日本製 | `TinySwallow-1.5B-Instruct` | Sakana AI | 1.5B | GGUF 派生あり | 超軽量日本語の比較候補。LFM と競合 |
| 日本製 | `RakutenAI-2.0-mini-instruct` | Rakuten | 1.5B | HF weights。GGUF 派生あり | 超軽量日本語の比較候補。優先度は LFM より下 |
| 中国系 | `qwen3-8b` | Alibaba Qwen | 8.2B | HF / GGUF / Ollama 等 | 多言語・日本語・構造化出力の 8B 基準 |
| 中国系 | `qwen2.5-vl-7b` | Alibaba Qwen | 7B | HF / vLLM / SGLang / 量子化派生 | Mac 第一波 VLM 候補。MLX-VLM 可否を確認 |
| 中国系 | `qwen3-coder-30b-a3b` | Alibaba Qwen | 30.5B total / 3.3B active | Ollama / GGUF / vLLM 系 | Mac coding 第一波。MoE が Mac 帯域で効くか確認 |
| 中国系 | `qwen3.6-35b-a3b` | Alibaba Qwen 想定 | 35B total / 3B active 想定 | 要確認 | 公式/配布元確認が済むまで保留 |
| 英語圏・欧米系 | `gemma4-12b` | Google DeepMind | 12B | 16-bit / QAT Q4 / MLX 派生あり | Mac 第一波 general/VLM 候補 |
| 英語圏・欧米系 | `gemma4:e4b` | Google DeepMind / Ollama | E4B | Ollama | smoke test 用。比較対象ではない |
| 英語圏・欧米系 | `devstral-small-2` | Mistral AI | 24B | HF / Ollama / quantized 派生 | Mac coding 第二波。Qwen Coder と比較 |
| 英語圏・欧米系 | `ministral-3-14b` | Mistral AI | 14B | compressed / FP8 等 | general/VLM 第二波 |
| omni | `minicpm-o-4.5` | OpenBMB | 9B | vLLM-Omni / llama.cpp-omni 系 | RTX 5060 Ti / DGX 側。Mac 第一波から除外 |
| omni | `qwen3-omni-30b-a3b` | Alibaba Qwen | 30B total / 3B active | vLLM-Omni | DGX 側。Mac 第一波から除外 |

## Mac M4 Pro で今回試す候補

優先順位は「小さく確実に動く → 日本語/構造化 → VLM → coding」の順にする。

| 優先 | モデル | 目的 | 期待する実行経路 | 判定したいこと |
|---|---|---|---|---|
| A | `LFM2.5-1.2B-JP-202606` | 日本語軽量 / 構造化出力 | MLX または llama.cpp/GGUF、可能なら Ollama | 日本語・JSON・日英混在の低遅延基準になるか |
| A | `qwen3-8b` | 多言語/日本語 8B 基準 | Ollama / MLX / llama.cpp | LFM との差分、構造化出力の安定性 |
| A | `qwen2.5-vl-7b` | 画像+テキスト | MLX-VLM | Mac の VLM 実力ラインになるか |
| A | `gemma4-12b` | general / VLM / concierge | MLX-VLM または Ollama | Google 系の品質基準。Mac で現実的な速度か |
| B | `qwen3-coder-30b-a3b` | coding | Ollama/GGUF、可能なら MLX | MoE 活性3.3B が Mac の帯域制約に効くか |
| B | `llm-jp-4-8b-instruct` | 日本製 8B baseline | Transformers/vLLM、GGUF 派生 | 日本製モデルとして LFM/Qwen と比べる価値があるか |
| B | `devstral-small-2` | coding | Ollama/GGUF | Qwen Coder に対する欧州系 coding baseline |

`gemma4:e4b` は既にこの Mac にあるため、ランタイム smoke test には使う。ただし比較対象には含めない。

## 再検討条件

- 他環境（RTX 5060 Ti / RTX 5070 / DGX Spark）で fit/speed が出たとき
- GGUF / MLX / Ollama の公式または高品質な変換が追加されたとき
- registry の候補が model onboarding で `onboarded` になったとき
- 日本語の自前 task 評価で LFM / LLM-jp / Swallow / Qwen の順位が変わったとき

## 参照

- Liquid AI: <https://docs.liquid.ai/lfm/models/lfm25-1.2b-jp>
- LiquidAI/LFM2.5-1.2B-JP-202606: <https://huggingface.co/LiquidAI/LFM2.5-1.2B-JP-202606>
- Qwen3: <https://qwenlm.github.io/blog/qwen3/>
- Qwen2.5-VL: <https://qwen.ai/blog?id=qwen2.5-vl>
- Qwen/Qwen3-8B: <https://huggingface.co/Qwen/Qwen3-8B>
- Qwen/Qwen2.5-VL-7B-Instruct: <https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct>
- Google Gemma 4 model card: <https://ai.google.dev/gemma/docs/core/model_card_4>
- Google Gemma releases: <https://ai.google.dev/gemma/docs/releases>
- Mistral 3: <https://mistral.ai/news/mistral-3/>
- Devstral Small 2: <https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512>
- LLM-jp-4 release: <https://www.nii.ac.jp/en/news/release/2026/0403.html>
- llm-jp-4-8b-instruct: <https://huggingface.co/llm-jp/llm-jp-4-8b-instruct>
- Llama 3.1 Swallow 8B v0.5: <https://swallow-llm.github.io/llama3.1-swallow-8B-v0.5.ja.html>
- TinySwallow-1.5B-Instruct: <https://huggingface.co/SakanaAI/TinySwallow-1.5B-Instruct>
- RakutenAI-2.0-mini-instruct: <https://huggingface.co/Rakuten/RakutenAI-2.0-mini-instruct>
