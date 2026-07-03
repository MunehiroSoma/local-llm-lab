# envs/mac — Mac M4 Pro runtime

Parent: #2 / BOLT: #15

Mac M4 Pro は常時手元の画像+テキスト評価ホストとして使う。フル omni は対象外。
このディレクトリは、Ollama(OpenAI互換) を共通基準ライン、MLX-VLM を Apple Silicon 実力ラインとして扱う。
追加の導入対象として、GGUF/Metal の低レイヤ比較に `llama.cpp`、OpenAI互換サーバ比較に
`vLLM Metal` も扱う。

## モデル方針

`gemma4:e4b` は smoke test 用のローカル既存モデルであり、比較対象モデルではない。
Mac 第一波の比較対象は 2026-07-02 時点の候補スナップショットであり、採用決定ではない。
候補の理由と再検討条件は [ADR 0008](../../docs/adr/0008-model-candidate-snapshot-2026-07-02.md) と
[調査メモ](../../docs/research/2026-07-02-model-candidate-survey.md) に残す。

| 優先 | 用途 | 比較対象 | 主ランタイム | 理由 |
|---|---|---|---|---|
| A | Japanese lightweight / structured | `lfm2.5-1.2b-jp-202606` | MLX / llama.cpp / Ollama | 日本語特化1.2B級。軽量・省電力・構造化出力の第一候補 |
| A | summarize / tagging | `qwen3-8b` | Ollama / MLX | 多言語・日本語・構造化出力の8B基準 |
| A | VLM | `qwen2.5-vl-7b` | MLX-VLM | 文書・画像入力の定番軽量 VLM |
| A | concierge / VLM | `gemma4-12b` | Ollama / MLX-VLM | 英語圏・Google系の general/VLM 品質基準 |
| B | coding | `qwen3-coder-30b-a3b` | Ollama / llama.cpp / MLX | MoE活性3.3B級で Mac の帯域制約に合うか確認 |
| B | Japan-made baseline | `llm-jp-4-8b-instruct` | Transformers / llama.cpp / Ollama | 日本製8B baseline。LFMとは別枠 |
| B | coding baseline | `devstral-small-2` | Ollama / llama.cpp | 欧州系 coding baseline |

#15 の完了条件は、上記モデルを評価できる Mac ランタイムの起動手順を固定すること。
各モデルの revision 固定、fit/speed/task の実測、`results/results.csv` への追記は #4 配下の
model onboarding BOLT で扱う。
`llama.cpp` と `vLLM Metal` の導入・実測は #85 の追補 BOLT として扱い、既存の
Ollama / MLX-VLM 結果とは runtime を分けて記録する。

## 前提

- macOS / Apple Silicon arm64
- `uv`
- Ollama
- MLX-VLM 用は arm64 Python 3.12
- llama.cpp 用は Xcode Command Line Tools / CMake / Metal 対応 build
- vLLM Metal 用は arm64 Python 3.12 / Rosetta 不可

## 1. 環境確認

```bash
bash envs/mac/check.sh
```

確認するもの:

- macOS / arm64 で動いていること
- Mac のチップとメモリ
- `uv` / `ollama` の有無
- Ollama API の起動状態
- MLX-VLM venv の有無

## ランタイム採用方針

| ランタイム | 位置づけ | 導入状態 |
|---|---|---|
| Ollama | 4環境横断の共通 baseline / 最短 smoke | 導入・実測済み |
| MLX-VLM | Mac の画像+テキスト実力ラン | 導入・実測済み |
| llama.cpp | GGUF/Metal の低レイヤ比較、Ollama との差分確認 | #85 で導入 |
| vLLM Metal | OpenAI互換サーバとしての Mac 実力ラン候補 | #85 で導入 |

`llama.cpp` はテキスト/GGUF と `llama-bench` の再現性を優先する。`vLLM Metal` は
OpenAI互換 endpoint と harness 連携を優先し、MLX-VLM / Ollama より速いかは自前実測で判断する。

## 2. Ollama を OpenAI 互換サーバとして起動

```bash
OLLAMA_MODEL=gemma4:e4b bash envs/mac/serve-ollama.sh
```

既定値:

- `OLLAMA_HOST=127.0.0.1:11434`
- `OLLAMA_MODEL=gemma4:e4b`
- OpenAI互換 base URL: `http://127.0.0.1:11434/v1`

既に Ollama が起動している場合、スクリプトは再起動せず API 疎通と model pull だけを行う。
比較実測時は、上のモデル方針に従って `OLLAMA_MODEL` を対象モデルのランタイム名に差し替える。

## 3. OpenAI互換 API の疎通確認

```bash
MODEL=gemma4:e4b BASE_URL=http://127.0.0.1:11434/v1 bash envs/mac/smoke-ollama.sh
```

