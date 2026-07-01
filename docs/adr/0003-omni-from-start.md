# ADR 0003: omni を最初から担う / DGX Spark を omni 主軸ホストに

- ステータス: accepted
- 日付: 2026-07-01

## 背景 / 課題
マルチモーダルを「画像+テキスト先行 → 後で omni」か、最初から omni(音声/動画/音声出力)を狙うか。
DGX Spark は手元にある。

## 決定
**omni を最初から担う**。フェーズは"検証の順序"であり後回しではない。
**④ DGX Spark（128GB）を omni 主軸ホスト**、**② RTX5060Ti(16GB) を副 omni ホスト**（MiniCPM-o 4.5等）。
① Mac は画像+テキスト(+音声入力の一部)に限定（フル omni は CUDA=vLLM-Omni 前提のため対象外）。

## 理由 / 代替案
- フル omni は実質 vLLM-Omni（CUDA）。Mac では不可に近い。
- DGX の 128GB は大型 omni（Qwen3-Omni 30B-A3B 等）の唯一の現実的ホスト。
- omni-from-start は最難関の構築（vLLM-Omni source/Docker, sm_121=CUDA13/NGC）を前倒しする点に留意。

## 影響
research §5, §6.4, §13.2。envs/dgx-spark, envs/rtx-5060ti。
