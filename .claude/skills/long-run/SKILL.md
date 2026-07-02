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
   - **If the run covers multiple Issues, cut one child branch per Issue** and keep them as separate PRs later (keeps `1 BOLT = 1 PR`, per `review-checklist.md`'s PR-meta rule). For a single-Issue/single-BOLT run, one child branch is enough — skip the split-PR steps below.
   - Decide the branch source per Issue by dependency:
     - **Independent** (doesn't touch the same files/decisions as another in-flight Issue in this run): branch from `autopilot/<topic>` directly. These can be reviewed/merged in any order.
     - **Dependent** (edits the same file, or builds on a not-yet-merged prior Issue's ADR/decision in this run): branch from **that prior Issue's own child branch** — not from `autopilot/<topic>` — so the dependency is visible in the branch history (a stacked branch).
   ```bash
   git checkout autopilot/<topic>          # independent case
   git checkout -b feat/<task-slug>

   git checkout feat/<prior-issue-slug>    # dependent case: stack on the prior Issue's branch
   git checkout -b feat/<task-slug>
   ```
3. Verify each child branch on its own (`<PRECOMMIT_CMD>` + tests) before opening its PR. Only merge a child branch into `autopilot/<topic>` if the run's final deliverable is a single combined PR for that topic (single-Issue runs, or when the human explicitly asked for one bundled PR) — otherwise leave child branches unmerged and let each become its own PR (step 4).
4. Open PRs:
   - **Multi-Issue run (default)**: open **one PR per Issue**. Independent-Issue PRs target `main`. Stacked/dependent-Issue PRs target the **prior Issue's branch**, not `main`. Rely on `delete_branch_on_merge` (a repo setting) so that once a base PR is squash-merged and its branch deleted, GitHub auto-retargets the dependent PR's base to `main`. State the required merge order in each stacked PR's description (e.g. "merge after #48").
   - **Single-Issue/single-BOLT run**: create one PR from the child branch (or `autopilot/<topic>` if child branches were merged into it) straight to `main`.
   - **Merge only after human approval, via squash** in all cases (out of scope for autopilot).
5. Do not open PRs directly to `main` from in-progress/unverified child branches.

## GitHub/administrative settings changes (not git)

- Changes applied via `gh api` (or the web UI) to shared repository configuration — branch protection, merge method, Dependabot, CODEOWNERS enablement, private vulnerability reporting, etc. — are **out of autopilot's default authority even under Full Access**, because they affect shared infrastructure, not just code in this repo.
- Treat these exactly like `push`/PR: **pause and get explicit human confirmation before applying**, even when the target Issue itself explicitly asks for the change.

## Execution steps

0. Reconfirm the objective and completion criteria in 1-3 lines
1. Prepare the dedicated autopilot parent branch `autopilot/<topic>`
2. Investigate the impact scope, cut child branches (one per Issue for multi-Issue runs — see Branch operations for stacked vs. independent), and implement in the order that delivers value fastest
3. After implementing, run `<PRECOMMIT_CMD>` and any required tests
4. On failure, self-correct and re-run, repeating until it passes
5. Open PRs per Branch operations (one per Issue by default; a single combined PR only for single-Issue runs or explicit bundling requests)
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
