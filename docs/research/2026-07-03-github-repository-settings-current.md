# GitHub repository settings current state

Date: 2026-07-03
Issue: #43
Repository: `MunehiroSoma/local-llm-lab`
Viewer permission: `ADMIN`

## Summary

Most repository-level settings requested by #43 are already enabled as of this check. The remaining gap is the connection
between CODEOWNERS and branch protection: `.github/CODEOWNERS` exists, but branch protection does not currently require
code owner review or any approving review.

No GitHub admin setting was changed in this branch. This document records live API reads and the exact follow-up setting
needed so the admin change can be approved/applied separately.

## Commands and observed values

Repository merge and cleanup settings:

```bash
gh repo view MunehiroSoma/local-llm-lab \
  --json nameWithOwner,defaultBranchRef,mergeCommitAllowed,rebaseMergeAllowed,squashMergeAllowed,deleteBranchOnMerge,viewerPermission,isPrivate
```

Observed:

```json
{
  "defaultBranchRef": {"name": "main"},
  "deleteBranchOnMerge": true,
  "isPrivate": false,
  "mergeCommitAllowed": false,
  "nameWithOwner": "MunehiroSoma/local-llm-lab",
  "rebaseMergeAllowed": false,
  "squashMergeAllowed": true,
  "viewerPermission": "ADMIN"
}
```

Branch protection:

```bash
gh api repos/MunehiroSoma/local-llm-lab/branches/main/protection \
  --jq '{required_status_checks, enforce_admins, required_pull_request_reviews, restrictions, allow_force_pushes, allow_deletions, block_creations, required_conversation_resolution, lock_branch}'
```

Observed:

```json
{
  "allow_deletions": {"enabled": false},
  "allow_force_pushes": {"enabled": false},
  "block_creations": {"enabled": false},
  "enforce_admins": {"enabled": true},
  "lock_branch": {"enabled": false},
  "required_conversation_resolution": {"enabled": true},
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false,
    "required_approving_review_count": 0
  },
  "required_status_checks": {
    "checks": [{"app_id": 15368, "context": "guard-golden-data"}],
    "contexts": ["guard-golden-data"],
    "strict": true
  },
  "restrictions": null
}
```

Repository rulesets:

```bash
gh api repos/MunehiroSoma/local-llm-lab/rulesets \
  --jq '[.[] | {id,name,target,source_type,enforcement,conditions,rules}]'
```

Observed:

```json
[]
```

Dependabot and security settings:

```bash
gh api -i -X GET repos/MunehiroSoma/local-llm-lab/vulnerability-alerts
gh api repos/MunehiroSoma/local-llm-lab/automated-security-fixes
gh api repos/MunehiroSoma/local-llm-lab/private-vulnerability-reporting
gh api repos/MunehiroSoma/local-llm-lab \
  --jq '{allow_merge_commit,allow_rebase_merge,allow_squash_merge,delete_branch_on_merge,security_and_analysis}'
```

Observed:

```json
{
  "vulnerability_alerts": "HTTP/2.0 204 No Content",
  "automated_security_fixes": {"enabled": true, "paused": false},
  "private_vulnerability_reporting": {"enabled": true},
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "allow_squash_merge": true,
  "delete_branch_on_merge": true,
  "security_and_analysis": {
    "dependabot_security_updates": {"status": "enabled"},
    "secret_scanning": {"status": "enabled"},
    "secret_scanning_push_protection": {"status": "enabled"}
  }
}
```

Dependabot config is present:

```bash
sed -n '1,220p' .github/dependabot.yml
```

Configured ecosystems:

- `github-actions`
- `uv`

CODEOWNERS is present:

```bash
sed -n '1,120p' .github/CODEOWNERS
```

Observed:

```text
# デフォルトのレビュー担当
* @MunehiroSoma
```

## Status against #43

| Requirement | Current status | Evidence |
|---|---|---|
| `main` branch protection | mostly enabled | `enforce_admins=true`, strict `guard-golden-data`, force push disabled, deletion disabled |
| Pull request / review enforcement | gap remains | `required_approving_review_count=0`, `require_code_owner_reviews=false` |
| Repository ruleset | not used | rulesets API returned `[]` |
| Squash-only merge | enabled | merge commit and rebase disabled; squash enabled |
| Delete branch on merge | enabled | `deleteBranchOnMerge=true` |
| Dependabot alerts | enabled | vulnerability alerts endpoint returned HTTP 204 |
| Dependabot security updates | enabled | `dependabot_security_updates.status=enabled` and automated security fixes enabled |
| Dependabot config | present | `.github/dependabot.yml` covers `github-actions` and `uv` |
| Private vulnerability reporting | enabled | `{"enabled": true}` |
| CODEOWNERS file | present | `* @MunehiroSoma` |

## Required admin follow-up

To make CODEOWNERS effective and satisfy the "direct push is physically impossible" intent, update `main` protection or
an equivalent ruleset so that:

- pull requests are required before merging;
- at least one approving review is required;
- code owner review is required;
- `guard-golden-data` remains a strict required check;
- force pushes and deletions remain disabled;
- admins remain included.

The concrete API shape for the branch protection review requirement is:

```bash
gh api \
  --method PATCH \
  repos/MunehiroSoma/local-llm-lab/branches/main/protection/required_pull_request_reviews \
  -f required_approving_review_count=1 \
  -F require_code_owner_reviews=true \
  -F dismiss_stale_reviews=false \
  -F require_last_push_approval=false
```

Apply this only after explicit human approval for the repository admin setting change.
