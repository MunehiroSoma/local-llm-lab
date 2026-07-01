# ローカルLLM／マルチモーダル推論 フレームワーク比較・実証実験（PoC）設計書

> 種別: 事前調査・設計資料（Markdown）／実証実験(PoC)前フェーズ
> 初版: 2026-07-01 ／ 現版: v2（スコープ拡張反映）
> ステータス: 設計フェーズ（本版時点で実インストール・PoC は未実施。読み取り専用の確認のみ実施）
> 対象読者: 自分用ローカル推論基盤（コーディングエージェント／AIコンシェルジュ／要約・タグ付け）を構築・検証する本人／意思決定者

---

## 更新履歴（v1 → v2）

| 変更点 | 内容 |
|---|---|
| 対象ハードを確定 | 抽象2台＋DGX Spark → **具体4台**（Mac M4 Pro / RTX 5060 Ti機 / RTX 5070機 / DGX Spark） |
| **DGX Spark を維持** | v2で一度スコープ外にしかけたが**比較対象として継続**（本人指示） |
| スコープを拡張 | 「vLLM速度比較」→ **各環境で“現状の推奨フレームワーク”を選定し、使えるかをPoCで実証** |
| マルチモーダルを拡張 | 画像＋テキスト → **画像＋音声＋動画（omni）**。Gemma系ほか**複数モデル**を評価 |
| 主目的を確定 | **単発（single-stream）推論**が主。用途＝コーディングエージェント／コンシェルジュ／要約・タグ付け |
| 新セクション追加 | **モデル選定支援ツール**調査（§7）、**実証実験(PoC)計画**（§13） |
| ライセンス | **考慮不要**（本人指示） |

---

## 凡例：情報の出所と信頼度

| タグ | 意味 |
|---|---|
| 【公式】 | ベンダー公式（vLLM / NVIDIA / Apple / Google / Microsoft 等）確認済み |
| 【準公式】 | 公式org配下だがコミュニティ保守（`vllm-project/vllm-metal`, `vllm-omni` 等）、NVIDIA NGC |
| 【コミュニティ】 | 技術ブログ・フォーラム・GitHub・ベンチ記事。参考値・要再現 |
| 【推測】 | 筆者の推論・外挿。未検証 |
| 【要確認】 | 本資料内で確定できず、後続で一次情報確認が必要 |

> 情報鮮度: vLLM/vLLM-Omni・Blackwell(RTX50/GB10)・MLX・Gemma系は 2025–2026 に激しく更新。数値・対応は**構築当日に再確認**。tok/s 等の参考値は**必ず自前PoCで再現**してから判断に用いる。

---

## 1. 調査目的

**各環境で現状の推奨フレームワークを選定し、狙うマルチモーダル(omni)モデルが実際に動くか・単発推論として実用速度が出るかを実証実験(PoC)で確かめる**ための設計資料。速度“比較”も行うが、主眼は「自分の用途で使えるか」の検証。

- 用途（すべて**単発・自分専用**）:
  - **コーディングエージェント**（長文脈・ツール呼び出し・高速デコード。必要に応じ画面/画像理解）
  - **AIコンシェルジュ**（対話。画像・音声など複数モダリティ）
  - **文章の要約・タグ付け**（長入力・構造化出力・文書/画像理解）
- 検証軸:
  - 環境ごとの**推奨フレームワーク**は何か（vLLM一択ではない）
  - **omni（画像＋音声＋動画）**がどこまで実際に動くか（フレームワーク／モデル／VRAMの制約）
  - **単発の体感速度**（TTFT・デコード tok/s・マルチモーダル前処理時間）
  - どの環境にどのモデルを置くのが最適か（**モデル選定支援ツール**も活用）

### 1.1 最重要の前提（率直に）
1. **単発中心なら vLLM の最大の強み（高並列の継続バッチング）はほぼ効かない。** 選定軸は「マルチモーダル対応 × 量子化(FP8) × 使い勝手 × 単発速度」に移る。
2. **“フル omni（音声・動画入力＋音声出力）”は実質 CUDA 専用（vLLM-Omni）。** Mac(Apple Silicon)は**画像＋テキスト（＋音声入力の一部）まで**。→ 環境ごとに担当モダリティが変わる。
3. **単発速度はメモリ帯域律速。** 帯域: RTX5070 ~672 > RTX5060Ti ~448 ≈ M4 Pro ~273 ≈ DGX Spark 273 (GB/s)。**モデルが載るなら RTX 勢が速い。DGX Spark は“大きいモデルを載せられる”のが価値で、単発は速くない。**

---

## 2. 比較対象環境（確定4台）

| # | 環境 | CPU | システムRAM | GPU/加速 | GPU VRAM | メモリ帯域 | compute cap | 主ランタイム候補 |
|---|---|---|---|---|---|---|---|---|
| **①** | MacBook Pro **M4 Pro** | M4 Pro (10P+4E, 14core) | **48GB 統合** | 統合GPU(Metal)+ANE | 統合48GB | **~273 GB/s**【要確認】 | N/A(Metal) | MLX-VLM / Ollama(MLX) |
| **②** | **RTX 5060 Ti** 機 | Intel **i7-14700** | **32GB** | RTX 5060 Ti (Blackwell) | **16GB** GDDR7 | **~448 GB/s** | sm_120 | vLLM / vLLM-Omni / Ollama |
| **③** | **RTX 5070** 機 | Intel **i9-14900K** | **64GB** | RTX 5070 (Blackwell) | **12GB** GDDR7 | **~672 GB/s** | sm_120 | vLLM / vLLM-Omni / Ollama |
| **④** | **NVIDIA DGX Spark** | GB10 Arm 20core | 128GB 統合 | Blackwell 統合 | **128GB** 統合 | **273 GB/s** | sm_121 | vLLM / vLLM-Omni(CUDA13/NGC) |

- **本セッションは①（M4 Pro 48GB）上で稼働中**を確認。Ollama 0.30.8 導入済み・モデルあり。Python は 3.11.9（MLXネイティブ系は 3.12 venv 推奨）。
- ②③は Windows 想定 → **WSL2 + CUDA** で揃える（§9）。OS依存差を減らすため2台とも同一方式に。
- ④ DGX Spark は**手元にあり利用可能** → **omni の主軸ホスト**に据える（§13）。
- 面白い非対称: **VRAMが大きいのは②(16GB)**、**帯域が速いのは③(672GB/s)**、**RAMが多いのは③(64GB)**。→ 「載せやすさ＝②」「載れば速い＝③」。

---

## 3. 結論サマリー

### 3.1 環境 × 推奨フレームワーク（単発＋マルチモーダル）

| 環境 | 画像＋テキスト(VLM) | 音声入力 | 動画入力 | 音声出力(TTS/フル omni) | 推奨主フレームワーク |
|---|---|---|---|---|---|
| **① Mac M4 Pro** | ◎ MLX-VLM / Ollama(MLX) | △ Gemma4等一部 | ✕〜△ | ✕（CUDA前提のため不可に近い） | **MLX-VLM**（＋Ollamaを基準線） |
| **② RTX 5060 Ti 16GB** | ◎ vLLM(FP8) | ○ | ○(7B級) | ○(7B omni, 要source build) | **vLLM / vLLM-Omni** |
| **③ RTX 5070 12GB** | ◎ vLLM(FP8, 最速) | ○ | △(VRAM厳しめ) | △(12GBで7B omniは窮屈) | **vLLM**（VLM単発最速）|
| **④ DGX Spark 128GB** | ○ | ○ | ○ | ◎（大型omni可） | **vLLM-Omni**（大型omni／余裕）|

凡例: ◎=快適 / ○=可 / △=条件付き・窮屈 / ✕=不可に近い

### 3.2 役割分担（結論）
- **日常の単発ドライバ**: **③ RTX5070（載るモデルで最速）** と **② RTX5060 Ti（VLM/omniに余裕）**、および **① Mac（画像＋テキスト＋一部音声、常時手元）**。
- **大型 omni・動画・音声生成の担当**: **④ DGX Spark**（128GBで大型 omni を載せられる。単発は速くないが“載る”のが価値）。
- **フル omni は CUDA（vLLM-Omni）**が前提 → **Mac はフル omni の担当から外す**（画像＋テキスト＋音声入力の一部に限定）。

### 3.3 フレームワーク選定の指針
- **各環境の“実力上限”ラン**: Mac=MLX-VLM、NVIDIA/DGX=vLLM / vLLM-Omni（FP8/NVFP4）。
- **公平比較の“共通基準”ラン**: **Ollama は4台すべてで動く**（Mac=MLXバックエンド, NVIDIA=CUDA）→ apples-to-apples の基準線に最適。
- 単発用途なので、**まず Ollama で“動く/実用速度”を素早く確認 → 必要な環境だけ vLLM/vLLM-Omni/MLX-VLM で最適化**、が最短。

---

## 4. 環境別の実現可能性とフレームワーク選定

