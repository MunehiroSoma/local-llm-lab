---
name: next-work
description: Recommend the next concrete repository task with evidence. Use when the user asks what to do next, asks for the next task or next action, wants priorities after PR/issue work, or wants Codex to consider their workflow habits before choosing follow-up work.
---

# skill: next-work

**IMPORTANT: Always respond to the user in Japanese (日本語). GitHub Issue/PR comments, PR bodies, review summaries, and status comments should also be Japanese unless the user explicitly asks otherwise.**

Use this skill to answer "次にやるべき作業は？" with a concrete, prioritized recommendation instead of a generic plan.

## Workflow

1. Inspect live state before recommending work.

   Prefer current evidence over memory for drift-prone state:

   ```bash
   git status --short --branch
   git branch -vv
   git clean -nd
   git log --oneline --decorate -6
   gh pr list --state open --json number,title,headRefName,baseRefName,mergeable,isDraft,url
   ```

   If the user recently mentioned merged PRs or cleanup, also check:

   ```bash
   git fetch --prune
   gh pr view <number> --json number,state,mergedAt,headRefName,baseRefName,url
   gh issue view <number> --json number,title,state,url,body,comments
   ```

   If network or sandbox restrictions block GitHub checks, state what could not be verified and base the recommendation on local evidence.

2. Rank work in this order.

   1. **Safety / local hygiene**: dirty worktree, untracked files from `git clean -nd`, branch behind `origin/main`, forbidden branch names, or leftover branches after merged PRs.
   2. **Merged PR aftermath**: fast-forward `main`, prune deleted remotes, delete only confirmed obsolete local branches, close or update completed issues.
   3. **Open PR blockers**: conflicts, failing checks, pending checks that should be watched, stale base branches, or stacked PRs that need `rebase --onto`.
   4. **Completion criteria gaps**: missing report updates, missing final verdict, `results/results.csv` approval gate, missing GitHub comments, or open issues that are effectively complete.
   5. **Next smallest BOLT**: choose a concrete child issue or bounded follow-up from the active EPIC. Prefer a short branch-to-PR unit over broad planning.
   6. **Workflow improvement**: when the same friction repeats, suggest turning it into or updating a skill.

3. Apply local-llm-lab defaults when this repository is active.

   - Use branch prefixes from `docs/conventions.md`; never suggest `codex/*` or `claude/*`.
   - Keep GitHub-facing prose in Japanese.
   - Treat `results/results.csv` as append-only; require the Operations approval gate before appending.
   - Keep `results/raw/` as local evidence only and do not suggest committing raw files.
   - After merges, aim for `main` fast-forwarded to `origin/main`, no obsolete local branches, and empty `git clean -nd`.
   - For EPIC work, identify the next child BOLT first. If the user already asked for the whole EPIC, keep moving with milestone updates instead of repeatedly asking for permission.

4. Produce a concise recommendation.

   Use this shape:

   ```markdown
   **次にやるべき作業**
   結論: <one concrete next action>

   理由:
   - <evidence-based reason>
   - <evidence-based reason>

   確認した状態:
   - branch: <current branch and cleanliness>
   - PR: <open/merged/conflict/check status>
   - Issue: <relevant issue status>

   推奨手順:
   1. <step>
   2. <step>
   3. <step>

   後回しでよいこと:
   - <deferred item, if useful>
   ```

   Keep the answer short. Give one primary recommendation, not a long menu, unless the user asks for alternatives.

5. Move from recommendation to action when appropriate.

   If the user asks "お願いします", "進めて", or otherwise approves the recommendation, execute the work end-to-end:

   - switch/create the correct branch when code or docs changes are needed
   - run relevant validation
   - commit, push, and create/update PR when requested by the work
   - update or close GitHub issues in Japanese
   - leave the repository in the cleanest safe state

## Common Recommendations

- If a PR was just merged: run the post-merge cleanup flow before starting new work.
- If only one open PR is mergeable and checks pass: recommend review/merge, then cleanup.
- If an issue's completion criteria are met but it remains open: recommend a final comment and close.
- If an EPIC has multiple open children: recommend the smallest unblocked BOLT with clear validation.
- If `results/results.csv` is involved: recommend presenting the row and comparison before any append, unless approval has already been given.
