# VLM image task set

Date: 2026-07-02
Parent issue: #3
BOLT: #19

The images are stored under `results/raw/` and are intentionally ignored by git. This tracked catalog records the source, license, and intended VLM task pattern.

| ID | Local path | Task pattern | Suggested prompt | Source / license |
|---|---|---|---|---|
| `periodic-table` | `results/raw/2026-07-02-vlm-periodic-table.png` | Dense table OCR | 水素、炭素、酸素、金の元素記号と原子番号を読み取る。 | [Wikimedia Commons `Simple Periodic Table Chart-en.svg`](https://commons.wikimedia.org/wiki/File:Simple_Periodic_Table_Chart-en.svg); CC0 |
| `morse-code` | `results/raw/2026-07-02-vlm-morse-code.png` | Symbol table lookup | SOS、A、N、5 のモールス符号を読み取る。 | [Wikimedia Commons `International Morse Code.svg`](https://commons.wikimedia.org/wiki/File:International_Morse_Code.svg); public domain; alpha flattened to white |
| `earth-water-distribution` | `results/raw/2026-07-02-vlm-earth-water-distribution.png` | Chart / infographic reasoning | 地球上の水の分布を階層的に要約し、淡水の内訳を説明する。 | [Wikimedia Commons / USGS](https://commons.wikimedia.org/wiki/File:Earth%27s_water_distribution.png); public domain |
| `cdc-stop-germs` | `results/raw/2026-07-02-vlm-cdc-stop-germs.png` | Poster instruction extraction | 感染予防のために推奨されている行動を箇条書きで抽出する。 | [Wikimedia Commons / CDC](https://commons.wikimedia.org/wiki/File:Stop_the_Spread_of_Germs_(CDC).png); public domain |
| `us-map-labels` | `results/raw/2026-07-02-vlm-us-map-labels.png` | Map label spatial reasoning | California、Texas、Florida、New York の位置関係を説明する。 | [Wikimedia Commons `Blank US map borders labels.svg`](https://commons.wikimedia.org/wiki/File:Blank_US_map_borders_labels.svg); public domain; alpha flattened to white |
| `nasa-mission-control` | `results/raw/2026-07-02-vlm-nasa-mission-control.jpg` | Scene understanding | 管制室の状況、人数、画面、作業環境を説明する。 | [Wikimedia Commons / NASA `Mission Operations Control Room during Apollo 13`](https://commons.wikimedia.org/wiki/File:Mission_Operations_Control_Room_during_Apollo_13.jpg); public domain |
| `intellipedia-screenshot` | `results/raw/2026-07-02-vlm-intellipedia-screenshot.png` | UI / document OCR | スクリーンショット内のページ種別、見出し、ナビゲーション要素を読む。 | [Wikimedia Commons `Screenshot-Intellipedia.png`](https://commons.wikimedia.org/wiki/File:Screenshot-Intellipedia.png); public domain mark |
| `stop-sign` | `results/raw/2026-07-02-vlm-stop-sign.png` | Sign OCR / safety semantics | 標識の文字、形、色、意味を説明する。 | [Wikimedia Commons / MUTCD](https://commons.wikimedia.org/wiki/File:Stop_sign.png); public domain |

Raw metadata is stored at `results/raw/2026-07-02-vlm-task-image-set.metadata.json`.

## Notes

- SVG-derived transparent PNGs can render unreadably against dark viewers or model preprocessing paths. `morse-code` and `us-map-labels` are flattened onto a white background in `results/raw/`.
- The first NASA candidate was an exterior/architectural image, so the task set uses the Apollo 13 Mission Operations Control Room image instead.
- Marker checks use alias groups for common wording differences, for example `salt` / `saline` and `Intellipedia` / `Intellipdia`.

## Usage

Example:

```bash
python3 -m harness.speed.openai \
  --model gemma4-26b-a4b \
  --env mac \
  --base-url http://127.0.0.1:11434/v1 \
  --runtime ollama \
  --profile vlm \
  --quantization q4_k_m \
  --max-model-len 128000 \
  --prompt "感染予防のために推奨されている行動を箇条書きで抽出する。" \
  --image results/raw/2026-07-02-vlm-cdc-stop-germs.png \
  --max-tokens 160 \
  --repeats 3 \
  --warmups 1 \
  --timeout-s 300
```