### 4.1 ① Mac M4 Pro 48GB
- **vLLM本体(CUDA)は不可**【公式】。Apple Silicon向けは (a)`vllm-metal`(MLX) (b)CPUモードvLLM(遅い)。だが**マルチモーダルの実務ラインは MLX-VLM / Ollama(MLX)**。
- **推奨**:
  - **MLX-VLM**: Apple Silicon 向けVLM実行の定番。**Gemma 3 は mlx-vlm に day-0 対応**、Qwen-VL/LLaVA等も可【コミュニティ/準公式】。
  - **Ollama 0.19+ の MLXバックエンド**（本機は 0.30.8）: 32GB+ 統合メモリでMLX直行、llama.cpp を迂回し**MLX性能をOllamaの手軽さで**【公式Ollama Blog】。**最短で着手可能**。
  - 参考: `vllm-mlx`（OpenAI/Anthropic互換, VLM対応, 400+ tok/s参考値）【コミュニティ】。
- **性能感（M4 Pro）**: 7B Q4 ~60–80 tok/s、13B ~35–50 tok/s（テキスト系）【コミュニティ参考値】。VLMは画像トークンで前処理が増える。
- **制約（曖昧にしない）**:
  - **フル omni（動画入力・音声出力）は Mac では実務的に困難**（vLLM-Omni は CUDA）。**画像＋テキストが主戦場、音声入力は Gemma 4 等で一部可**。
  - CUDA前提機能（FlashAttention CUDA実装 / CUDA Graphs / NVFP4 等）は非適用。量子化は**MLX量子化**で NVIDIA と非等価（§10）。
  - `vllm-metal` を使う場合は **arm64 Python 3.12 必須・Rosetta不可**【準公式】。本機は 3.11.9 のため **uv で 3.12 venv** を作る。
- **判断**: **画像＋テキストVLM（＋音声入力の実験）の常時手元機**。フル omni は担当外。

### 4.2 ② RTX 5060 Ti 16GB（i7-14700 / 32GB）
- **vLLM / vLLM-Omni が素直に動く**【公式/準公式】。Blackwell(sm_120)は **FP8ネイティブ** → **FP8が本命**（VRAM半減・品質~99%・速度ペナルティ小）【コミュニティ】。
- **16GB の効き**: VLM-7B〜14B級・**7B級 omni（Qwen2.5-Omni-7B 等）**を中程度コンテキストで搭載可【推測/要PoC】。画像・**動画トークンは重い**ので余裕は正義。
- **WSL2**: `nvidia-container-toolkit`＋Windows側新ドライバでGPUパススルー。ネイティブ比 ~5–15% 程度の低下【コミュニティ】。**②③とも WSL2 で揃える**。
- **判断**: **omni を含む“載せやすい”NVIDIA機**。フル omni PoC の主担当候補。

### 4.3 ③ RTX 5070 12GB（i9-14900K / 64GB）
- **VLM 単発は最速級**（帯域 ~672 GB/s）。Llama3.1-8B Q4 で ~75 tok/s 参考値【コミュニティ】。
- **12GB の制約**: VLM-7B(Q4/FP8)は快適。ただし**omni（音声・特に動画）の追加エンコーダ＋トークンで 12GB は窮屈**。大きめ文脈・複数画像で OOM リスク【要PoC】。system RAM 64GB は CPU オフロードに有利だが GPU 常駐が基本。
- **判断**: **画像＋テキストVLMの“単発最速”機**。omni は 7B を切り詰めて可否をPoC。

### 4.4 ④ NVIDIA DGX Spark 128GB（GB10 / sm_121）
- **vLLM / vLLM-Omni 可（条件付き）**: ARM64ネイティブ対応。ただし **sm_121 は新しく、上流stableイメージ非対応時期あり → CUDA 12.9+/CUDA13系・NGCコンテナ・nightly** 推奨【コミュニティ/要確認】。
- **強み＝容量**: 128GB統合で **大型 omni（例 Qwen3-Omni-30B-A3B, MiniCPM-o 4.5(9B) 等）**を単体搭載可。②③に載らない規模を担当。
- **弱み＝単発速度**: 帯域 273 GB/s。**②③に載るモデルなら DGX の単発は遅い**（帯域律速）。用途が単発中心なので、DGX は「**大型/フル omni 専用**」と位置づけるのが妥当。
- 推奨設定の論調【コミュニティ】: FP8＋KV cache FP8＋`gpu_memory_utilization` 0.85＋prefix caching、NVFP4 MoE が旨味。
- **判断**: **大型・フル omni／余裕枠**。単発ベンチでは「遅い＝劣る」ではなく「載る領域が違う」と注記。

### 4.5 推論エンジン別「どれが最速か」（評判と実測傾向）

「最速」は **(1)単発 vs 高並列、(2)プラットフォーム、(3)マルチモーダル要否** で変わり、**全クラスで勝つ単一エンジンは無い**【コミュニティ・複数ベンチ集約】。

| エンジン | 対応PF | 単発速度の評判 | マルチモーダル | 手軽さ | 備考 |
|---|---|---|---|---|---|
| **TensorRT-LLM** | NVIDIA | ◎ 最速級（p50/p95最小） | △ 弱い | ✕ モデル毎にengine compile(~28分) | ピーク性能王だが硬い・多モーダル不得手 |
| **SGLang** | NVIDIA | ◎ TTFT最速級（prefix共有で vLLM比+30%級） | ○ | △ | RAG/多ターン/エージェント向き |
| **vLLM / vLLM-Omni** | NVIDIA | ○ 上位（70B Q4/RTX5090で ~48 tok/s） | **◎ 最広（動画/omni標準）** | △ | **多モーダルは実質本命** |
| **ExLlamaV3 (EXL3)** | NVIDIA | ◎ 単発・VRAM効率良（V2はarchived） | ○ EXL3で対応 | △ | 単一consumer GPUの単発愛好家枠 |
| **llama.cpp** | CUDA/Metal/CPU/Vulkan | ○ （~43 tok/s、MLXより下） | △ **静止画のみ・動画×** | ◎ | 最も可搬。GGUF。Ollamaの母体 |
| **Ollama** | 全部(llama.cpp/MLX) | ○ （~41 tok/s、薄い上乗せ） | △ 画像中心 | ◎ 最易 | 便利レイヤ。共通基準に最適 |
| **MLX / MLX-VLM** | Apple Silicon | ◎ **Mac最速**（llama.cpp比 +15–30%） | ○ 画像(＋一部音声) | ○ | Mac実力ランの本命 |

参考実測（単一ベンチ, RTX5090, Llama-3-70B Q4, 単発）: **vLLM 48.2 > ExLlamaV2 44.1 > llama.cpp 43.0 > Ollama 41.5 tok/s**。7B Q4 なら5090で 150–200 tok/s も【コミュニティ・要再現】。ソース: BIZON / Spheron / DeployBase 等（§19）。

**本件（単発＋マルチモーダル/omni）での結論**:
- **テキストのみ最速**狙いなら、NVIDIAは **TensorRT-LLM / ExLlamaV3 / SGLang** が“最速”と言われがち、Macは **MLX**。→ **コーディングエージェント（テキスト特化）にはこの系統が効く**。
- ただし **動画・フル omni はこれら“速いがテキスト寄り”エンジンが未対応/弱い**。**多モーダル要件では、実際に動く中で最速なのは NVIDIA=vLLM/vLLM-Omni、Mac=MLX-VLM**。
- **Ollama/llama.cpp** は最速ではない（先頭比 ~10–15%落ち・**動画非対応**）が、**“まず動かす／共通基準”に最適**。

> **【方針決定 2026-07-01】二段構えは“遅延評価型”を採用。** まず全環境を**一段**（NVIDIA=vLLM/vLLM-Omni、Mac=MLX-VLM、共通基準=Ollama）で立て、PoCで単発を実測。**コーディング単発が体感不足 かつ ExLlamaV3/SGLang が vLLM比で実測 ≥ 約20–30% 速く安定**な場合に限り、②③へ**テキスト高速レーン**を増設（§13 Phase 4）。差が小さければ一段のまま（運用簡素を優先）。Mac は MLX が最速兼多モーダルのため常に一段で完結。

---

## 5. マルチモーダル／omni 要件と対応状況（重要）

### 5.1 モダリティ別「対応の広さ」（率直な現実）
対応の広さは **画像 ≫ 音声入力 > 動画入力 > 音声出力（フル omni）** の順で狭くなる。

| モダリティ | 対応の広さ | 代表フレームワーク | 備考 |
|---|---|---|---|
| 画像＋テキスト(VLM) | 広い（ほぼ全FW） | vLLM / MLX-VLM / Ollama / llama.cpp / LM Studio | Gemma3/4, Qwen-VL, MiniCPM-V 等 |
| 音声入力 | 中 | vLLM(-Omni) / 一部Ollama(MLX, Gemma4) | Gemma4=音声入力対応、Qwen-Omni(Whisper-v3エンコーダ) |
| 動画入力 | 狭い | **vLLM-Omni** 中心 | フレーム抽出＋ViT。トークン多く重い |
| 音声出力/フル omni | 最狭 | **vLLM-Omni（要source/Docker）** | `pip`のvLLMは音声“出力”未対応の場合あり |

