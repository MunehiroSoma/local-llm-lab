# ADR 0008: モデル候補は環境別の暫定スナップショットとして扱う

- ステータス: accepted
- 日付: 2026-07-02

## 背景 / 課題

#2 の環境構築を進める前に、Mac M4 Pro で試すモデル候補を整理する必要がある。
ただし、モデル候補は 2026-07-02 時点でも変化が速く、Mac だけで決めると
RTX 5060 Ti / RTX 5070 / DGX Spark の fit/speed 結果と矛盾する可能性がある。

また、モデルは「中国系 / 英語圏・欧米系 / 日本製 / 日本語特化だが非日本製」のように
提供元や言語特化の軸が混ざる。`LFM2.5-1.2B-JP-202606` は日本語特化だが、
提供元は Liquid AI であり、日本製モデルとは別枠で扱う。

## 決定

モデル候補は **採用決定ではなく、2026-07-02 時点の暫定候補スナップショット** として扱う。
詳細な候補表は [`docs/research/2026-07-02-model-candidate-survey.md`](../research/2026-07-02-model-candidate-survey.md) に置く。

Mac M4 Pro の第一波は以下を優先する。

| 優先 | モデル | 位置づけ |
|---|---|---|
| A | `LFM2.5-1.2B-JP-202606` | 日本語軽量・構造化出力の第一候補 |
| A | `qwen3-8b` | 多言語/日本語 8B 基準 |
| A | `qwen2.5-vl-7b` | Mac VLM 実力ライン |
| A | `gemma4-12b` | 英語圏・Google 系 general/VLM 基準 |
| B | `qwen3-coder-30b-a3b` | Mac coding MoE 候補 |
| B | `llm-jp-4-8b-instruct` | 日本製 8B baseline |
| B | `devstral-small-2` | 欧州系 coding baseline |

`gemma4:e4b` はこの Mac に既にある smoke test 用モデルとして使うが、比較対象モデルには含めない。

`qwen3.6-35b-a3b` は公式/配布元確認が済むまで比較対象から外し、候補保留とする。

## 理由 / 代替案

- LFM は 1.2B 級で、Mac の低遅延・省電力・日本語構造化出力の基準として有用。
- Qwen3 8B と Qwen2.5-VL 7B は、中国系の多言語/構造化/VLM 基準として比較しやすい。
- Gemma 4 12B は、英語圏・Google 系の general/VLM 品質基準として置く。
- coding は Qwen3 Coder 30B-A3B と Devstral Small 2 を比較する。Mac では dense 大型より MoE/量子化の実測が重要。
- 日本製枠は LFM と混同しない。LLM-jp-4 8B、Swallow、TinySwallow、RakutenAI mini は
  日本製/国内研究開発モデルとして別枠で比較する。

代替案として、registry にある候補をすべて Mac 第一波に含める案もあるが、
ダウンロード量・実測時間・ランタイム差分が大きくなりすぎるため採用しない。

## 影響

- `envs/mac/README.md` には現在の Mac 候補だけを載せる。
- model onboarding は #4 配下の BOLT で行う。revision 固定、fit/speed/task 実測、`results/results.csv` 追記は
  環境構築 #15 ではなく model onboarding 側の責務とする。
- 他環境の結果が出たら、この ADR は supersede して候補表を更新する。
