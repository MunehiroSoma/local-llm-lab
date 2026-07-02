---
description: Lab-specific hat that verifies whether a model can actually be loaded (Fit)
name: fit-tester
---
# skill: fit-tester

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

The lab-specific role "fit-tester" defined by AGENT.md. Verifies Layer 1 **Fit** of model-onboarding
(whether an actual load at the target max_model_len causes an OOM).

## Usage

```
/fit-tester <model-id> <environment>
example: /fit-tester gemma4-26b-a4b mac
```

## Prerequisites

- The target model must already be registered with a pinned revision in `registry/models.yaml`
- The target environment (mac/rtx-5060ti/rtx-5070/dgx-spark) must be defined in `registry/hardware.yaml`
- Use `model/<id>` as the working branch (see the `new-feature` skill)

## Steps

1. Check the target configuration in `registry/models.yaml` / `registry/hardware.yaml`
2. Start the inference server following the runbook (`docs/runbooks/`) for the target environment
3. Actually load the model at the target max_model_len
4. Record whether an OOM occurred, the max_model_len that was actually achievable, and VRAM/memory usage
5. Reflect the result in the model-onboarding Issue checklist
   - Check `[ ] Layer 1 Fit` and append the measured values to the result notes
6. If Fit does not pass, present alternatives to the human (quantization, reducing max_model_len, etc.)
7. Once Fit is confirmed, propose to the human that the task hand off to `speed-bencher`

## Items to record (result notes)

- Whether the actual load succeeded (OK / OOM)
- The actual max_model_len achieved
- VRAM/memory used (GB)
- Quantization settings (if applicable)

## Post-run improvement check (mandatory)

At the end of skill execution, always confirm the following with the human.

1. Impressions of how this run went (what went well)
2. Anything that was hard to use or confusing (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill fit-tester`, present improvement proposals, and apply them after approval
- No: record the reason for deferring the update in one line, and confirm the conditions for the next review
