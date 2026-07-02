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

## Usage

```
/create-issue
```

## Issue Types and When to Use Them

| Type | When to use | Label (example) |
|---|---|---|
| **Task Issue** | Per implementation task (granularity completable in 1-3 days) | Phase/type label |
| **Bug Issue** | When a defect in the code is found | `bug` + `priority:S/A/B` |
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

## Example gh Command

```bash
gh issue create --repo <owner>/<repo> \
  --title "[<number>] <title>" \
  --body "..." \
  --label "<label>"
```

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
