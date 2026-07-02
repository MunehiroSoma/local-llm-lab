---
description: Review the execution results of a used skill and improve its SKILL.md
metadata:
    github-path: skills/update-skill
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: ef1e7db3e18e954824daed85569375362f19baba
name: update-skill
---
# skill: update-skill

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Review the execution of the most recently used skill, identify improvements to its SKILL.md, and update it.
A skill grows every time it is used.

All user-facing GitHub artifacts created during this skill — PR titles/bodies, Issue comments, review summaries, and status comments — must be written in Japanese unless the human explicitly asks for another language.

## Usage

```
/update-skill <skill-name>
example: /update-skill ship
```

## Execution trigger (after running another skill)

At the end of running another skill, always ask the human the following.

1. Impressions of how this run went (what worked well)
2. Points of friction or hesitation (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

- Yes: run `/update-skill <target-skill-name>`
- No: leave the reason for skipping in one line in a related Issue or work note, and confirm the conditions for the next review

## Steps

1. Read the target skill's SKILL.md
   - Claude Code: `.claude/skills/<name>/SKILL.md`
   - Codex (if also used): `.codex/skills/<name>/SKILL.md`

2. Review the most recent execution (from the following perspectives)
   - Were there any steps that were ambiguous and caused hesitation?
   - Were there too many / too few steps?
   - Did any errors or unexpected behavior occur?
   - Was there a simpler or more effective approach?
   - Are the example commands out of date?

3. Present the improvement proposal to the user (clearly showing before / after)

4. Once the user approves, update SKILL.md (if Codex is also used, sync both)

5. Record the outcome in a related Issue or work note

6. Commit the change
   ```bash
   git add .claude/skills/<name>/SKILL.md
   git commit -m "chore: update <name> skill based on usage feedback"
   ```

## Criteria for judging improvements

| Situation | Response |
|---|---|
| Steps are ambiguous and cause hesitation every time | Add concrete examples |
| Steps are too long | Remove / collapse non-essential steps |
| A command produced an error | Fix it to the correct command |
| A new best practice was discovered | Reflect it in the steps |
| There is an unused step | Remove it |

## Notes

- Do not rewrite SKILL.md without the user's approval
- When also using Codex, always keep `.claude/` and `.codex/` in sync
- Always commit changes so they remain in history

## Reconsidering when the existing flow isn't working

If any of the following apply, reconsider the confirmation flow itself.

- The post-run confirmation questions are being skipped
- Even when asked, the Yes/No criteria are unclear and don't lead to an update
- The same improvement point comes up multiple times but is never reflected in SKILL.md

When reconsidering, update the "question wording," "transition conditions," and "how it's recorded in the Issue" together as a set.
