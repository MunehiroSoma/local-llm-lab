# gemma4-12b onboarding

Issue: #26

## Model

- Registry id: `gemma4-12b`
- Source repo: `google/gemma-4-12b-it`
- Source revision: `5926caa4ec0cac5cbfadaf4077420520de1d5205`
- Ollama model: `gemma4:12b`
- Ollama local alias: `gemma4-12b`
- Ollama ID: `4eb23ef187e2`
- MLX-VLM runtime repo: `mlx-community/gemma-4-12b-it-4bit`
- MLX-VLM runtime revision: `73bcf09092aa277861d5a191b989b666f7f32e8f`
- Environment: `mac`

## Evidence

- Final report: [`results/reports/2026-07-03-gemma4-12b-onboarding.md`](../../results/reports/2026-07-03-gemma4-12b-onboarding.md)
- Raw evidence: `results/raw/gemma4-12b/` (local only, gitignored)

## Verdict

`hold`.

Ollama and MLX-VLM both fit on the MacBook Pro and both are usable for screenshot VLM tasks. Ollama has the stronger
custom screenshot score (`10 / 10`, mean `0.98`), while MLX-VLM has the faster measured generation speed
(`33.105 tok/s` vs Ollama `28.952 tok/s`).

Do not adopt yet because the fixed `llm-jp-eval` OpenAI-compatible text path returns empty `content` for this model
under the existing standard benchmark condition. Keep it as a strong VLM/concierge candidate and revisit the text
benchmark path when the harness can pass Ollama native `think=false` or otherwise consume the model's answer content.
