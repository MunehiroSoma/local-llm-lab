---
description: Lab-specific hat that measures model speed (tok/s, TTFT, etc.)
name: speed-bencher
---
# skill: speed-bencher

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

The lab-specific role "speed-bencher" defined by AGENT.md. Measures Layer 2 **Speed** of model-onboarding
(single-shot tok/s, TTFT, and, for multimodal cases, preprocessing time).

## Usage

```
/speed-bencher <model-id> <environment>
example: /speed-bencher gemma4-26b-a4b rtx-5070
```

## Prerequisites

- Layer 1 Fit (`fit-tester`) must be complete, with a confirmed loadable configuration
- Use `exp/*` or `model/<id>` as the working branch

## Steps

1. Start the server with the Fit-confirmed configuration (max_model_len, quantization)
2. Measure the following with single-shot inference
   - tok/s (generation speed)
   - TTFT (Time To First Token)
   - If there is multimodal input, preprocessing time (image/audio encoding time)
3. Measure multiple times and check the variance (min/max/median)
4. Reflect the result in the model-onboarding Issue checklist
   - Check `[ ] Layer 2 Speed` and append the measured values to the result notes
5. Save the raw logs to `results/raw/`
6. Once measurement is complete, propose to the human that the task hand off to `eval-author` (standard benchmarks / custom task evaluation)

## Items to record (result notes)

- tok/s (median, min-max)
- TTFT (median, min-max)
- Preprocessing time (if applicable)
- Measurement conditions (prompt length, output length, batch size)

## Post-run improvement check (mandatory)

At the end of skill execution, always confirm the following with the human.

1. Impressions of how this run went (what went well)
2. Anything that was hard to use or confusing (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill speed-bencher`, present improvement proposals, and apply them after approval
- No: record the reason for deferring the update in one line, and confirm the conditions for the next review
