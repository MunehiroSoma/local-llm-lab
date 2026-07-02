# llm-jp-4-8b-instruct onboarding report

Date: 2026-07-02
Environment: `mac`
Runtime: `ollama`

| Layer | Result |
|---|---|
| Fit | `yes` |
| Speed | `tok_s=48.7303`, `ttft_ms=185.477` |
| Capability | `llm-jp-eval-smoke-ja-qa-public-v1=1.0` |
| Task | `summary-tags-schema-public-v1=1.0` |
| Verdict | `hold` |

The speed run required `--stop '<|end|>'` because the Ollama GGUF default stop settings returned an empty first chat chunk. The Layer 3 value is a public one-question Japanese QA smoke, not a full official `llm-jp-eval` run.
