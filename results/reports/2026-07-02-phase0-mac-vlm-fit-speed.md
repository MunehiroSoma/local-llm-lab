# Phase0 Mac VLM fit/speed report

Parent issue: #3
BOLT: #19
Date: 2026-07-02
Environment: `mac`

## Environment

| Item | Result |
|---|---|
| Host | MacBook Pro / Apple M4 Pro / 48 GB unified memory |
| macOS | 26.5 |
| Ollama | 0.31.1; OpenAI-compatible API reachable at `http://127.0.0.1:11434/v1` |
| MLX-VLM | `~/.venv-mlxvlm`, Python 3.12.9 arm64, `mlx_vlm` 0.6.3; actual model run OK |

## Ollama VLM baseline

| Model | Runtime | Quantization | Fit | tok/s | TTFT | Notes |
|---|---|---|---|---:|---:|---|
| `gemma4-26b-a4b` | Ollama | `q4_k_m` | `yes` | `63.6827` | `336.399ms` | local alias for `gemma4:26b`; Ollama model id `5571076f3d70`; image+text smoke |
| `gemma4-26b-a4b` | Ollama | `q4_k_m` | `yes` | `62.7975` | `356.383ms` | CC0 periodic table image; OCR smoke for selected element symbols/numbers |

The smoke image is a generated 64x64 four-color PNG kept in ignored raw results. The model identified it as a 2x2 grid of red, blue, green, and yellow squares.

The richer Web image is `Simple Periodic Table Chart-en.svg`, rendered to a 1280px PNG from Wikimedia Commons. It is CC0 / public domain dedication by Offnfopt. For the OCR smoke prompt, the model correctly read:

- Hydrogen: `H`, atomic number `1`
- Carbon: `C`, atomic number `6`
- Oxygen: `O`, atomic number `8`
- Gold: `Au`, atomic number `79`

Gemma4 streams reasoning deltas through Ollama. The harness now counts `delta.reasoning` as generated text when `delta.content` is empty, so the reported speed includes reasoning output.
The same fallback is applied to non-streaming `message.reasoning`, because Gemma4 can return an empty
`message.content` through Ollama's OpenAI-compatible endpoint.

## 8-image VLM task set

The image catalog is tracked in `results/reports/2026-07-02-vlm-image-task-set.md`. Source images and raw
measurement logs are kept under ignored `results/raw/`.

Conditions:

- Model: `gemma4-26b-a4b`
- Runtime: Ollama OpenAI-compatible API
- Quantization: `q4_k_m`
- `max_model_len`: `128000`
- Speed run: warmups `1`, repeats `3`, `max_tokens=180`
- Verification run: non-streaming, `max_tokens=320`; `earth-water-distribution` used `640` to avoid truncating
  the freshwater breakdown

Aggregate:

| Model | Tasks | Pass | Review | Error | Median tok/s | Median TTFT |
|---|---:|---:|---:|---:|---:|---:|
| `gemma4-26b-a4b` | 8 | 8 | 0 | 0 | `59.3692` | `389.411ms` |

Per-task results:

| Task | Pattern | Status | tok/s | TTFT | Marker score |
|---|---|---|---:|---:|---:|
| `periodic-table` | Dense table OCR | `pass` | `58.8822` | `389.566ms` | `1.00` |
| `morse-code` | Symbol table lookup | `pass` | `59.8562` | `389.008ms` | `1.00` |
| `earth-water-distribution` | Chart / infographic reasoning | `pass` | `60.4620` | `382.134ms` | `1.00` |
| `cdc-stop-germs` | Poster instruction extraction | `pass` | `60.3811` | `430.449ms` | `1.00` |
| `us-map-labels` | Map label spatial reasoning | `pass` | `60.4862` | `378.855ms` | `1.00` |
| `nasa-mission-control` | Scene understanding | `pass` | `51.2723` | `389.256ms` | `1.00` |
| `intellipedia-screenshot` | UI / document OCR | `pass` | `42.3492` | `413.679ms` | `1.00` |
| `stop-sign` | Sign OCR / safety semantics | `pass` | `36.4844` | `436.560ms` | `1.00` |

Observed image/task hygiene:

- Transparent SVG renders can collapse to black in downstream viewers or preprocessing. `morse-code` and
  `us-map-labels` were flattened onto white backgrounds before the accepted run.
- The NASA scene-understanding image was replaced with a true Mission Operations Control Room photo after the first
  candidate proved to be an exterior/architectural image.
- Marker scoring now supports alias groups for lightweight checks, but this remains a smoke task set rather than a
  full MMMU-style benchmark.

## MLX-VLM actual model smoke

`mlx-community/gemma-3-4b-it-4bit` was used as the MLX-VLM actual-model smoke because it is small enough for a quick
runtime check and is published as an MLX-VLM-compatible 4-bit model.

| Model | Runtime | Quantization | Fit | Task | Generation tok/s | Prompt tok/s | Peak memory | Notes |
|---|---|---|---|---|---:|---:|---:|---|
| [`mlx-community/gemma-3-4b-it-4bit`](https://huggingface.co/mlx-community/gemma-3-4b-it-4bit) | MLX-VLM 0.6.3 | `4bit` | `yes` | `stop-sign` | `88.794` | `200.810` | `5.401GB` | cached 3-run median; output read `STOP`, octagon, red, stop meaning |

Raw logs:

- `results/raw/2026-07-02-phase0-mac-mlx-vlm-gemma-3-4b-it-4bit-stop-sign-repeats.txt`
- `results/raw/2026-07-02-phase0-mac-mlx-vlm-gemma-3-4b-it-4bit-stop-sign-summary.json`

Rejected attempt:

- [`mlx-community/gemma-4-e4b-it-4bit`](https://huggingface.co/mlx-community/gemma-4-e4b-it-4bit) downloaded but failed
  during MLX-VLM load with a weight/config mismatch: `ValueError: Received parameters not in model` for
  `language_model` layers 24-41. Raw log:
  `results/raw/2026-07-02-phase0-mac-mlx-vlm-gemma-4-e4b-it-4bit-stop-sign.txt`.

## Appended results rows

After Operations approval, the representative result rows below were appended to `results/results.csv` with a
`hold` decision. The preliminary four-color and periodic-table smoke rows remain report-only evidence.

```csv
gemma4-26b-a4b,,ollama,mac,vlm,q4_k_m,yes,128000,59.3692,389.411,,,1,,2026-07-02,hold; phase0 mac vlm public-image-task-set-8; pass=8/8; sources=wikimedia-commons-public-domain-or-cc0; reasoning_tokens_included; nonstream_reasoning_included; raw=2026-07-02-phase0-mac-gemma4-26b-a4b-vlm-task-set-results.json
mlx-community/gemma-3-4b-it-4bit,,mlx-vlm,mac,vlm,4bit,yes,,88.794,,,,1,,2026-07-02,hold; phase0 mac mlx-vlm stop-sign-smoke; prompt_tok_s=200.810; peak_memory_gb=5.401; output_pass; gemma-4-e4b-it-4bit-load_error; raw=2026-07-02-phase0-mac-mlx-vlm-gemma-3-4b-it-4bit-stop-sign-summary.json
```

## Scope notes

- `qwen3.6-35b-a3b` remains blocked by source/model confirmation and is not a VLM target for this image+text run.
- `mm_preprocess_ms` is blank because the Ollama OpenAI-compatible API does not expose image preprocessing time separately; TTFT includes the image path overhead seen by the endpoint.
