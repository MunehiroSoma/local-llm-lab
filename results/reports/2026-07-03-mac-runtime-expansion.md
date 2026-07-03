# Mac runtime expansion (#85)

Date: 2026-07-03
Host: MacBook Pro M4 Pro, 48 GB unified memory, macOS 26.5, arm64

## Summary

`llama.cpp` と `vLLM Metal` はどちらも Mac M4 Pro 上で導入と smoke が成功した。
`results/results.csv` への追記は Operations approval gate 前なので行っていない。

## llama.cpp Metal

- Source: `~/.local/src/llama.cpp`
- Ref: `b9850` (`4f31eedb0ccf546b7e8d6bb243b170f12522f54d`)
- Build: `cmake -DGGML_METAL=ON`
- Build evidence: configure logで `Including METAL backend`、device logで `Apple M4 Pro`
- Model: `LiquidAI/LFM2.5-1.2B-JP-202606-GGUF:Q4_K_M`
- GGUF snapshot: `8c74801fdfe71394c59d3f519b86de305ff49f00`
- Model type: `lfm2 1.2B Q4_K - Medium`
- Smoke: `llama-cli` が `OK` を生成
- `llama-cli` internal timing: prompt 519.1 t/s, generation 436.9 t/s

`llama-bench -p 128 -n 64 -r 3 -o json`:

| test | avg tok/s | stddev tok/s | samples tok/s |
|---|---:|---:|---|
| prompt 128 | 2695.18 | 2.43 | 2697.68, 2695.04, 2692.83 |
| generation 64 | 248.01 | 3.53 | 247.87, 251.60, 244.55 |

## vLLM Metal

- Venv: `~/.venv-vllm-metal`
- Python: 3.12.9 arm64
- vLLM: `0.24.0+cpu`
- vLLM Metal: `0.3.0.dev20260703073858`
- MLX: `0.31.2`
- MLX-LM: `0.31.3`
- Server model: `Qwen/Qwen3-0.6B`
- Served model name: `qwen3-0.6b`
- max model len: 2048
- Runtime id for harness: `vllm-metal`
- Server evidence: Metal plugin activated, `MLX device set to: Device(gpu, 0)`, PyTorch device `mps`, paged attention enabled.
- `/v1/models`: returned `qwen3-0.6b`

Harness checks without `--append-results`:

| layer | model | runtime | fit | tok/s | TTFT ms |
|---|---|---|---|---:|---:|
| Fit | `qwen3-0.6b` | `vllm-metal` | yes |  |  |
| Speed | `qwen3-0.6b` | `vllm-metal` | yes | 130.35 | 27.3195 |

## Notes

- `qwen3-0.6b` is a vLLM Metal runtime smoke model, not an adoption target.
- CUDA vLLM results must remain separate from `vllm-metal`.
- Raw local logs were kept under `~/.local/var/local-llm-lab/` and are not committed.