### 5.2 omni フレームワーク: **vLLM-Omni**【準公式】
- `vllm-project/vllm-omni`: vLLMを omni へ拡張。2025-11 公開。**CUDA前提 → ②③④で稼働、①(Mac)は対象外**。
- 版: v0.16.0(2026-02) で Qwen3-Omni/Qwen3-TTS・MiMo-Audio・GLM-Image・拡散画像/動画。v0.22.0(2026-06) で MiniCPM-o 4.5・量子化拡張等。
- **Qwen2.5-Omni**: text/image/audio/video 入力＋音声ストリーミング出力。音声エンコーダ=Whisper-large-v3、動画=Qwen2.5-VL系ViT。**vLLMで audio+image+video 入力可**。ただし **`pip`版は text 出力のみ → 音声“出力”は source/Docker ビルドが必要**【準公式/コミュニティ】。

### 5.3 Mac(MLX) でのマルチモーダル
- **MLX-VLM**: 画像＋テキストの実務ライン（Gemma3/4, Qwen-VL 等）。
- **音声**: Gemma 4 12B は音声入力対応でOllama/MLX導入可【コミュニティ】。ただし**動画・音声出力（フル omni）はMacでは限定的**。
- 結論: **Mac は「画像＋テキスト（＋音声入力の実験）」に限定し、フル omni は NVIDIA/DGX に振る**。

---

## 6. 推奨モデル候補（マルチモーダル／omni・複数）

用途とVRAMで複数を評価する。**具体VRAM実測は§7ツール＋§13 PoCで確定**（下記は設計上の目安）。

| モデル | 種別/モダリティ | 規模 | 主用途 | 想定搭載環境（目安） | 主フレームワーク |
|---|---|---|---|---|---|
| **Gemma 3 (12B)** | VLM: 画像＋テキスト・長文脈 | 12B | コンシェルジュ/要約/タグ | ①②③（Q4/FP8）/④ | MLX-VLM / vLLM / Ollama |
| **Gemma 4 (12B)** | 画像＋**音声入力**＋テキスト | 12B | コンシェルジュ/音声 | ①(一部)②③/④ | Ollama / MLX / vLLM |
| **Qwen2.5-VL-7B** | VLM: 画像/複数画像/動画理解 | 7B | 要約/タグ/文書・画像 | ①②③/④ | vLLM / MLX-VLM |
| **Qwen3-VL** | VLM 強化(コード＋視覚も強) | 各サイズ | コーディング＋視覚 | サイズ次第 | vLLM / MLX-VLM |
| **Qwen2.5-Omni-7B** | **フル omni**(画像+音声+動画→音声) | 7B | コンシェルジュ(音声) | ②(可)③(窮屈)/④ | **vLLM-Omni** |
| **Qwen3-Omni-30B-A3B** | フル omni・MoE | 30B(active~3B) | 高品質 omni | **④のみ現実的** | **vLLM-Omni** |
| **MiniCPM-o 4.5** | omni(視覚/音声/ライブ配信) | 9B | 効率omni | ②/④(③は要確認) | vLLM(-Omni) |
| **Qwen3-Coder / Qwen2.5-Coder** | テキスト(コード特化) | 7B/14B | **コーディングエージェント** | ②③(最速)/①/④ | vLLM / Ollama / MLX |

- **コーディングエージェントはテキスト特化が有利**（Coder系）。視覚が要るならQwen3-VL。→ **用途別に複数モデルを併用**（本人の「複数見ておく」方針に合致）。
- **フル omni は 7B(Qwen2.5-Omni)を②で、① Mac は画像＋テキストの Gemma/Qwen-VL を**、大型 omni は④、が現実的な初期配置【推測/要PoC】。

### 6.1 コーディングエージェント用モデル：調査結果と候補（要PoC確定）

コーディングは**テキスト特化モデル**が有利。評価軸は **SWE-bench Verified / Aider Polyglot / LiveBench Coding**（エージェント性能・ツール呼び出し・多言語編集）。
**重要な原理**: 単発デコード速度 ≈ **活性パラメータ数 ÷ メモリ帯域**。→ **MoE（活性パラメータが少ない）は帯域の低い ①Mac・④DGX で特に有利**、**dense小型は高帯域・低VRAMの ②③RTX に向く**。**結果として“1モデルを全台”ではなく、機ごとに最適が変わる**。

| モデル | 種別 | 総/活性 | ベンチ(参考) | 想定搭載 | 備考 |
|---|---|---|---|---|---|
| **Qwen2.5-Coder-14B** | dense | 14B | 高 | ②③(Q4~8-9GB)/①/④ | **12GB(③)にも収まる無難な主力** |
| **DeepSeek-Coder V3 (distill)** | — | 小 | SWE 40.5%(12GB) | ③(12GB)/② | **12GB最適の質/GB** |
| **Devstral Small 2 (24B)** | dense/agentic | 24B | SWE 68% | ②(16GB,窮屈~15-25tok/s)/①/④ | Mistralの**エージェント特化** |
| **Qwen2.5-Coder-32B** | dense | 32B | Aider 73.7 | ①(48GB)/④ | 高品質。RTXには不可 |
| **Qwen3-Coder-30B-A3B** | **MoE** | 30B/3.3B活性 | 高・256K文脈(~19GB Q4) | **①Mac**/④ | **Mac/DGXの本命**（活性3B=帯域低くても速い）|
| **Qwen3-Coder-Next 80B-A3B** | **MoE** | 80B/3B活性 | **SWE 70.6%** | **④DGXのみ** | 活性3Bで大型並み。DGX 128GBの旨味 |

**環境別の第一候補（最終選定はPoC）**:
- **③ RTX5070 12GB**: DeepSeek-Coder V3(distill) or Qwen2.5-Coder-14B(Q4)。帯域672で**単発最速**。
- **② RTX5060Ti 16GB**: Devstral Small 2(24B) or Qwen2.5-Coder-14B。16GBで24B級に手が届く。
- **① Mac M4 Pro 48GB**: **Qwen3-Coder-30B-A3B(MoE)**（活性3B=Mac帯域でも高速）or Qwen2.5-Coder-32B。
- **④ DGX 128GB**: **Qwen3-Coder-Next 80B-A3B(MoE)**（SWE70.6%・活性3B）。容量×低活性の理想形。

> ベンチ値はコミュニティ/公開値。**実エージェント用途（ツール呼び出し・長文脈・自分のコードベース）での有用性はPoCで検証**（§7ツールでVRAM当たり付け→実測）。視覚も要るなら **Qwen3-VL** を別枠で。

### 6.2 汎用・日常・コンシェルジュ用（Gemma 4 / Qwen 3.6 / GLM）＋使用感

**コミュニティ総評（X/Reddit・技術ブログ, 2026-04頃）【コミュニティ・信頼度中／要自己検証】**:
- **Gemma 4 = 「日常使いとバランスの王」**。「ローカルスタックを丸ごと置換した」「26B-A4B は神」。創作・視覚・音声・日本語(140+言語)に強い。RTX40系で 60+ tok/s。
- **Qwen 3.6 = 「本気のコーディング／エージェントの王」**。「Claude Code の最良の代替」「エージェントコーディングで Gemma4 を圧倒」。爆速。日本語も強い。
- **GLM-5.1 = 「高難度推論の隠れGOAT」**。「意図理解が Claude Opus 級」。GLM-4.5-Air も「難問最強」。

| モデル | 規模 | 得意 | 使用感の要点 | 搭載目安 |
|---|---|---|---|---|
| **Gemma 4 26B-A4B** | 26B/4B活性 MoE | 日常・視覚・音声・創作・多言語 | 「箱出しで良い」「スタック置換」・速い | ①/②(Q4)/④、③窮屈 |
| **Gemma 4 12B** | 12B dense | 日常・視覚・音声・要約 | 整った文章・16GBで快適 | ①②③/④ |
| **Gemma 4 31B** | 31B | 最上位・256K文脈・MMLU-Pro ~85% | consumer最上位級 | ①(48GB)/④ |
| **Qwen 3.6 (35B-A3B)** | 35B/3B活性 MoE | コーディング・エージェント・多言語・262K(~1M) | 「爆速」「Claude Code代替」 | ①/④、②③はQ4で窮屈〜不可 |
| **GLM-5.1 / GLM-4.5-Air** | 大/中 | 高難度推論・意図理解 | 「Opus級の理解」・量子化前提 | ④中心（Airは①も可）|

→ **住み分け: コンシェルジュ=Gemma 4／コーディング=Qwen 3.6・Coder系／難問=GLM**。

### 6.3 VLM（画像＋テキスト）深掘り

| モデル | 規模 | 強み | 使用感/評判 |
|---|---|---|---|
| **Qwen3-VL** | 各サイズ(〜235B-A22B) | 最強格。OCR32言語・GUI/スクショ・動画・2D/3D grounding・エージェント | 画面理解が優秀・コード＋視覚に強い |
| **Qwen2.5-VL-7B** | 7B | 文書/複数画像/動画。定番 | 安定・軽量・実績多 |
| **InternVL3-78B** | 78B | MMMU 72.2%・ツール/GUI/3D | 高精度・研究寄り |
| **Gemma 4 (12B/26B-A4B)** | — | 視覚＋音声＋多言語 | 日常VLMの本命 |
| **MiniCPM-V 4.5** | 8B | **文書処理トップ** | 軽量・エッジ最適 |
| **Llama 4 (Scout/Maverick)** | 大 | ネイティブ画像 | 大型・汎用 |

（Pixtral / Phi-4 multimodal / Molmo / NVLM も候補）

