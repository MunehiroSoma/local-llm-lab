# qwen2.5-vl-7b onboarding

Issue: #28

## Model

- Registry id: `qwen2.5-vl-7b`
- Source repo: `Qwen/Qwen2.5-VL-7B-Instruct`
- Source revision: `cc594898137f460bfe9f0759e9844b3ce807cfb5`
- Runtime repo: `mlx-community/Qwen2.5-VL-7B-Instruct-4bit`
- Runtime revision: `fdcc572e8b05ba9daeaf71be8c9e4267c826ff9b`
- Runtime: `mlx-vlm`
- Environment: `mac`
- Quantization: `4bit`
- Profile: `vlm-screenshot`

## Evidence

- Final report: [`results/reports/2026-07-03-qwen2.5-vl-7b-onboarding.md`](../../results/reports/2026-07-03-qwen2.5-vl-7b-onboarding.md)
- Raw evidence: `results/raw/qwen25-vl-7b/` (local only, gitignored)

## Verdict

`hold`.

Fit and speed are usable on Mac/MLX-VLM, but the current synthetic screenshot task result is `6 / 10`
(`task_score=0.72`). Keep the model as a VLM baseline candidate, but do not adopt it as the preferred screenshot/OCR
baseline over the existing Gemma4 result.
