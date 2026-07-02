---
name: post-merge-cleanup
description: Clean the local repository after a human merges one or more GitHub PRs. Use when the user says a PR was merged, asks to clean local state before the next task, asks to return to main after merge, or asks to delete merged local branches and verify the worktree is clean.
---

# skill: post-merge-cleanup

**IMPORTANT: Always respond to the user in Japanese (日本語), including GitHub Issue/PR comments created during this skill.**

Bring the local repository back to a safe baseline after human-approved PR merges.

## Goals

- End on `main`, fast-forwarded to `origin/main`.
- Prune deleted remote branches.
- Delete local branches for PRs that are confirmed merged or obsolete coordination branches.
- Verify there are no tracked changes and no untracked files that would be removed by `git clean`.
- Never discard user work silently.

## Workflow

1. Inspect the current state before changing anything.

   ```bash
   git status --short --branch
   git branch -vv
   git clean -nd
   ```

   If tracked changes exist, stop and report them. Do not stash, reset, checkout over, or delete them unless the user explicitly asks.

2. Refresh remote state.

   ```bash
   git fetch --prune
   ```

3. If the user named PR numbers, verify each PR is merged.

   ```bash
   gh pr view <number> --json number,state,mergedAt,headRefName,baseRefName,url
   ```

   If the user did not name PR numbers, infer likely merged branches from `git branch -vv` entries whose upstream is `gone`, then verify with GitHub when possible:

   ```bash
   gh pr list --state merged --head <branch-name> --json number,mergedAt,headRefName,url
   ```

4. Return to current `main`.

   ```bash
   git checkout main
   git pull --ff-only origin main
   ```

   If fast-forward fails, stop and report the exact reason. Do not rebase or merge unless the user explicitly asks.

5. Delete local work branches only after safety checks.

   - Use `git branch -d <branch>` when Git reports the branch is merged into `main`.
   - For squash-merged PR branches, `git branch --merged main` often will not include the branch. Use `git branch -D <branch>` only when GitHub confirms the PR is merged or the remote branch was pruned because the merged PR deleted it.
   - Delete coordination branches such as `chore/<topic>-coordination` only when their child PRs are merged or the branch is clearly obsolete.
   - Never delete `main`.

6. Verify the final state.

   ```bash
   git status --short --branch
   git clean -nd
   git branch -a -vv
   git log --oneline --decorate -3
   ```

   A clean result means:

   - `git status --short --branch` shows `main...origin/main` with no file entries.
   - `git clean -nd` prints nothing.
   - Only expected branches remain, usually `main` and `origin/main`.

## Reporting

Report the final branch, current commit, deleted local branches, whether `git clean -nd` was empty, and any skipped cleanup. Keep the report short.

If anything was skipped because it was unsafe, state the exact blocking condition and the next command or decision needed from the user.