### 6.4 omni（音声＋動画＋音声出力）深掘り

| モデル | 規模 | 特徴 | デプロイ性/使用感 | 本件の適地 |
|---|---|---|---|---|
| **Qwen3-Omni** | 30B-A3B | 40分超音声・119言語・Thinking・234ms低遅延・音声生成 | **クラウド/高性能GPU寄り** | **④ DGX**（128GBで活きる）|
| **MiniCPM-o 4.5** | 9B | 視覚/音声で Gemini2.5 Flash級・全二重ライブ配信 | **エッジ最適・低資源**（SigLip2+Whisper-med+CosyVoice2+Qwen3-8B）| **② 16GB**（ローカルomniの本命）|
| **Qwen2.5-Omni-7B** | 7B | 前世代omni・音声出力 | 音声“出力”は source build 要 | ②/③(窮屈) |

→ **ローカル単発omniは MiniCPM-o 4.5(9B) が本命**（② 16GBに収まる）、**大型・高品質omniは Qwen3-Omni を ④ DGX**。

### 6.5 要約・タグ付け／小型・構造化出力（重要な注意）

- **タグ付け・JSON等の構造化出力は 3B級では不安定**（Llama-3.2-3B の JSON parse 47–56%、SmolLM2-1.7B 26%）→ **7B/8B以上を推奨**【コミュニティ・信頼度中】。
- 候補: **Qwen3-8B**（多言語・/think・日本語）、**Gemma 4 12B**（整った文章・要約）、**Mistral 7B**（要約が強い）。
- 構造化はモデル任せにせず **vLLM/Ollama の guided/structured output（JSONスキーマ強制）を併用**。
- 日本語の要約・タグは **Qwen 系が無難**（多言語強い・Apache）。

### 6.6 コミュニティ使用感 総評＆環境別 早見表

【出所: X/Reddit集約・技術ブログ（note.com/zephel01, dev.to, benchlm 等）／信頼度中・要自己検証】

**2026コンセンサスの住み分け**: 日常/コンシェルジュ=**Gemma 4** ／ コーディング/エージェント=**Qwen 3.6・Qwen3-Coder** ／ 難問推論=**GLM-5.1** ／ ローカルomni=**MiniCPM-o 4.5** ／ 大型omni=**Qwen3-Omni(DGX)**。

| 環境 | コンシェルジュ | コーディング | VLM/視覚 | omni | 要約/タグ |
|---|---|---|---|---|---|
| **① Mac 48GB** | Gemma 4 26B-A4B | **Qwen 3.6 35B-A3B** | Qwen2.5/3-VL | MiniCPM-o(画像+音声) | Qwen3-8B/Gemma4-12B |
| **② 5060Ti 16GB** | Gemma 4 12B/26B-A4B(Q4) | Qwen3-Coder-14B/Devstral | Qwen2.5-VL-7B | **MiniCPM-o 4.5** | Qwen3-8B |
| **③ 5070 12GB** | Gemma 4 12B | DeepSeek-Coder/Qwen2.5-Coder-14B | MiniCPM-V/Qwen2.5-VL | (窮屈) | Qwen3-8B |
| **④ DGX 128GB** | Gemma 4 31B/GLM-5.1 | Qwen3-Coder-Next 80B-A3B | Qwen3-VL(大) | **Qwen3-Omni** | 何でも |

> すべて**参考の当たり付け**。最終は §13 PoC で**自分のタスク・日本語・ツール呼び出し**の実使用感で検証（ベンチ上位≠自分の用途で最良）。

---

## 7. モデル選定支援ツール（本人要望・調査対象）

「自分のハードで最適なモデルを選ぶ／載るか判定する」ツール群。**用途は“当たり付け”**であり、**マルチモーダルのVRAMは過小評価しがち**（後述）。

> **注目（本人共有・Qiita紹介）: WhichLLM** — GPUを自動検出し、**複数リーダーボード(LiveBench / Artificial Analysis / Aider / Chatbot Arena ELO / Open LLM / 視覚)を統合 × VRAM適合 × 推定速度**で「実際に載って・速くて・賢い」モデルを機械推薦するCLI。**recency-aware**（古いLBを系譜に沿って減点）で**将来のモデル世代交代に強い**。証拠信頼度の階層(direct→variant→base_model→…)も明示。→ **§13.5の“モデル入替前提”と好相性**。

| ツール | 種別 | できること | URL |
|---|---|---|---|
| **WhichLLM** | **モデル自動推薦** | GPU自動検出→ベンチ統合×VRAM×速度でランキング。`--profile coding`/`--min-speed 20`/`plan`/`upgrade`/`run`。MIT・Py3.11+・`uvx whichllm@latest` | https://github.com/Andyyyy64/whichllm |
| **LLM Checker** | **モデル自動推薦** | ハード走査→Quality/Speed/Fit/Context の4軸採点。HF/Ollama/GPT4All 33k+ レジストリ・Ollama統合 | https://github.com/Pavelevich/llm-checker |
| LLM Model VRAM Calculator (HF, NyxKrage) | VRAM計算 | HFモデル名＋量子化＋文脈長＋GPU VRAM で可否/使用量 | https://huggingface.co/spaces/NyxKrage/LLM-Model-VRAM-Calculator |
| ApX "Can You Run This LLM?" | VRAM計算＋tok/s推定 | **NVIDIA/Apple Silicon対応**、tok/s概算も | https://apxml.com/tools/vram-calculator |
| Local AI Master Model Recommender | **モデル推薦** | **タスク＋ハード**選択で推奨モデル＋VRAM＋ベンチ＋導入コマンド | https://localaimaster.com/tools/model-recommender |
| Logarithmic Spirals GPU Planner | VRAM/計画 | Apple Silicon＋NVIDIA＋コーディングエージェント考慮 | https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/ |
| gpuforllm.com | VRAM計算 | HF URLインポートで任意モデル判定 | https://gpuforllm.com/ |
| DevTk.AI VRAM Calculator | VRAM計算 | モデル選択＋量子化(Q4_K_M推奨)で概算 | https://devtk.ai/en/tools/vram-calculator/ |
| HF `accelerate estimate-memory` | CLI | モデルのメモリ見積り（テキスト中心） | (transformers/accelerate) |
| Ollama / LM Studio | ランタイム内蔵 | 自動量子化選択・互換バッジ | (各アプリ) |

**重要な注意（率直に）**:
- 多くの計算機は**テキストLLMの重み＋KVキャッシュ**を前提。**マルチモーダルの視覚/音声エンコーダ、画像/動画トークン（大量になりうる）を過小評価**する → **omni では鵜呑み禁物、PoCで実測**。
- 本件では **「§7ツールで当たり付け → §13 PoC で実測確定」** の2段構え。将来、**4台×候補モデルの“載る/速い”マトリクスを自作スクリプトで自動生成**することも可能（要望あれば別途）。
- **WhichLLM / LLM Checker の注意（率直に）**: 便利だが (a) **推定速度＋公開ベンチの統合**であり**自分のタスク性能ではない**、(b) WhichLLM は AWQ/GPTQ=Linux+NVIDIA限定・**Apple Silicon/CPU は GGUF のみ**、(c) omni/動画の適合判定は弱め。→ **当たり付けに使い、確証は §12.9 自前タスク評価**で。各マシンで実行すれば①Mac/②③RTX/④DGX の候補を機械抽出できる。

---

## 8. 必要な材料（4環境・確認コマンドつき）

### 8.1 ソフトウェア
| 項目 | ① Mac | ② RTX5060Ti / ③ RTX5070 (WSL2) | ④ DGX Spark |
|---|---|---|---|
| OS | macOS（新しめ）【要確認】 | Windows11 + WSL2(Ubuntu22.04/24.04) | DGX OS(ARM64) |
| ランタイム | MLX-VLM / Ollama(MLX) / (vllm-mlx) | vLLM / vLLM-Omni / Ollama | vLLM / vLLM-Omni(CUDA13/NGC) |
| Python | 3.11(現) → **3.12 venv**（MLX/vllm-metal用） | 3.12推奨 | 3.12推奨 |
| CUDA | 不要 | 近年13.0既定【要確認】 | **12.9+/13系必須**【コミュニティ】 |
| Driver | — | Windows側 WSL対応の新ドライバ | DGX同梱 |
| Docker | 任意 | 任意（toolkit必須, 再現性高） | NGC pull用 |

### 8.2 事前確認（読み取り専用）
```bash
# ① Mac（本機）
uname -m; system_profiler SPHardwareDataType | grep -Ei "Chip|Memory"
ollama --version; ollama list
python3 --version; uv --version   # 3.12 venv 準備判断

# ②③ NVIDIA + WSL2（各PCのWSL内）
nvidia-smi --query-gpu=name,memory.total,compute_cap,driver_version --format=csv
python -c "import torch;print(torch.__version__, torch.cuda.is_available(), torch.version.cuda)"
cat /etc/os-release; ldd --version
docker run --rm --gpus all nvidia/cuda:13.0-base nvidia-smi   # Docker経路の場合

# ④ DGX Spark
uname -m   # aarch64
nvidia-smi; nvidia-smi -q | grep -iE "power|temperature"
```

---

