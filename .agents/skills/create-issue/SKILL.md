---
description: Register GitHub Issues with correct granularity and structure
metadata:
    github-path: skills/create-issue
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 8f2916cf3dbbb45f3b08f880a8c62e4f403b1739
name: create-issue
---
# skill: create-issue

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Register GitHub Issues with correct granularity and structure.

## Language Policy

- Write GitHub Issue titles and bodies in Japanese by default.
- Keep code identifiers, package names, commands, labels, and required GitHub keywords in their original language.
- Use another language only when the human explicitly requests it.

## Usage

```
/create-issue
```

## Issue Types and When to Use Them

| Type | When to use | Label (example) |
|---|---|---|
| **Task Issue** | Per implementation task (granularity completable in 1-3 days) | Phase/type label |
| **Bug Issue** | When a defect in the code is found | `bug` + `priority:S/A/B` |
| **Security / Dependency Issue** | When a Dependabot alert, vulnerable dependency, or supply-chain risk needs tracking | `dependencies` + phase/type label |
| **Epic Issue** | Parent issue grouping multiple Tasks | `epic` |

## Pre-Registration Review (Required)

Before running `gh issue create`, always present the following to a human for review.

1. Planned title
2. Planned labels
3. Issue body draft (including checklist and completion criteria)

- Do not create the Issue until the human gives `OK`
- If revision is requested, reflect it, re-present, and only create after approval

---

## Task Issue Template

```
Title: [<number>] <task name>

## Parent Issue
#<number> <parent task name>

## Tasks
- [ ] Task 1
- [ ] Task 2

## Completion Criteria
<specific verification method>
```

## Bug Issue Template

```
Title: [Bug] <problem summary>

## Summary
<what is the problem / scope of impact>

## Problem Location
`<file path>` L<line number>

## Steps to Reproduce
1. ...

## Expected Behavior
...

## Related
- #XX
```

## Security / Dependabot Alert Issue Template

Use this when turning Dependabot alerts, vulnerable packages, or supply-chain findings into an Issue.

Before drafting, collect:

- Alert number(s), if available
- Ecosystem, package name, severity, and vulnerable version range
- Whether GitHub reports a patched version
- Whether the package is a direct dependency or transitive dependency
- Dependency path, if it can be identified from the lockfile or package manager
- Recommended disposition: update, remove, isolate, or risk-accept with rationale

```
Title: [BOLT] Dependabot alert: <package(s)> <decision/action summary>

## Parent Issue
#<number> <parent task name>

## Summary
Dependabot alerts or dependency risk:

- `package-a` / ecosystem / severity / vulnerable: `<range>` / patched: `<version or none>`
- `package-b` / ecosystem / severity / vulnerable: `<range>` / patched: `<version or none>`

Dependency path:
- `<direct package>` is a direct dependency in `<file>`
- `<transitive package>` is pulled in via `<direct package>`

Recommended direction:
- <update/remove/isolate/risk-accept> because <short rationale>

## Tasks
- [ ] Decide whether the dependency is still needed
- [ ] Apply the chosen mitigation or document explicit risk acceptance
- [ ] Update the lockfile if dependencies changed
- [ ] Confirm the alert is resolved, or record why it remains open

## Completion Criteria
- The alert is resolved, or the risk-acceptance rationale is recorded in the Issue
- If dependencies changed, the lockfile is updated and frozen install still works
- Related PR is merged to `main`

## Related
- #XX
```

## Example gh Command

```bash
gh issue create --repo <owner>/<repo> \
  --title "[<number>] <title>" \
  --body "..." \
  --label "<label>"
```

For multi-line Issue bodies, prefer a temporary Markdown file and `--body-file` over shell-escaped
`--body` strings. This avoids quoting mistakes when the body includes backticks, checkboxes, or code blocks.

## Recommended Flow

1. Check existing Issues to avoid duplicates
2. Decide the granularity of the Issue to create (split into multiple if needed)
3. Present the planned title, labels, and body draft to the human
4. After reflecting the human's review, run `gh issue create`
5. Share the resulting URL

## Post-Execution Improvement Check (Required)

At the end of the skill execution, always confirm the following with the human.

1. Impressions of how this session went (what went well)
2. Points that were hard to use / caused hesitation (usability)
3. Improvement suggestions from the agent (procedure / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition Rules

- Yes: Run `/update-skill create-issue`, present the improvement proposal, and reflect it after approval
- No: Record the reason for deferring the update in one line, and confirm the condition for the next review