このコマンドは Ollama の OpenAI互換 API を直接叩く疎通確認で、`results/results.csv` は変更しない。
結果採用フェーズでは、registry 上の model ID とランタイム側 model 名を揃えたうえで
`make fit` / `make speed` / `make onboard` を `--append-results` ありで実行する。

## 4. MLX-VLM venv を作る

```bash
bash envs/mac/setup-mlx-vlm.sh
```

既定値:

- venv: `~/.venv-mlxvlm`
- package: `mlx-vlm`

パッケージ版を固定したい場合:

```bash
MLX_VLM_PACKAGE='mlx-vlm==<version>' bash envs/mac/setup-mlx-vlm.sh
```

## 5. MLX-VLM 単発実行

```bash
source ~/.venv-mlxvlm/bin/activate
python -m mlx_vlm.generate \
  --model mlx-community/<model> \
  --image <image-path> \
  --prompt "画像を一文で説明してください。"
```

## 6. llama.cpp / vLLM Metal 追補

導入対象には含めるが、#15 時点では未固定。#85 では以下を最低条件にする。

- `llama.cpp`: Metal 有効 build、`llama-cli` smoke、`llama-bench` 単発速度、GGUF model revision
- `vLLM Metal`: arm64 Python 3.12 venv、OpenAI互換 server smoke、harness `fit` / `speed`
- `results/results.csv` へ追記する場合は、runtime を `llama.cpp` / `vllm-metal` として分ける

### 6.1 llama.cpp Metal

`llama.cpp` は macOS では Metal が既定で有効だが、再現性のため `-DGGML_METAL=ON` を明示する。
source/build/model cache は repo 外に置く。

```bash
bash envs/mac/setup-llamacpp-metal.sh
```

既定値:

- source: `~/.local/src/llama.cpp`
- ref: `b9850`
- build: `~/.local/src/llama.cpp/build`
- binary: `~/.local/src/llama.cpp/build/bin/llama-cli`, `llama-bench`, `llama-server`

smoke / bench 例:

```bash
~/.local/src/llama.cpp/build/bin/llama-cli \
  -hf LiquidAI/LFM2.5-1.2B-JP-202606-GGUF:Q4_K_M \
  -p '日本語でOKとだけ返してください。' \
  -n 8 \
  -ngl all \
  --single-turn \
  --no-display-prompt \
  --no-warmup

~/.local/src/llama.cpp/build/bin/llama-bench \
  -hf LiquidAI/LFM2.5-1.2B-JP-202606-GGUF:Q4_K_M \
  -p 128 \
  -n 64 \
  -r 3 \
  -o json
```

2026-07-03 の代表値は `results/reports/2026-07-03-mac-runtime-expansion.md` に記録する。
`llama-bench` の `-ngl` は数値のみ受け付けるため、全 offload は既定値 `-1` を使う。

### 6.2 vLLM Metal

vLLM Metal は Apple Silicon 用の vLLM plugin として扱い、NVIDIA CUDA vLLM とは runtime を分ける。
arm64 Python 3.12 の venv を repo 外の `~/.venv-vllm-metal` に作る。

```bash
bash envs/mac/setup-vllm-metal.sh
```

OpenAI互換 server の最小 smoke:

```bash
HOST=127.0.0.1 \
PORT=8008 \
VLLM_METAL_MODEL=Qwen/Qwen3-0.6B \
SERVED_MODEL_NAME=qwen3-0.6b \
MAX_MODEL_LEN=2048 \
bash envs/mac/serve-vllm-metal.sh
```

別 terminal から:

```bash
curl --fail --silent --show-error http://127.0.0.1:8008/v1/models

python3 -m harness.fit.openai \
  --model qwen3-0.6b \
  --env mac \
  --runtime vllm-metal \
  --base-url http://127.0.0.1:8008/v1 \
  --max-model-len 2048

python3 -m harness.speed.openai \
  --model qwen3-0.6b \
  --env mac \
  --runtime vllm-metal \
  --base-url http://127.0.0.1:8008/v1 \
  --max-model-len 2048 \
  --max-tokens 64 \
  --repeats 3 \
  --warmups 1
```

`qwen3-0.6b` は vLLM Metal 導入確認用の小型モデルであり、採用判断の比較対象ではない。
`results/results.csv` へ追記する場合は Operations approval gate を通す。

## 完了条件

- `bash envs/mac/check.sh` が Mac/arm64 とランタイム状態を表示できる
- `bash envs/mac/serve-ollama.sh` が `http://127.0.0.1:11434/v1` を用意できる
- `bash envs/mac/smoke-ollama.sh` で OpenAI互換 chat completions の疎通確認ができる
- MLX-VLM 用 venv の構築手順が repo 内に固定されている

## 追補対象

- llama.cpp の Metal build / bench 手順
- vLLM Metal の venv / server / OpenAI互換 smoke 手順
