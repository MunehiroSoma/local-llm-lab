---
description: Sync main to the latest state and rebase the current branch
metadata:
    github-path: skills/sync-main
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 523eee0b76f01fe1400af702354ee951a94a9590
name: sync-main
---
# skill: sync-main

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Sync main to the latest state and rebase the current branch onto it.

## Usage

```
/sync-main
```

## Steps

1. Record the current branch
   ```bash
   git branch --show-current
   ```

2. Update main to the latest state
   ```bash
   git fetch --prune origin
   git checkout main
   git pull --ff-only origin main
   ```

3. Choose the correct rebase path before rebasing

   For an ordinary branch based directly on `main`, return to the original branch and rebase:

   ```bash
   git checkout <original-branch>
   git rebase main
   ```

   If the branch was stacked on a PR that was squash-merged, do not run the ordinary rebase first. Use this path
   when the current PR was based on another work branch and that base PR has since been squash-merged into `main`.
   A normal `git rebase main` can replay the pre-squash base commit and create conflicts or duplicate changes.

   First confirm the base PR is actually merged and identify the old base branch or commit:

   ```bash
   gh pr view <base-pr-number> --json number,state,mergedAt,headRefName,baseRefName,url
   git branch -vv
   git log --oneline --decorate --graph --max-count=12 --all
   ```

   Then rebase only the current PR's unique commits onto updated `main`:

   ```bash
   git checkout <original-branch>
   git rebase --onto main <old-base-branch-or-commit>
   ```

   Example:

   ```bash
   git rebase --onto main model/llm-jp-4-8b-instruct-standard-bench
   ```

   Afterward, verify that the PR diff contains only the current branch's intended files:

   ```bash
   git diff --name-status main..HEAD
   gh pr view <current-pr-number> --json number,state,mergeable,baseRefName,headRefName,url
   ```

4. If there are conflicts, review the details and report them to the user

## Notes

- After rebasing, `git push --force-with-lease` may be required
- After a stacked-PR `rebase --onto`, prefer `git push --force-with-lease` over plain force push
- If conflicts are complex, confirm with the user before proceeding

## Post-run improvement check (required)

At the end of the skill run, always confirm the following with the human.

1. Impressions of how this run went (what worked well)
2. Points of friction or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill sync-main`, present the improvement proposal, and apply it once approved
- No: record the reason for not updating in one line, and confirm the conditions for the next review