## 9. 懸念事項（単発・omni・Blackwell・Mac に更新）

| # | 懸念 | 影響 | 対処 |
|---|---|---|---|
| 1 | **フル omni は CUDA専用（vLLM-Omni）** | ◎ | Mac をフル omni から除外。①=画像＋テキスト、②③④=omni |
| 2 | **Mac の vLLM 非対応／別実装** | ◎ | MLX-VLM/Ollama(MLX)で評価。量子化・カーネルは NVIDIA と非等価 |
| 3 | **Blackwell(sm_120/121)の新しさ** | ○ | vLLMは近年対応だが**版・CUDA要確認**。DGX(sm_121)はCUDA13/NGC |
| 4 | **VRAM×マルチモーダル** | ◎ | ③12GBはomni窮屈。画像/動画トークンで膨張。PoCでOOM境界を確定 |
| 5 | **単発では帯域が支配** | ◎ | ③(672)>②(448)≈①/④(273)。DGXは大型担当、単発は速くない前提 |
| 6 | **音声“出力”は要source build** | ○ | Qwen-Omni音声出力は`pip`不可のことあり→Docker/source |
| 7 | **WSL2オーバーヘッド/パススルー** | ○ | toolkit必須、5–15%低下。②③とも同方式で揃える |
| 8 | **モデル選定ツールのMM過小評価** | ○ | omni VRAMは実測で確定（§7注意） |
| 9 | **熱・電力スロットリング（特にMacノート/小型筐体）** | ○ | ウォームアップ後の定常値で評価、長時間drift記録 |
| 10 | **量子化フォーマット非等価**(MLX/GGUF/AWQ/FP8/NVFP4) | ○ | 「共通基準ラン(Ollama)」＋「各機最適ラン」を分離（§10） |
| 11 | **前処理(エンコード)時間がTTFTを支配**（画像/音声/動画） | ○ | **マルチモーダル前処理時間を独立指標化**（§12） |
| 12 | **DGX入手/利用状況が未確定** | ○ | PoC時期に影響。§17で確認 |

---

## 10. 同一条件で比較するためのハードル（フレームワーク跨ぎ）

- **同一モデル**: 論理モデルは共通化可。ただし重み形式が分岐（MLX変換 / GGUF / safetensors+FP8）→ **ビット単位同一は不可**。
- **同一精度/量子化**: 最大公約数は **BF16（載るサイズ）**。実力ランは各機ネイティブ（Mac=MLX 4bit, NVIDIA=FP8, DGX=NVFP4/FP8）。**2種を別ランで**。
- **同一プロンプト/画像/音声/動画入力・max_tokens・サンプリング(temp/top_p/top_k/seed)**: 全環境固定。seedは**環境内再現用**（異バックエンドで出力一致はしない）。
- **同一API**: **全サーバを OpenAI互換で起動**（Ollama, vLLM, vLLM-Omni, vllm-mlx いずれも互換）→ **同一クライアントで計測**（公平性の要）。
- **共通基準は Ollama**（4台で動く）。**各機最適は MLX-VLM / vLLM(-Omni)**。
- **vLLM非対応（Mac）**は「代替ランタイムの参考値」として**別カテゴリ表記**。棒グラフに混ぜない。

---

## 11. 固定すべき設定項目

### 11.1 サーバ側（例: vLLM / vLLM-Omni）
`--model`(revision固定) / `--dtype` / `--quantization`(fp8/nvfp4) / `--kv-cache-dtype` / `--max-model-len` / `--gpu-memory-utilization`(0.85–0.90) / `--max-num-seqs`(単発なら小) / `--limit-mm-per-prompt`(画像/音声/動画の個数上限) / `--enforce-eager`(統一) / `--trust-remote-code`(Qwen系) / `--seed` / `--served-model-name` / `--enable-prefix-caching`。
> 記録: フレームワーク版・torch/CUDA・driver・GPU名/cap・起動コマンド全文・`VLLM_*`環境変数。

### 11.2 クライアント側
backend(openai-chat) / 入力長・出力長（`--ignore-eos`で厳密化）/ 画像・音声・動画の入力仕様（解像度/長さ/本数）/ concurrency=**1（単発主）**＋補助スイープ / warmup（対象外）/ 反復回数(3回・中央値) / percentile-metrics(ttft,tpot,itl,e2el)。

### 11.3 計測対象外
初回モデルロード（別計測）／ウォームアップ／JIT・CUDA Graphキャプチャ初回。

---

## 12. ベンチマーク設計（単発を主指標に）

### 12.1 指標（**主＝単発**）
| 指標 | 定義 | 分類 |
|---|---|---|
| **TTFT** | 受理→初トークン（**画像/音声/動画のエンコード時間を含む**） | **主** |
| **単発 output tokens/sec** | concurrency=1 のデコード速度 | **主** |
| **マルチモーダル前処理時間** | 画像/音声/動画のエンコード（ViT/Whisper）に要する時間 | **主(MM)** |
| E2Eレイテンシ | 固定タスクの総応答時間 | 主 |
| p50/p95(単発反復ばらつき) | 反復の分布 | 副 |
| VRAM/統合メモリ ピーク | 搭載可否とマージン | 副(可否) |
| 消費電力 / **tokens/joule** | 効率（電力枠差の正規化） | 副 |
| モデルロード時間 | 起動〜ready | 補助 |
| エラー率/OOM | 妥当性・可否境界 | 副 |
| （参考）並列総 tok/s | concurrency>1 の総量 | 参考(用途外) |

### 12.2 主指標の選定理由
用途が**単発・自分専用**のため、**TTFT＋単発デコード tok/s＋マルチモーダル前処理時間**が体感を最も代表。**並列スループットは参考**（DGXの強みだが本用途では従）。効率比較に **tokens/joule** を併記。

### 12.3 計測条件
- concurrency=1 主体（補助で 4/8 を軽く）。
- 入出力: (テキスト in512/out256)、(画像1枚＋質問)、(音声Ns＋質問)、(短動画＋質問) をタスク別に固定。
- ウォームアップ後、各3回・中央値。長時間drift（10–30分）を1回。
- 電力: 可能なら**壁コンセント電力計で全系統**（`nvidia-smi`=GPU rail、`powermetrics`=SoC全体で範囲が違う点に注意）。

### 12.4 評価の4階層（載る→速い→賢い→“自分の用途で良い”）

意思決定は**この順のふるい落とし**。上流で落ちたら下流は測らない。

1. **載るか (Fit)** — OOMせず目標コンテキストでロードできるか（§12.5）
2. **速いか (Speed)** — 単発 tok/s・TTFT が実用域か（§12.6）
3. **賢いか (Capability・標準)** — 公開ベンチで“当たり付け”（§12.7–12.8）
4. **自分の用途で良いか (Task)** — ★本命★ 自前資料での実タスク評価（§12.9）

> 公開ベンチは**スクリーニング**。**最終判断は §12.9 の自前タスク評価**（ベンチ上位 ≠ 自分の用途で最良）。

### 12.5 レイヤ1「載る/載らない」判定 — ツールと方法

| 手段 | 用途 | 備考 |
|---|---|---|
| §7 VRAM計算機(HF/ApX/gpuforllm 等) | 事前の当たり付け | **マルチモーダルは過小評価**に注意 |
| `accelerate estimate-memory` | 重みメモリ概算 | テキスト中心 |
| `gguf-parser` | GGUFの層/メモリ見積り | llama.cpp/Ollama系 |
| **実ロードテスト** | **確定** | 目標 `--max-model-len` でOOM有無。**KVキャッシュ込みが真実** |

- 方法: 各(モデル×量子化×環境)で「目標文脈長でロード→短い推論が通る」を可否判定。**画像/音声/動画トークンでVRAMが膨らむ**ので、MMは実入力で確認。

### 12.6 レイヤ2「速度(tok/s)」計測 — OSSツール（ランタイム別）

| ツール | 対象 | 測るもの | 備考 |
|---|---|---|---|
| **vLLM `vllm bench`** (serve/latency/throughput) | vLLM/-Omni | TTFT/TPOT/ITL/throughput | 純正・OpenAI互換叩き |
| **NVIDIA GenAI-Perf** | OpenAI/Triton互換全般 | TTFT/ITL/TPS・並列掃引 | 汎用・NVIDIA製 |
| **GuideLLM** | 推論サーバ全般 | SLO志向の負荷/性能 | 到達レート掃引 |
| **LLMPerf** | OpenAI互換 | throughput/latency | Ray製 |
| **llama-bench / llama-benchy** | llama.cpp/Ollama | 生throughput／client実測 | GGUF。benchyは背端自動判定 |
| **LocalScore** | ローカル全般 | ハード速度スコア | **機×モデルの横断比較に便利** |
| **Bench360** | ローカルLLM | 360度(速度+資源+品質) | 包括フレーム(arXiv) |
| MLX(`mlx_lm`)内蔵計時 | Mac/MLX | tok/s・TTFT | OpenAI互換化しGenAI-Perf併用可 |

- **統一方針**: 全ランタイムを **OpenAI互換で起動 → GenAI-Perf か `vllm bench` で共通計測**（クライアント固定）。Mac/llama.cpp は内蔵計器も併用しズレを把握。単発は `concurrency=1`。

