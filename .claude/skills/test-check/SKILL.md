---
description: Run the implementation-complete verdict checklist and provide a test record template
metadata:
    github-path: skills/test-check
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 4c4f6edf1623c4dbaecc7e4fa7be574154f9f2c7
name: test-check
---
# skill: test-check

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Run the implementation-complete verdict checklist.

## Usage

```
/test-check <target feature name>
example: /test-check EventService
```

## Definition of implementation complete

Do not mark it "complete" until all of the following are satisfied.

- [ ] `<TEST_CMD>` passes
- [ ] `<LINT_CMD>` has no errors
- [ ] `<FORMAT_CMD>` shows no diff
- [ ] The happy path has been verified
- [ ] The error path has been verified (invalid input, external API errors)
- [ ] Issues can be isolated via logs
- [ ] Verification results are recorded (test records under `docs/`)

## Minimum checks for the happy path

- [ ] The expected output is returned
- [ ] The record is saved to the DB (if DB operations are involved)
- [ ] The file is saved (if file output is involved)

## Minimum checks for the error path

- [ ] Invalid input returns an appropriate error
- [ ] On external API failure, an appropriate fallback/error is returned
- [ ] Technical details are retained in the error log

## Completion criteria for model onboarding (harness/eval work)

For `model-onboarding` issues and work on `exp/*` / `model/<id>` branches, do not mark it "complete" until the following are satisfied in addition to the above (research §13.5 / §12.4).

- [ ] Layer 1 **Fit**: No OOM occurs under an actual load (for the target max_model_len)
- [ ] Layer 2 **Speed**: tok/s, TTFT, and (for MM) preprocessing time have been measured
- [ ] Layer 3 **Standard benchmarks**: Use-case-specific screening benchmarks have been run (SWE-bench/Aider/MMMU/llm-jp-eval, etc.)
- [ ] Layer 4 **Custom task evaluation**: promptfoo/DeepEval (including Japanese) have been run
- [ ] One line has been appended to `results/results.csv` (append only; do not rewrite existing rows)
- [ ] The verdict (adopt / hold / reject) and its rationale have been recorded
- [ ] Operations phase acceptance approval (human) has been obtained

## Test case record template

Record in `docs/<category>/TC_<feature-name>.md` using the following format.

```markdown
# TC_<feature name>

## Execution info
- Date: YYYY-MM-DD
- Performed by: <name>

## Happy path
- (what was verified)

## Error path
- (what was verified)

## Unverified
- (unverified items)

## Notes
- (additional remarks)
```

## Post-execution improvement check (required)

At the end of skill execution, always confirm the following with a human.

1. Impressions of how this run went (what worked well)
2. Points of difficulty or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: Run `/update-skill test-check`, present the improvement proposal, and apply it after approval
- No: Record the reason for deferring the update in one line, and confirm the conditions for the next review
