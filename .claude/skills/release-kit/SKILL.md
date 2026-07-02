---
description: Reflect skill/template improvements into the public repository and distribute them as a new version
metadata:
    github-path: skills/release-kit
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: c09fddf396dca37737fbce87517b1814676a6fc8
name: release-kit
---
# skill: release-kit

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Reflect improvements to the `ai-dev-kit` plugin (the standard skill/template collection) into the
public GitHub repository and release them. This allows each project's and each trainee's
environment to receive the latest skills via `/plugin update`.

> This skill is the downstream step after `update-skill` (which improves individual skills).
> It **publishes as a distributable artifact** the content refined via update-skill.

## Usage

```
/release-kit <summary of changes>
example: /release-kit Add worktree evacuation steps to ship
```

## Prerequisites

- This repository is already published (or shared) on GitHub as `<owner>/<repo>`
- `gh auth status` passes

## Steps

0. Pre-check
   ```bash
   gh auth status
   git status --short        # confirm the changes to be released are all present
   ```

1. Validate the manifest
   ```bash
   claude plugin validate .
   ```
   - Confirm there are no errors in `marketplace.json` or the skill frontmatter

2. Bump the version (required)
   - Bump `version` in `plugins/ai-dev-kit/.claude-plugin/plugin.json` using SemVer
   - Adding a skill = minor, wording fixes = patch, incompatible structural changes = major
   - Note: leaving `version` unchanged means existing users will not receive the update

3. Record the change history
   - Append a `## <version> (YYYY-MM-DD)` section to `CHANGELOG.md`

4. Commit and tag
   ```bash
   git add -A
   git commit -m "release: ai-dev-kit v<version> — <summary of changes>"
   git tag v<version>
   ```

5. Push
   ```bash
   git push origin main
   git push origin v<version>
   ```

6. Notify trainees/users (depending on installation method)
   - If installed via `gh skill`:
     ```
     gh skill update
     ```
   - If installed via a Claude plugin:
     ```
     /plugin marketplace update ai-dev-training
     /plugin update ai-dev-kit@ai-dev-training
     /reload-plugins
     ```

## Notes

- Manage `version` only on the `plugin.json` side (do not write it in `marketplace.json` — writing it in both causes confusion, since plugin.json takes precedence)
- Pushing to the public repository is an outward-facing, irreversible operation. Present the changes to the user and get approval before pushing
- Always check before pushing that no sensitive information (`.env` / keys / internal-only values) is included

## Post-execution improvement check (required)

At the end of skill execution, always confirm the following with a human.

1. Impressions of how this run went (what worked well)
2. Points of difficulty or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rules

- Yes: Run `/update-skill release-kit`, present the improvement proposal, and apply it after approval
- No: Record the reason for deferring the update in one line, and confirm the conditions for the next review
