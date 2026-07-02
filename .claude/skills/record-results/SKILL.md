---
description: Record Operations-phase results in results/results.csv and pass the acceptance approval gate
name: record-results
---
# skill: record-results

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

A skill corresponding to the AI-DLC **Operations** phase (operations and ongoing verification).
Append the measurement results obtained in Construction to `results/results.csv`, check for
regressions, and pass the human approval gate of "accept results -> adopt model".

## Usage

```
/record-results <target model-id or harness feature>
example: /record-results gemma4-26b-a4b
```

## Prerequisites

- The Construction phase (PR merge) is complete
- `results/results.csv` is **append-only** (rewriting or deleting existing rows is prohibited)
- The judge model and golden-set version are fixed (if a change is needed, record it in an ADR first)

## Steps

1. Check the target measurement results (fit / tok_s / ttft / task_score, etc.)
   - For model-onboarding, confirm the Issue checklist (layers 1-4) is fully filled in
2. Assemble one row following the fixed schema of `results/results.csv` (research §12.10)
3. Compare against existing rows and check for regressions (significant performance degradation, score drop)
   - If there is a regression, report the cause to the human and ask for a decision before appending
4. Present the row to be appended to the human
   ```
   Row to append: <CSV row>
   Comparison target: <most recent row under the same conditions, if any>
   Regression: <yes/no, with details if yes>
   ```
5. **Human approval gate (required)**: confirm the decision "adopt / hold / reject" with the human
   - Do not write to `results/results.csv` until approval is given
6. After approval, append to `results/results.csv`
   ```bash
   echo "<CSV row>" >> results/results.csv
   ```
7. Save raw logs to `results/raw/` and charts to `results/reports/` (where applicable)
8. If there is a model-onboarding Issue, leave a comment with the decision and reasoning, then close it
9. If a large results snapshot is needed, suggest tagging `results-YYYYMMDD` to the human

## Regression detection guidelines

| Metric | Guideline for regression |
|---|---|
| task_score | Clear decline compared to the most recent same-condition run |
| tok/s | Significant decline under the same environment and quantization |
| fit (OOM presence) | New OOM at the same max_model_len |

If no clear threshold is defined, present the reasoning to the human and confirm each time.

## Post-run improvement check (required)

At the end of the skill run, always confirm the following with the human.

1. Impressions of how this run went (what worked well)
2. Points of friction or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill record-results`, present the improvement proposal, and apply it once approved
- No: record the reason for not updating in one line, and confirm the conditions for the next review
