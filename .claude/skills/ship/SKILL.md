---
description: Commit the changes on the current branch, push, and create a PR, all in one flow
metadata:
    github-path: skills/ship
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 7a8633b2cf8d7f4a0ee055cfc53e9821a26be2dd
name: ship
---
# skill: ship

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Commit the changes on the current branch, push, and create a PR, all in one flow.

> This repository's `<MERGE_STYLE>` = **squash** (per conventions.md, fixed).
> Merge only after passing through the AI-DLC Construction phase completion gate (PR review approval).

## Usage

```
/ship <commit message>
example: /ship feat: implement DB schema and migration
```

## Steps

0. Check for a dirty working tree
   ```bash
   git status --short
   ```
   - If there are changes unrelated to the target issue, do not push/PR as-is
   - If dirty, isolate in a temporary worktree or evacuate via `git stash`
   - Do not discard changes (e.g. `git restore`) without user confirmation

1. Check the changed files and verification
   ```bash
   git status
   git diff --stat
   <PRECOMMIT_CMD>   # or <LINT_CMD> / <FORMAT_CMD>
   ```

2. Stage and commit
   ```bash
   git add <relevant files>
   git commit -m "<type>: <summary>"
   ```

3. Push
   ```bash
   git push origin <current-branch>
   ```

4. Create a PR (include `Closes #XX` if there is a related issue; otherwise state `N/A` explicitly)
   ```bash
   gh pr create --title "<type>: <summary>" --body "## Summary
   <description of changes>

   ## Related issue
   Closes #<number>   # N/A if none

   ## Checklist
   - [ ] Happy path verified
   - [ ] Error path verified
   - [ ] Tests added (if applicable)
   - [ ] Verification commands pass"
   ```

5. **Human approval gate (required, cannot be skipped)**
   - Present the PR URL to a human and wait for the review outcome (whether it's OK to merge)
   - This corresponds to the AI-DLC Construction phase transition gate, so do not proceed to step 6 until approval is given

6. Merge and post-processing (only after approval)
   ```bash
   gh pr merge <PR number> --squash --delete-branch
   git checkout main
   git pull origin main
   ```

- Policy: after integration, delete unneeded branches and treat returning to `main` as the end condition for the work
- The merge method follows this repository's convention (conventions.md): **squash, fixed**

## Commit message rules

| type | meaning |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Refactoring |
| `chore` | Configuration change |
| `test` | Test addition/modification |

## Post-execution improvement check (required)

At the end of skill execution, always confirm the following with a human.

1. Impressions of how this run went (what worked well)
2. Points of difficulty or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: Run `/update-skill ship`, present the improvement proposal, and apply it after approval
- No: Record the reason for deferring the update in one line, and confirm the conditions for the next review
