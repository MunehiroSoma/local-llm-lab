"""Rubric aggregation helpers for DeepEval and LLM-as-judge outputs."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


def aggregate_scores(report: dict[str, Any], metric_key: str = "score") -> float:
    """Aggregate numeric metric scores from a DeepEval-like JSON report."""
    cases = report.get("testCases") or report.get("cases") or report.get("results")
    if not isinstance(cases, list):
        raise ValueError("report must contain testCases, cases, or results")
    values: list[float] = []
    for case in cases:
        if not isinstance(case, dict):
            continue
        value = case.get(metric_key)
        if isinstance(value, int | float):
            values.append(float(value))
    if not values:
        raise ValueError(f"no numeric {metric_key!r} values found")
    return statistics.mean(values)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for aggregating DeepEval-style reports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--metric-key", default="score")
    args = parser.parse_args(argv)
    score = aggregate_scores(json.loads(args.report.read_text(encoding="utf-8")), args.metric_key)
    sys.stdout.write(json.dumps({"task_score": score}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
