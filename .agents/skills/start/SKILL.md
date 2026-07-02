---
description: Check GitHub Issues at the start of work and run everything through branch creation
metadata:
    github-path: skills/start
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: a9941787a8edf6b61d5a95250301b24cec56bc85
name: start
---
# skill: start

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Before starting new work, check GitHub Issues, choose the Issue to work on, and cut a branch.

## Usage

```
/start
```

## Steps

0. Pre-flight check (required)
   ```bash
   command -v gh
   gh auth status
   ```
   - If `gh` is not installed or not logged in, stop processing
   - Always ask the user to perform any installation or authentication operation that requires `sudo`
   - Do not proceed via an API fallback or another route without the user's confirmation

1. Get the list of open Issues
   ```bash
   gh issue list --repo <owner>/<repo> --state open
   ```

2. Check labels and numbers and present work candidates

3. The user chooses which Issue to work on

4. Check the details of the chosen Issue
   ```bash
   gh issue view <number> --repo <owner>/<repo>
   ```

5. Cut a branch appropriate to the Issue type
   ```bash
   git checkout main
   git pull origin main
   git checkout -b <prefix>/<issue-slug>
   # example: feature/db-schema, fix/login-retry
   ```

6. Leave a work-start comment on the Issue (optional)
   ```bash
   gh issue comment <number> --body "Starting work. Branch: <branch-name>"
   ```

## Operating rules (on completion)

- Once the PR for the target Issue is merged, delete the work branch if it is no longer needed
- Return to `main` after the merge work

## Principles when execution errors occur

- If stopped due to insufficient permissions, a missing command, or incomplete authentication, first share the situation with the user and ask them to act
- Only switch to an alternative flow if the user explicitly requests an alternative approach

## Post-run improvement check (required)

At the end of the skill run, always confirm the following with the human.

1. Impressions of how this run went (what worked well)
2. Points of friction or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: run `/update-skill start`, present the improvement proposal, and apply it once approved
- No: record the reason for not updating in one line, and confirm the conditions for the next review
- If there is a related Issue: share the outcome (updated / reason for skipping) as an Issue comment
