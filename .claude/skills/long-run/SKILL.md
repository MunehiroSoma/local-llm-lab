---
description: Continue long-running work without interruption on a dedicated autopilot branch, integrating into main at the end
metadata:
    github-path: skills/long-run
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 35912196ffd19178c657970ecd86907d8cc2d11d
name: long-run
---
# skill: long-run

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Continue long-running implementation/investigation tasks without unnecessary confirmation pauses.
Do not work directly on `main` — proceed with a dedicated autopilot branch as the parent.

## Usage

```
/long-run <task description>
example: /long-run Proceed with #21 performance verification through to completion
```

## Execution prerequisites

- This skill runs under the assumption of Full Access
- Continue implementation, verification, and fixes until an explicit stop instruction is given
- Share progress at each milestone, but in principle do not ask "may I continue?"
- Where judgment calls are needed, err toward the lower-impact option and keep moving forward
- However, AI-DLC phase transition gates (integration from `autopilot/<topic>` into `main`, Operations acceptance approval) are out of scope for autopilot and must always wait for human approval

## Branch operations (required)

1. Create a dedicated autopilot parent branch from `main`
   ```bash
   git checkout main
   git pull origin main
   git checkout -b autopilot/<topic>
   ```
2. Cut a child branch from the parent branch for each implementation (prefixes follow conventions.md = `feat/` `fix/` `exp/` `model/<id>` `env/` `docs/` `chore/`)
   ```bash
   git checkout autopilot/<topic>
   git checkout -b feat/<task-slug>
   ```
3. After implementing and verifying on the child branch, merge into the parent branch
   ```bash
   git checkout autopilot/<topic>
   git merge --no-ff feat/<task-slug>
   ```
4. Once everything is complete, create a PR from `autopilot/<topic>` to `main`. **Merge only after human approval, via squash** (out of scope for autopilot)
5. Do not open PRs directly to `main` from in-progress child branches

## Execution steps

0. Reconfirm the objective and completion criteria in 1-3 lines
1. Prepare the dedicated autopilot parent branch `autopilot/<topic>`
2. Investigate the impact scope, cut child branches, and implement in the order that delivers value fastest
3. After implementing, run `<PRECOMMIT_CMD>` and any required tests
4. On failure, self-correct and re-run, repeating until it passes
5. Merge child branches into the parent sequentially, then finally create a PR from the parent to `main`
6. Once the completion criteria are met, report the results, unresolved items, and recommended next actions

## Default assumptions

- Keep changes to a minimal diff; do not mix in unnecessary refactoring
- Prioritize related tests, expanding scope as needed

## Notifications (optional)

- For long-running tasks, notifying start/interim/blocked/done to Discord etc. makes tracking easier
- Recommended events: `start` / `checkpoint` / `blocked` / `done`

## Behavior when blocked

- If progress stalls for more than 10 minutes, first try an alternative path forward
- Only if that still doesn't resolve it, ask a single short question

## Post-execution improvement check (required)

At the end of skill execution, always confirm the following with a human.

1. Impressions of how this run went (what worked well)
2. Points of difficulty or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: Run `/update-skill long-run`, present the improvement proposal, and apply it after approval
- No: Record the reason for deferring the update in one line, and confirm the conditions for the next review
