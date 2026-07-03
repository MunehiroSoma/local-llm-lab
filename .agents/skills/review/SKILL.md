---
description: Runs viewpoint-scoped subagents in parallel and aggregates findings for review (ADR 0006)
metadata:
    github-path: skills/review
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 4114a3a619b78151c9c68b0f693dfe8980c2e429
name: review
---
# skill: review

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Runs one subagent per viewpoint category from `docs/coding-standards/review-checklist.md` in parallel and aggregates the findings (reflects the ADR 0006 viewpoint-split policy).

## Usage

```
/review <target feature name or file path>
e.g. /review EventService
e.g. /review app/core/event_generation.py
```

## When to run

- Run **only at PR creation time** (after `ship`, before human approval).
- Do not run on every push (mechanical checks are already covered by pre-commit / CI ruff & mypy).

## Launching viewpoint-scoped subagents

Launch one Explore-type subagent per viewpoint category in `docs/coding-standards/review-checklist.md`, in parallel. Each subagent reads only its own viewpoint's checklist file and does not read files owned by other viewpoints.

| Viewpoint | Checklist | Input scope | Target model |
|---|---|---|---|
| Basic quality | `docs/coding-standards/review-checklist/01-basic-quality.md` | Diff only | Lightweight |
| Error handling | `docs/coding-standards/review-checklist/02-error-handling.md` | Diff only | Lightweight |
| Security | `docs/coding-standards/review-checklist/03-security.md` | Diff only | Higher-tier |
| Test | `docs/coding-standards/review-checklist/04-test.md` | Diff only | Lightweight to mid-tier |
| Design consistency | `docs/coding-standards/review-checklist/05-design-consistency.md` | Diff + ADRs / research notes | Higher-tier |
| harness-eval-registry | `docs/coding-standards/review-checklist/06-harness-eval-registry.md` | Diff only (ADRs too if `registry` changes) | Higher-tier |
| Web security / UI (conditional) | `docs/coding-standards/review-checklist/07-web-security.md` | Diff only | Higher-tier |
| Data operations / resource management | `docs/coding-standards/review-checklist/08-data-operations.md` | Diff only | Higher-tier |
| External API integration | `docs/coding-standards/review-checklist/09-external-api.md` | Diff only | Higher-tier |
| CI/CD & supply chain (conditional) | `docs/coding-standards/review-checklist/10-cicd-supply-chain.md` | Diff only | Higher-tier |
| Infra / containers (conditional) | `docs/coding-standards/review-checklist/11-infra-container.md` | Diff only | Higher-tier |

- **Right model for the job**: use a lightweight model for mechanical, convention/format checks (naming, import ordering, forbidden-pattern detection); use a higher-tier model for viewpoints requiring design judgment, harness logic, or architectural consistency.
- **Scale the launch to the change size**: for small diffs (rule of thumb: fewer than 5 files), launch only the main viewpoints (basic quality, error handling, test); for model-onboarding or large harness changes, launch all viewpoints including data operations and external API integration.
- **Conditional viewpoints**: only launch these when the diff matches their trigger, never for unrelated diffs.
  - Web security / UI: diff touches `web/` (React) or a FastAPI backend (ADR 0007 Phase B onward).
    Check XSS / `dangerouslySetInnerHTML`, unauthenticated LAN exposure, React and harness logic separation,
    frontend secret leakage, a11y / UI consistency, Tailwind CSS usage, handwritten CSS suppression,
    and `npm run lint` / `npm run format:check` / `npm run typecheck` execution.
  - CI/CD & supply chain: diff touches `.github/workflows/` or adds/updates a dependency (`pyproject.toml`/`uv.lock`/`web/package.json`).
  - Infra / containers: diff touches `envs/` Docker/compose implementation.

## Noise-suppression rules for viewpoint-scoped subagents (mandatory)

- Do not point out things that are good (findings only)
- Do not propose fixes (fixing is the implementer's/another skill's responsibility)
- Do not flag YAGNI violations (over-engineering)
- Do not flag existing code that is not part of the diff
- Keep each viewpoint's input scope narrow (do not read files/checklists owned by other viewpoints)

## Permission policy

Viewpoint-scoped subagents get **read-only permissions equivalent to Read/Grep/Glob only**. No write access.

## Output format

Viewpoint-scoped subagents must standardize their output to:

```
SEVERITY(Must/Should/Nits) / FILE / LINE / ISSUE / viewpoint
```

Example:

```
Must / app/core/event_generation.py / 42 / Exception swallowed (empty except) / Error handling
Should / app/api/event.py / 10 / Missing timeout / Security
Nits / tests/test_event.py / 5 / Test name doesn't follow naming convention / Test
```

The `review` skill itself aggregates each subagent's output, dedupes, then presents the result.

> If a language-specific convention review is also needed, combine with a separate language-specific skill such as `py-review`.

## Post-run improvement check (mandatory)

At the end of the skill run, always confirm the following with the human.

1. Impressions of this run (what went well)
2. Anything awkward or confusing (usability)
3. Improvement suggestions from the agent (steps / commands / output)
4. Whether to update this skill right now (Yes / No)

### Transition rule

- Yes: run `/update-skill review`, propose improvements, and apply them after approval
- No: record the reason for skipping the update in one line, and confirm the condition for revisiting it next time
