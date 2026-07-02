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
   git fetch origin
   git checkout main
   git pull origin main
   ```

3. Return to the original branch and rebase
   ```bash
   git checkout <original-branch>
   git rebase main
   ```

4. If there are conflicts, review the details and report them to the user

## Notes

- After rebasing, `git push --force-with-lease` may be required
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