### 12.7 レイヤ3「能力」標準ベンチ（用途別）

| 用途 | 推奨ベンチ | ハーネス |
|---|---|---|
| 汎用/指示追従 | MMLU-Pro, IFEval, GPQA | **lm-evaluation-harness** / LightEval |
| コーディング | **SWE-bench Verified**(agentic修復)・**LiveCodeBench**(汚染耐性)・BigCodeBench(ライブラリ)・**Aider Polyglot**(差分編集)・Terminal-Bench(端末) | 各公式harness / bigcode-eval |
| 推論/難問 | GPQA, MATH, ARC-AGI | lm-eval / 各公式 |
| VLM(視覚) | MMMU, DocVQA, ChartQA, OCRBench | lm-eval-harness(VLM) / VLMEvalKit |
| omni | 音声ASR(WER), 動画QA | 各モデル公式eval |

- **注意**: エージェント系は**足場(harness/ツール)でスコアが大きく動く** → **2–3種を併用**し単一スコアを盲信しない。参照リーダーボード: CodeSOTA / BenchLM / llm-stats / awesome-llm-bench(日次同期)。

### 12.8 日本語評価（日本語主体のため重要）

| リソース | 内容 | 実行 |
|---|---|---|
| **llm-jp-eval** | MC/QA/RC/NLI 等の日本語タスク | OSS・自前実行可 |
| **llm-jp-eval-mm** | **日本語マルチモーダル(VLM)評価** | OSS・**VLM用途に直結** |
| **Nejumi Leaderboard 4** (`wandb/llm-leaderboard`) | JMMLU-Pro/BFCL/SWE-bench 等・企業志向 | OSS・自前実行可 |
| **Swallow Leaderboard v2** | JEMHopQA/MMLU-ProX/JHumanEval/M-IFEval-Ja | 参照/一部再現 |
| JGLUE / JMMLU / JHumanEval | 個別タスク | データ公開 |

- 参考: 日本語特化 **Llama 3.1 Swallow 8B**(Nejumi4 sub-10B首位)、PLaMo、LLM-jp なども比較候補に。

### 12.9 レイヤ4「自前タスク評価」= 本命（仕様書駆動開発・要約・タグ付け）

★意思決定の核★。**自分の実資料で “ゴールデンセット”（30–100件）** を作り、全候補モデルを**同一ハーネス**で通して採点する。

**ツール**:
- **promptfoo**: アサーション(含有/**JSONスキーマ**/類似度/**LLM-rubric**)。プロダクト的テスト・回帰に強い。
- **DeepEval**: **G-Eval**(平易な言葉のカスタムrubric→LLM-judge・連続スコア)、**エージェント指標**(タスク完了・ツール使用)、RAG指標。
- **RAGAS**: 要約/RAGの忠実性。
- **Langfuse / Arize Phoenix**: エージェントの**軌跡トレース**（多段ツール呼び出しはeval単体では追えない）。

**用途別の自前評価デザイン**:
| 用途 | 入力(自前資料) | 評価方法 | 主メトリクス |
|---|---|---|---|
| **コーディング(仕様書駆動)** | 既存システムの**仕様書＋対象リポジトリ** | エージェント(Aider/OpenHands 等)で実装→**テスト実行**＋差分のLLM-rubric | **タスク完了率・テストpass率・ツール呼び出し成功率**・所要ターン/トークン |
| **コンシェルジュ(多モーダルQA)** | 代表的な画像/音声＋質問セット | LLM-as-judge rubric(正確性/有用性/**日本語**/幻覚)＋TTFT | rubricスコア・幻覚率・体感TTFT |
| **要約・タグ付け** | 自分の文書群 | **JSONスキーマ準拠率**＋タグ適合(gold少数と照合)＋要約忠実性(RAGAS/LLM-judge) | **schema準拠率・タグP/R・忠実性** |

**手順**: (1)資料から30–100件をゴールデンセット化（正解/ルーブリック付与）→ (2)promptfoo/DeepEval に1本の設定として定義 → (3)全候補モデルを OpenAI互換で差し替え一括実行 → (4)スコア＋速度＋fit を合成表に。**judge は強いモデル(クラウド可)を固定**し公平化。

### 12.10 総合評価マトリクスと主指標（用途別）

最終アウトプットは **(モデル×環境)** ごとの1行:

`Fit(○/×) → 単発tok/s → TTFT → 標準ベンチ(参考) → 自前タスクスコア → tok/J → 総合判定`

| 用途 | 主指標(1位) | 副指標 |
|---|---|---|
| コーディング | 自前**タスク完了率/テストpass率** | 単発tok/s・ツール成功率・SWE-bench(参考) |
| コンシェルジュ | 自前**rubricスコア(日本語/正確性)** | TTFT・幻覚率 |
| 要約・タグ | 自前**schema準拠率＋忠実性** | tok/s・日本語品質 |

> **速い・賢い・載る が揃って初めて採用。自前タスクスコアを最上位**に置く（公開ベンチは足切り/参考）。

---

## 13. 実証実験（PoC）計画 ← 本フェーズの中核

### 13.1 ゴールと合否基準
各環境で「推奨フレームワーク × 狙うモデル」が**実際に動き、単発で実用速度が出る**ことを確認する。

**合否基準（例・要調整）**
- **可否**: 対象モデルが**OOMせずロード**でき、対象モダリティ入力で**正しい応答**が返る。
- **速度**: 単発デコード **≥ 20 tok/s**（体感実用の目安）、テキスト単発は**≥ 40 tok/s**目標。
- **TTFT**: テキスト **≤ 1s**、画像1枚込み **≤ 2–3s**（前処理込み）目安。
- **モダリティ**: 目標モダリティ（画像/音声/動画/音声出力）が想定どおり機能。

### 13.2 フェーズ設計（狭い→広い）

> **方針（本人指示）: omni を最初から担う。** フェーズは“後回し”ではなく**検証の順序**。**④ DGX（手元・128GB）を omni 主軸ホスト**、**② RTX5060Ti を副 omni ホスト**に据え、Phase 0（疎通）→ **早期に Phase 1–3（音声・動画・音声出力）**へ進む。① Mac は omni 対象外（画像＋テキスト＋音声入力の一部）。③ RTX5070(12GB)は omni は窮屈なので**単発VLM＋コーディング**主体。

1. **Phase 0 画像＋テキスト**（全環境）: 最も広く動く。まずここで各FWの疎通・速度を確認。
2. **Phase 1 音声入力**（②③④、①はGemma4で試行）。
3. **Phase 2 動画入力**（②④中心、③は12GBで可否確認）。
4. **Phase 3 音声出力/フル omni**（**vLLM-Omni source/Docker**、②④）。
5. **Phase 4（条件付き）テキスト高速レーン**（②③のみ）: コーディングエージェント用のテキスト特化モデル(Qwen-Coder系)を **ExLlamaV3 / SGLang** で立て、Phase 0の vLLM 実測と単発比較。
   - **発動条件**: Phase 0–3 で**コーディング単発が体感不足** かつ **vLLM比で実測 ≥ 約20–30% 速く安定**。→満たせば②③に高速レーンを常設。
   - **非発動**: 差が閾値未満なら **vLLM 一段のまま**（2スタック運用の複雑さを回避）。
   - **対象外**: ① Mac（MLXが最速兼多モーダルで一段完結）、④ DGX（大型omni担当で単発最速は狙わない）。

### 13.3 環境別 PoC 手順（概要）
- **① Mac（本機）**: (a)Ollama(MLX)で VLM(Gemma3/Qwen2.5-VL) を pull → 画像＋テキスト推論・TTFT/tok-s。(b)`uv` で 3.12 venv → MLX-VLM 導入 → 同モデルで実力ラン。(c)Gemma4で音声入力を試行。
- **② RTX5060Ti / ③ RTX5070**: WSL2でGPU確認 → (a)Ollama で共通基準 → (b)vLLM(FP8)でVLM実力ラン → (c)②で vLLM-Omni(7B omni) の可否、③はVRAM境界を確認。
- **④ DGX Spark**: NGC/CUDA13でvLLM-Omni → 大型omni(Qwen3-Omni-30B-A3B等)ロード可否と単発速度。
- **共通ハーネス**: 全サーバ OpenAI互換起動 → 単一クライアントで TTFT/tok-s/前処理時間を計測（§11.2）。

### 13.4 ① Mac 具体手順（次アクション：本人GOで即実行可）
```bash
# (a) Ollama(MLX) 最短ライン ─ 画像＋テキスト
ollama pull gemma3:12b          # or qwen2.5-vl 系。数GB DL
# 画像＋質問（OpenAI互換 /api or /v1）で推論し TTFT/tok-s を計測

# (b) MLX-VLM 実力ライン（3.12 venv）
uv venv --python 3.12 ~/.venv-mlxvlm && source ~/.venv-mlxvlm/bin/activate
uv pip install mlx-vlm
python -m mlx_vlm.generate --model <mlx-community/gemma-3-...> --image <path> --prompt "..."
```
> **本版では未実行**（本人指示: 設計書更新を先行）。GO をもらえば①のPhase 0から着手。

### 13.5 将来対応：モデル入替・追加検証を可能にする前提条件（設計原則）

