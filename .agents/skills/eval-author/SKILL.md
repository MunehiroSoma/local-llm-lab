---
description: Lab-specific hat that designs/runs standard benchmarks and custom task evaluation
name: eval-author
---
# skill: eval-author

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

The lab-specific role "eval-author" defined by AGENT.md. Designs and runs Layer 3 **standard benchmarks**
and Layer 4 **custom task evaluation** of model-onboarding.

## Usage

```
/eval-author <model-id> <evaluation target>
example: /eval-author gemma4-26b-a4b swebench
example: /eval-author gemma4-26b-a4b promptfoo
```

## Prerequisites

- Layers 1-2 (Fit / Speed) must be complete
- The judge model and golden set version must be fixed (if changing them, record the reason in an ADR)
- Do not commit real data if placed in `datasets/golden/` (subject to `.gitignore`; only `samples/` may be public)

## Steps

1. Choose the standard benchmark (Layer 3) appropriate to the target use case
   - Coding: SWE-bench / Aider
   - Multimodal: MMMU
   - Japanese: llm-jp-eval
   - Clarify the pass/fail cutoff criteria for each use case and judge pass/fail
2. Run custom task evaluation (Layer 4) with the `harness/task/promptfoo` or `harness/task/deepeval` configuration
   - Include Japanese-language tasks
   - Run with the judge model and golden set version fixed
3. Reflect the results in the model-onboarding Issue checklist
   - Check `[ ] Layer 3 standard benchmarks` and `[ ] Layer 4 custom task evaluation`, and append scores to the result notes
4. Save raw logs to `results/raw/` and charts/tables to `results/reports/`
5. Once evaluation is complete, hand off to `record-results` and proceed with appending to `results/results.csv` and making the adoption decision

## Items to record (result notes)

- Standard benchmark name, score, and whether the cutoff was passed
- Custom task evaluation score (including Japanese)
- The judge model and golden set version used

## Post-run improvement check (mandatory)

At the end of skill execution, always confirm the following with the human.

1. Impressions of how this run went (what went well)
2. Anything that was hard to use or confusing (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill eval-author`, present improvement proposals, and apply them after approval
- No: record the reason for deferring the update in one line, and confirm the conditions for the next review
