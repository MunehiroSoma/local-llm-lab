# AGENT.md — local-llm-lab Agent Operating Guide

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this file is written in English.**

Norms for AI agents (Claude Code / Cursor / Copilot, etc.) working in this repository.
For humans, see [README](README.md) / [CONTRIBUTING](CONTRIBUTING.md); decisions live in [docs/adr](docs/adr/);
detailed conventions are in [docs/conventions.md](docs/conventions.md).

## Project
A solo lab running on my own hardware (Mac M4 Pro / RTX 5060 Ti / RTX 5070 / DGX Spark) that does
"framework selection → model comparison → PoC → ongoing evaluation" for local LLM and multimodal (omni) inference.
Source material: [`docs/research/local-llm-multimodal-study.md`](docs/research/local-llm-multimodal-study.md).

## Development method: AI-DLC (AI-Driven Development Life Cycle) + GitHub Flow
Adopts AWS's **AI-DLC**, lightened for solo development (ADR 0005).
Core: **docs-first, phase gates, human approval, short BOLTs, hats (roles)**.

### 3 phases (each transition has a human-approval gate)
| Phase | Meaning in this lab | Artifacts | Gate (human approval) |
|---|---|---|---|
| **Inception** (intent → plan / Mob Elaboration) | What to evaluate/build. Model-addition plan, eval design | Issue (model-onboarding) / ADR / research update | **Approve the plan Issue before starting** |
| **Construction** (design → implement → test) | harness implementation, eval config, experiment (BOLT) execution | `harness/` `envs/` PR / results | **PR review + pre-commit + tests passing** |
| **Operations** (run & keep verifying) | Server ops (`envs/`/runbooks), append to results, regression detection | `results/` reports / tags | **Result acceptance approval → model adoption** |

### BOLT / Unit of Work
- 1 BOLT = a short-lived branch (`exp/*` `model/<id>` `feat/*`) lasting hours to a day.
- Unit of Work = "one (model × environment × eval)" or "one harness feature."

### Hats (roles) = skills / subagents
19 skills live under `.claude/skills/`, grouped into three categories:

| Category | Skills |
|---|---|
| ai-dev-kit skills (core flow) | `start` `new-feature` `create-issue` `sync-main` `ship` `review` `test-check` `long-run` |
| Lab-specific hats (roles) | `fit-tester` (Layer 1 Fit) / `speed-bencher` (Layer 2 Speed) / `eval-author` (Layer 3–4 standard benchmarks & custom eval) / `record-results` (Operations, adoption decision) |
| Governance & distribution | `changelog` `create-readme` `documentation-writer` `git-commit` `refactor` `release-kit` `update-skill` |

`review` runs one subagent per viewpoint category (basic quality / error handling / security / test / design consistency / harness-eval-registry) in parallel and aggregates findings (ADR 0006).

## Ironclad rules (guardrails)
1. **Never advance a phase without human approval** (Inception → Construction → Operations).
2. **Never put real data in `datasets/golden/`** (public repo; samples only).
3. **push / PR / destructive operations only on explicit human instruction**. Never push directly to `main`.
4. **`results/results.csv` is append-only**. Judge model and golden-set version are pinned.
5. Record decisions in ADRs, rationale in `research/` (docs-first).

## Standard flow (1 BOLT)
1. **Inception**: break the plan into right-sized pieces with `create-issue` → human approval
2. `new-feature` (branch from `main`; for model-onboarding, run `fit-tester` → `speed-bencher` → `eval-author` in that order)
3. **Construction**: implement/experiment → `test-check`
4. `pre-commit run --all-files`
5. `ship` (commit [Conventional Commits] → push → PR → human approval → squash merge) → `review`
6. **Operations**: `record-results` — append to `results/`, check for regressions, adoption decision (human approval)

## Commands
| Purpose | Command |
|---|---|
| Check environment | `bash scripts/check_env.sh` |
| Extract candidate models | `bash scripts/whichllm_scan.sh <profile>` |
| Validate | `make validate` / `pre-commit run --all-files` |
| Help | `make help` |

## Documentation system (templates & conventions)

| Type | File |
|---|---|
| Lab requirements spec | [`docs/specs/01_要件定義書.md`](docs/specs/01_要件定義書.md) |
| Generic templates | [`docs/templates/`](docs/templates/) (01_requirements–06_functional-requirements, hearing sheets) |
| Code review checklist | [`docs/coding-standards/review-checklist.md`](docs/coding-standards/review-checklist.md) |
| Python coding standard | [`docs/coding-standards/python.md`](docs/coding-standards/python.md) |
| Web/GUI coding standard | [`docs/coding-standards/web-gui.md`](docs/coding-standards/web-gui.md) |
| JavaScript/TypeScript coding standard | [`docs/coding-standards/javascript-typescript.md`](docs/coding-standards/javascript-typescript.md) |

At PR review time, consult `review-checklist.md` and approve once all Musts are ✓ and CI is green.

## References
- AWS AI-DLC: https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/
- awslabs/aidlc-workflows: https://github.com/awslabs/aidlc-workflows ／ https://ai-dlc.dev/