**目的**: 新モデル（次期 Gemma / Qwen4 / 新omni 等）が出ても**最小手数で載せ替え・再評価**でき、**過去結果と地続きで比較**できる状態を常に保つ。

**アーキテクチャ原則（疎結合3層）**
1. **インターフェース固定＝OpenAI互換API**: アプリ/エージェントは常に OpenAI互換エンドポイントだけを見る。裏のランタイム(vLLM/-Omni/MLX/Ollama/llama.cpp)やモデルは差し替え自由 → **アプリ無変更でモデル交換**。
2. **モデルはコード直書きせず“レジストリ(設定)で管理”**: `models.yaml` に (モデルID・revision・量子化・ランタイム・max_model_len・想定環境・profile) を宣言。**追加は行を足すだけ**。
3. **評価ハーネスはモデル非依存**: §12.9 のゴールデンセット＋promptfoo/DeepEval 設定を固定。新モデルは**同じ設定を通すだけで同じ物差しで再評価**。

**継続検証（continuous verification）の前提**
- **モデル・オンボーディング・チェックリスト**（新モデルは必ずこの順）: ①WhichLLM/LLM Checkerで当たり付け → ②Fit(実ロード) → ③Speed(tok/s) → ④標準ベンチ(足切り) → ⑤自前タスク評価 → ⑥合成表に1行追記。
- **結果はスキーマ固定表に追記**: `results.csv/json`（`model, revision, runtime, env, fit, tok_s, ttft, std_bench, task_score, tok_per_J, date`）。**時系列比較・回帰検知が可能**に。
- **バージョン・ピン留め＋更新履歴**: モデルrevision・ランタイム版・CUDA/torch・評価データ版を固定し、更新時は履歴に残す（再現性）。
- **ゴールデンセットも git 管理・版付け**: タスク追加/変更時は版を上げる。
- **judgeモデルは固定**: LLM-as-judge のjudgeを固定（変えると過去比較が壊れる。変える時は再ベースライン）。
- **ハード・プロファイル化**: 4台を環境プロファイル(GPU/VRAM/帯域/ランタイム)として定義。**新ハード追加も同じ枠**で受け入れ。

**アンチパターン（禁止）**
- モデルIDをアプリにハードコード（交換時に全修正が必要になる）。
- 評価を毎回アドホック実行（過去と比較不能）。
- judge/評価データを黙って変更（スコアが不連続になり信頼を失う）。

**受け入れ基準（この前提が満たされた状態）**
- 新モデルを `models.yaml` に**1行追加 → 1コマンドで Fit/Speed/自前タスクまで自動実行 → `results` に追記**。
- **アプリ側コードは無変更**（OpenAI互換の裏だけ差し替え）。
- 半年後に「当時 vs 現在」を同一ゴールデンセットで再走でき、劣化/改善を数値で言える。

---

## 14. 計測コマンド・設定例（フレームワーク別・雛形）

```bash
# vLLM (NVIDIA ②③) ─ VLM 画像＋テキスト, FP8
vllm serve Qwen/Qwen2.5-VL-7B-Instruct --quantization fp8 --dtype bfloat16 \
  --max-model-len 8192 --gpu-memory-utilization 0.90 --limit-mm-per-prompt image=2 \
  --seed 0 --served-model-name bench-model --host 127.0.0.1 --port 8000 --trust-remote-code

# vLLM-Omni (② / ④ DGX) ─ フル omni（source/Docker, sm_121はCUDA13/NGC）
# 参照: https://github.com/vllm-project/vllm-omni （Qwen2.5-Omni / Qwen3-Omni の例に従う）

# Ollama (共通基準・全環境) ─ 画像＋テキスト
ollama serve &        # OpenAI互換: http://127.0.0.1:11434/v1
ollama pull gemma3:12b

# 共通クライアント（単発計測の要点）: concurrency=1, --ignore-eos, TTFT/tok-s/前処理時間を記録
# 例: vllm bench serve --backend openai-chat --base-url ... --max-concurrency 1 \
#     --random-input-len 512 --random-output-len 256 --num-prompts 30 --seed 0 \
#     --percentile-metrics ttft,tpot,itl,e2el --save-result ...

# モニタ
nvidia-smi --query-gpu=timestamp,power.draw,utilization.gpu,memory.used,temperature.gpu --format=csv -l 1  # ②③④
sudo powermetrics --samplers gpu_power,cpu_power -i 1000   # ① Mac(SoC全体)
```

---

## 15. Web調査結果（v2 追補・主要ソース）

**フレームワーク／omni**
- vLLM-Omni（公式org・omni拡張, 2025-11公開, v0.22 2026-06）: https://github.com/vllm-project/vllm-omni ／ 対応モデル: https://docs.vllm.ai/projects/vllm-omni/en/latest/models/supported_models/ 【準公式・信頼度高・関連高】
- Red Hat: vLLM-Omni解説(2026-06-30): https://next.redhat.com/2026/06/30/expanding-ai-beyond-text-vllm-omni-extension-for-multimodal-models/ 【コミュニティ寄り・中】
- Qwen3-Omni: https://github.com/QwenLM/Qwen3-Omni ／ Qwen2.5-Omni: https://github.com/QwenLM/Qwen2.5-Omni 【公式・高】（音声“出力”は source/Docker 要）
- MiniCPM-o/-V: https://github.com/openbmb/MiniCPM-V 【公式・中〜高】

**Apple Silicon / Mac**
- Ollama×MLX（公式Blog）: https://ollama.com/blog/mlx 【公式・高】
- llama.cpp vs MLX vs Ollama vs vLLM (Apple, 2026): https://contracollective.com/blog/llama-cpp-vs-mlx-ollama-vllm-apple-silicon-2026 【コミュニティ・中】
- MLX vs Ollama ベンチ(2026): https://willitrunai.com/blog/mlx-vs-ollama-apple-silicon-benchmarks 【コミュニティ・中／参考値】
- vllm-mlx: https://github.com/waybarrios/vllm-mlx 【コミュニティ・中】

**Gemma**
- Gemma 3（HF公式Blog, 画像＋テキスト・mlx-vlm day0）: https://huggingface.co/blog/gemma3 【公式・高】
- Gemma 4 12B（音声入力対応, 2026-04）Developer Guide: https://developers.googleblog.com/gemma-4-12b-the-developer-guide/ 【公式・高】
- Gemma 4 × Ollama 手順: https://haimaker.ai/blog/gemma-4-12b-ollama-opencode-setup/ 【コミュニティ・中】

**Blackwell(RTX50) / vLLM**
- Consumer Blackwell 推論ガイド(arXiv 2026): https://arxiv.org/html/2601.09527v1 【学術寄り・中〜高】
- RTX 5060 Ti 16GB(14B ~51 tok/s): https://modelfit.io/gpu/rtx-5060-ti/ 【コミュニティ・中／参考値】
- RTX 5070 vLLM/llama.cpp/CUDA: https://gigagpu.com/rtx-5070-llm-inference/ 【コミュニティ・中／参考値】
- Unsloth Blackwell対応(5060–5090): https://unsloth.ai/docs/blog/fine-tuning-llms-with-blackwell-rtx-50-series-and-unsloth 【準公式・中〜高】

**モデル選定ツール**（URL は §7 表）: HF VRAM Calculator / ApX / Local AI Master Recommender / Logarithmic Spirals / gpuforllm / DevTk.AI 【ツール・中／MMは過小評価注意】

**DGX Spark（v1確定・維持）**
- 製品: https://www.nvidia.com/en-us/products/workstations/dgx-spark/ ／ HW仕様: https://docs.nvidia.com/dgx/dgx-spark/hardware.html 【公式・高】（128GB/273GB-s/sm_121/240W）
- vLLM on GB10(Docker): https://technotim.com/posts/vllm-gb10-docker/ ／ LMSYSレビュー(2025-10-13): https://www.lmsys.org/blog/2025-10-13-nvidia-dgx-spark/ 【コミュニティ・中】

> 注意: モデル名（例「Gemma-4-31B」等）や tok/s はコミュニティで表記揺れ・条件不統一。**確定値は自前PoCで置換**。

---

## 16. 未確定事項

- 【解決 2026-07-01】④ DGX Spark は**手元にあり利用可**。omni 主軸ホストとして早期PoC対象。
- 【要確認】各環境の **vLLM / vLLM-Omni のピン留め版**と要求 torch/CUDA（特に sm_120/121 と CUDA13）。
- 【要確認】**Qwen-Omni の音声“出力”**に必要な build 手順（source/Docker）と②③のVRAM実測境界。
- 【要確認】① Mac の **macOSバージョン**、`vllm-metal` を使うかどうか（3.12 venv 要否）。
- 【要確認】M4 Pro / RTX の**正確なメモリ帯域**（本資料は概算）。
- 後続検索クエリ: `vllm-omni qwen3-omni serve audio output docker`, `rtx 5070 5060ti vllm fp8 vlm vram oom`, `mlx-vlm gemma3 qwen2.5-vl mac benchmark tok/s`, `gemma4 audio ollama mlx`, `dgx spark sm_121 vllm cuda13 install`。

---

## 17. 私への質問

