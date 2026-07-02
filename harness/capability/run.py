"""Layer 3 adapter for recording standard benchmark scores."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from harness.common.registry import load_registry, model_defaults
from harness.common.results import append_result
from harness.common.types import ResultRow


def extract_metric(data: Any, path: str) -> float:
    """Extract a numeric metric from nested JSON using a dot-separated path."""
    value = data
    for part in path.split("."):
        if isinstance(value, dict):
            value = value[part]
        else:
            raise KeyError(path)
    if not isinstance(value, int | float):
        raise TypeError(f"metric {path!r} is not numeric")
    return float(value)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for recording Layer 3 benchmark scores."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bench", required=True, help="Benchmark name, e.g. mmlu-pro or llm-jp-eval.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--env", required=True)
    parser.add_argument("--runtime")
    parser.add_argument("--profile")
    parser.add_argument("--quantization")
    parser.add_argument("--revision")
    parser.add_argument("--max-model-len", type=int)
    parser.add_argument("--score", type=float)
    parser.add_argument("--score-json", type=Path)
    parser.add_argument("--metric-key")
    parser.add_argument("--command", help="Optional external benchmark command to run before parsing score-json.")
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    args = parser.parse_args(argv)

    if args.command:
        completed = subprocess.run(shlex.split(args.command), check=False)  # noqa: S603
        if completed.returncode != 0:
            return completed.returncode
    score = args.score
    if score is None and args.score_json and args.metric_key:
        score = extract_metric(json.loads(args.score_json.read_text(encoding="utf-8")), args.metric_key)
    if score is None:
        parser.error("--score or (--score-json and --metric-key) is required")

    registry = load_registry()
    defaults = model_defaults(registry, args.model, args.env)
    row = ResultRow(
        model=args.model,
        revision=args.revision or _optional_string(defaults["revision"]),
        runtime=args.runtime or str(defaults["runtime"]),
        env=args.env,
        profile=args.profile or str(defaults["profile"]),
        quantization=args.quantization or _optional_string(defaults["quantization"]),
        fit="yes",
        max_model_len=args.max_model_len or _optional_int(defaults["max_model_len"]),
        std_bench=score,
        notes=f"bench={args.bench}",
    )
    if args.append_results:
        append_result(args.results, row)
    sys.stdout.write(json.dumps(row.to_csv_record(), ensure_ascii=False) + "\n")
    return 0


def _optional_string(value: object | None) -> str | None:
    return None if value is None else str(value)


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return int(str(value))


if __name__ == "__main__":
    raise SystemExit(main())
