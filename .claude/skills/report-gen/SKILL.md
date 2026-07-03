---
description: Generate reproducible static reports from results/results.csv without changing results data
name: report-gen
---
# skill: report-gen

**IMPORTANT: Always respond to the user in Japanese (日本語), even though this skill file is written in English.**

Generates Phase A static reports from `results/results.csv` using the repository-standard reporting command.
This skill is a read-only reporting workflow. It does not collect model evidence, does not use raw logs as input,
and does not append to `results/results.csv`.

## Usage

```
/report-gen <report purpose or output path>
example: /report-gen latest model comparison
example: /report-gen results/reports/2026-07-03-results-summary.md
```

## Scope

- Use for Phase A static reports from committed results data.
- Use the existing command path:
  - `make report-results OUTPUT=<path>`
  - or `python3 -m harness.reporting.results_summary --output <path>`
- Do not use this skill for model adoption decisions. Use `record-results` only after Fit / Speed / Layer evaluations
  and the human approval gate are complete.

## Required Rules

1. Treat `results/results.csv` as the only input data source.
   - Do not read from `results/raw/`.
   - Do not ask the user to commit raw logs.
2. Do not modify `results/results.csv`.
   - WhichLLM candidate extraction and report generation are read-only operations.
   - Only `record-results` may append rows after the explicit human approval gate.
3. Stamp every generated report with reproducibility metadata.
   - Input path: `results/results.csv`
   - Input scope or filter condition
   - Git commit SHA
   - Generation date
   - Generation command
   - Major tool versions when available
4. Keep generated reports under `results/reports/`.
5. Use bounded output in chat and PRs.
   - Summarize report path, row count / scope, and key findings.
   - Do not paste full generated reports unless explicitly requested.

## Standard Procedure

1. Confirm repository state.
   ```bash
   git status --short --branch
   git rev-parse --short HEAD
   git clean -nd
   ```
2. Generate the report.
   ```bash
   make report-results OUTPUT=results/reports/<date>-results-summary.md
   ```
3. Inspect the generated metadata section and confirm it includes commit SHA, input path, input scope,
   generation date, and command.
4. Confirm no forbidden changes happened.
   ```bash
   git diff -- results/results.csv
   git status --short -- results/raw results/results.csv results/reports
   ```
5. Run focused verification.
   ```bash
   python3 -m pytest tests/test_reporting_results_summary.py
   ```
6. In the PR body, record:
   - report command
   - generated report path
   - confirmation that `results/results.csv` was not changed
   - confirmation that `results/raw/` was not used as input and remains uncommitted

## Connection To Other Skills

- `record-results`: append-only results registration after human approval. `report-gen` must not bypass it.
- `review`: run at PR creation time when the report generator or reporting rules changed.

## Playwright MCP Boundary

Playwright MCP is not part of Phase A static report generation. Introduce it when Phase B React + TypeScript + Vite
UI work starts and GUI E2E verification becomes necessary. Until then, connect Playwright as an E2E candidate in
Web/GUI documentation, not as a prerequisite for static report generation.
