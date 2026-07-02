---
description: Start development by cutting a new branch from main
metadata:
    github-path: skills/new-feature
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 85f6bc18f0f05c444c41187f9a7585f51b677ed2
name: new-feature
---
# skill: new-feature

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Cut a new branch from main and start development.

## Usage

```
/new-feature <prefix>/<branch-name>
example: /new-feature feat/eval-runner
example: /new-feature exp/gemma4-mac-swebench
example: /new-feature model/gemma4-26b-a4b
```

## Steps

1. Update main to the latest state
   ```bash
   git checkout main
   git pull origin main
   ```

2. Create the branch and switch to it
   ```bash
   git checkout -b <prefix>/<branch-name>
   ```

3. Confirm the branch name and purpose with the user, then start development

## Branch naming convention (this repo, per conventions.md)

| Prefix | Purpose | Example |
|---|---|---|
| `feat/` | Features (e.g. harness) | `feat/eval-runner` |
| `fix/` | Fixes | `fix/login-retry` |
| `exp/` | Measurement runs / experiments (BOLT) | `exp/gemma4-mac-swebench` |
| `model/<id>` | Model addition / validation (BOLT) | `model/gemma4-26b-a4b` |
| `env/` | Environment setup (runbook/compose) | `env/dgx-spark-vllm` |
| `docs/` | Documentation | `docs/api-reference` |
| `chore/` | Chores / config | `chore/update-deps` |

- All lowercase, hyphen-separated. No Japanese text, spaces, or underscores.
- For a BOLT (Unit of Work = model x environment x evaluation, or a single harness feature), prefer `exp/*` or `model/<id>`.

## Post-run improvement check (required)

At the end of the skill run, always confirm the following with the human.

1. Impressions of how this run went (what worked well)
2. Points of friction or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill new-feature`, present the improvement proposal, and apply it once approved
- No: record the reason for not updating in one line, and confirm the conditions for the next review
