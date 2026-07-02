"""Run one spec-driven coding-agent evaluation case."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from harness.common.results import append_result
from harness.common.types import ResultRow

MS_PER_SECOND = 1000.0


@dataclass(frozen=True)
class CodingAgentCase:
    """One executable coding-agent eval case."""

    name: str
    model: str
    runtime: str
    env: str
    profile: str
    agent_command: str
    test_command: str
    workdir: Path


def load_case(path: Path) -> CodingAgentCase:
    """Load a coding-agent eval case from YAML."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("case file must be a YAML mapping")
    return CodingAgentCase(
        name=str(data["name"]),
        model=str(data["model"]),
        runtime=str(data["runtime"]),
        env=str(data["env"]),
        profile=str(data.get("profile", "coding")),
        agent_command=str(data["agent_command"]),
        test_command=str(data["test_command"]),
        workdir=Path(str(data.get("workdir", "."))),
    )


def run_case(case: CodingAgentCase, timeout_s: float) -> tuple[float, str]:
    """Run agent and test commands, returning task score and notes."""
    started = time.perf_counter()
    agent = subprocess.run(shlex.split(case.agent_command), cwd=case.workdir, timeout=timeout_s, check=False)  # noqa: S603
    if agent.returncode != 0:
        elapsed = (time.perf_counter() - started) * MS_PER_SECOND
        return 0.0, f"case={case.name}; agent_exit={agent.returncode}; elapsed_ms={elapsed:.0f}"
    tests = subprocess.run(shlex.split(case.test_command), cwd=case.workdir, timeout=timeout_s, check=False)  # noqa: S603
    elapsed = (time.perf_counter() - started) * MS_PER_SECOND
    score = 1.0 if tests.returncode == 0 else 0.0
    return score, f"case={case.name}; test_exit={tests.returncode}; elapsed_ms={elapsed:.0f}"


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for one coding-agent eval case."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--timeout-s", type=float, default=900.0)
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    args = parser.parse_args(argv)

    case = load_case(args.case)
    score, notes = run_case(case, args.timeout_s)
    row = ResultRow(
        model=case.model,
        runtime=case.runtime,
        env=case.env,
        profile=case.profile,
        fit="yes",
        task_score=score,
        notes=notes,
    )
    if args.append_results:
        append_result(args.results, row)
    sys.stdout.write(json.dumps(row.to_csv_record(), ensure_ascii=False) + "\n")
    return 0 if score > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