**必須確認 → 【回答済 2026-07-01】**
1. ④ DGX Spark: **手元にある** → omni 主軸ホストに採用（§13）。
2. omni 優先度: **最初からフル omni を担う**（Phase 0後すぐ音声・動画・音声出力へ）。
3. コーディングモデル: **要調査 → §6.1 に候補整理済**（コード特化中心・機ごとに最適、最終選定はPoC）。視覚要否は今後判断。

**推奨確認（精度が上がる）**
4. **共通基準は Ollama（4台横断）**でよいか。各機の実力ランは Mac=MLX-VLM / NVIDIA=vLLM(-Omni) でよいか。
5. **消費電力**を指標に含めるか（含めるなら壁電力計を用意できるか）。
6. ②③は **WSL2 前提**でよいか（ネイティブWindowsは含めない）。

**後続確認（PoC実行フェーズで）**
7. 対象モデルの revision 固定、DL元（HF/ミラー）。
8. 合否基準の tok/s・TTFT しきい値（§13.1 の暫定値でよいか）。
9. 4台×候補モデルの「載る/速い」マトリクスを**自作スクリプトで自動化**するか。

---

## 18. PPTX化に向けた構成案

| # | スライド | 主張 | 図表 |
|---|---|---|---|
| 1 | 表紙 | 4環境×マルチモーダル×単発の検証 | 環境アイコン |
| 2 | 目的・用途 | コーディング/コンシェルジュ/要約・タグ、単発主 | 箇条書き |
| 3 | 対象4環境 | Mac/5060Ti/5070/DGX の要点 | **環境比較表**（§2） |
| 4 | 最重要前提 | フルomni=CUDA専用／単発=帯域律速 | **意思決定ツリー** |
| 5 | 環境×FW×モダリティ | どこで何が動くか | **◎○△✕マトリクス**（§3.1） |
| 6 | 役割分担 | 単発ドライバ vs 大型omni(DGX) | 役割図 |
| 7 | Mac の実現性 | vLLM不可・MLXが本命 | **CUDA vs Metal/MLX アーキ図** |
| 8 | Blackwell(5060Ti/5070) | FP8旨味・VRAM vs 帯域 | **VRAM×帯域 バブル** |
| 9 | DGX Spark | 128GBで大型omni・単発は遅い | 仕様＋帯域バー |
| 10 | omni対応の広さ | 画像≫音声>動画>音声出力 | **モダリティ・ピラミッド** |
| 11 | モデル候補 | Gemma3/4・Qwen-VL/Omni・Coder | **モデル×環境×用途表** |
| 12 | モデル選定ツール | 当たり付け→PoC実測 | ツール一覧＋注意 |
| 13 | ベンチ指標 | TTFT＋単発tok/s＋MM前処理 | 指標マップ |
| 14 | PoC計画 | Phase0→3、合否基準 | **フェーズ・ガント** |
| 15 | リスク | VRAM/omni/Blackwell新しさ | リスク表 |
| 16 | 質問・次アクション | 必須/推奨/後続 | 質問表 |

**アーキ図**: (a)CUDA vLLM(-Omni) vs Metal/MLX、(b)WSL2→NVIDIA パススルー、(c)DGX統合メモリ、(d)共通OpenAI互換ハーネス。
**比較表**: 環境(§2)/対応マトリクス(§3.1)/モデル(§6)/ツール(§7)/指標(§12)。

---

## 19. 参考URL（主要）

- vLLM-Omni: https://github.com/vllm-project/vllm-omni ／ 対応モデル: https://docs.vllm.ai/projects/vllm-omni/en/latest/models/supported_models/
- Qwen3-Omni: https://github.com/QwenLM/Qwen3-Omni ／ Qwen2.5-Omni: https://github.com/QwenLM/Qwen2.5-Omni ／ MiniCPM-V/o: https://github.com/openbmb/MiniCPM-V
- Ollama×MLX: https://ollama.com/blog/mlx ／ mlx-vlm経由 Gemma3: https://huggingface.co/blog/gemma3 ／ Gemma4: https://developers.googleblog.com/gemma-4-12b-the-developer-guide/
- vllm-mlx: https://github.com/waybarrios/vllm-mlx ／ Apple FW比較: https://contracollective.com/blog/llama-cpp-vs-mlx-ollama-vllm-apple-silicon-2026
- Blackwell推論: https://arxiv.org/html/2601.09527v1 ／ 5060Ti: https://modelfit.io/gpu/rtx-5060-ti/ ／ 5070: https://gigagpu.com/rtx-5070-llm-inference/
- DGX Spark: https://www.nvidia.com/en-us/products/workstations/dgx-spark/ ／ HW: https://docs.nvidia.com/dgx/dgx-spark/hardware.html ／ vLLM on GB10: https://technotim.com/posts/vllm-gb10-docker/
- モデル選定ツール: **WhichLLM** https://github.com/Andyyyy64/whichllm ／ **LLM Checker** https://github.com/Pavelevich/llm-checker ／ Qiita紹介 https://qiita.com/kai_kou/items/1c4831ed750652870677 ／ HF VRAM Calc https://huggingface.co/spaces/NyxKrage/LLM-Model-VRAM-Calculator ／ ApX https://apxml.com/tools/vram-calculator ／ Local AI Master https://localaimaster.com/tools/model-recommender ／ Logarithmic Spirals https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/
- 推論エンジン速度比較: https://bizon-tech.com/blog/best-llm-inference-engines ／ https://www.spheron.network/blog/vllm-vs-tensorrt-llm-vs-sglang-benchmarks/ ／ https://deploybase.ai/articles/best-llm-inference-engine ／ llama.cpp多モーダル(mtmd/動画Issue): https://github.com/ggml-org/llama.cpp/issues/17660
- Gemma 4: https://huggingface.co/blog/gemma4 ／ https://ai.google.dev/gemma/docs/core/model_card_4 ／ 音声encoder: https://www.mindstudio.ai/blog/gemma-4-audio-encoder-e2b-e4b-speech-recognition
- VLM比較: https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models ／ https://presenc.ai/research/best-open-weight-vision-language-models-2026
- 使用感/コミュニティ評判(X・Reddit集約): https://note.com/zephel01/n/n0bed69d82aa7 ／ https://dev.to/bean_bean/the-late-april-2026-chinese-llm-stack-qwen-36-deepseek-v4plus-kimi-k26-minimax-m27-glm-51-2bif ／ https://benchlm.ai/blog/posts/best-chinese-llm
- omni比較: https://arxiv.org/html/2509.17765v1 (Qwen3-Omni) ／ https://github.com/openbmb/MiniCPM-V ／ https://stable-learn.com/en/qwen-omni-vsminicpm-v/
- 要約/小型/構造化出力: https://www.siliconflow.com/articles/en/best-open-source-llms-for-summarization ／ https://dev.to/pockit_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk
- 速度計測ツール: LLMPerf https://github.com/ray-project/llmperf ／ llama-bench(同梱) https://github.com/ggml-org/llama.cpp ／ Bench360 https://arxiv.org/pdf/2511.16682 ／ GenAI-Perf解説 https://kchandan.medium.com/llm-inference-benchmarking-genai-perf-and-vllm-5dd06b57428e ／ LocalScore https://www.localscore.ai/ （GuideLLM/GenAI-Perf は名称で検索）
- 能力ハーネス: lm-evaluation-harness https://github.com/EleutherAI/lm-evaluation-harness ／ LightEval https://github.com/huggingface/lighteval ／ OpenCompass https://github.com/open-compass/opencompass ／ VLMEvalKit https://github.com/open-compass/VLMEvalKit
- コードベンチ: SWE-bench https://www.swebench.com/ ／ LiveCodeBench https://livecodebench.github.io/ ／ BigCodeBench https://github.com/bigcode-project/bigcodebench ／ Aider https://aider.chat/docs/leaderboards/ ／ awesome-llm-bench(日次) https://github.com/leoncuhk/awesome-llm-bench ／ CodeSOTA https://www.codesota.com/ ／ BenchLM https://benchlm.ai/coding
- 日本語評価: llm-jp-eval https://github.com/llm-jp/llm-jp-eval ／ llm-jp-eval-mm(VLM) https://github.com/llm-jp/llm-jp-eval-mm ／ Nejumi(W&B) https://github.com/wandb/llm-leaderboard ／ Swallow https://swallow-llm.github.io/leaderboard/about.en.html
- 自前タスク評価/LLM-judge: promptfoo https://www.promptfoo.dev/ ／ DeepEval https://github.com/confident-ai/deepeval ／ RAGAS https://github.com/explodinggradients/ragas ／ Langfuse https://github.com/langfuse/langfuse ／ Arize Phoenix https://github.com/Arize-ai/phoenix

---

### 付記：本版の到達点と次アクション
- **到達点**: 4環境を確定し、**環境ごとの推奨フレームワーク**（Mac=MLX-VLM/Ollama、NVIDIA=vLLM(-Omni)、DGX=vLLM-Omni大型担当）と、**omni対応の現実（フルomni=CUDA専用）**、**単発を主指標にしたベンチ設計**、**モデル選定ツール**、**Phase制のPoC計画**を整備。DGX Sparkを比較対象として維持。
- **次アクション**: §17必須（**DGX有無／omni優先度／コーダ用モデルの視覚要否**）の回答 → GOで **① Mac の Phase 0（Ollama画像＋テキスト）PoC** から着手。
