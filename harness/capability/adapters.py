"""Result adapters for standard capability benchmark JSON outputs."""

from __future__ import annotations

import statistics
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

COMMON_SCORE_KEYS: tuple[str, ...] = (
    "score",
    "accuracy",
    "acc",
    "acc_norm",
    "exact_match",
    "f1",
    "pass_rate",
)

LLM_EVAL_METRICS: tuple[str, ...] = ("acc_norm", "acc", "exact_match", "f1")
COMMON_SCALAR_PATHS: tuple[str, ...] = (
    "score",
    "accuracy",
    "avg_score",
    "average",
    "overall",
    "summary.score",
    "summary.accuracy",
    "summary.avg_score",
    "summary.average",
    "summary.overall",
    "results.score",
    "results.accuracy",
    "results.avg_score",
    "results.average",
    "results.overall",
)
AIDER_SCALAR_PATHS: tuple[str, ...] = (
    "pass_rate",
    "percent_cases_passed",
    "solved_rate",
    "summary.pass_rate",
    "summary.percent_cases_passed",
    "results.pass_rate",
    "results.percent_cases_passed",
)


def extract_metric(data: Any, path: str) -> float:
    """Extract a numeric metric from nested JSON using a dot-separated path."""
    value = data
    for part in path.split("."):
        if isinstance(value, dict):
            value = value[part]
        elif isinstance(value, list) and part.isdecimal():
            value = value[int(part)]
        else:
            raise KeyError(path)
    if not isinstance(value, int | float):
        raise TypeError(f"metric {path!r} is not numeric")
    return float(value)


def extract_benchmark_score(data: Any, bench: str, *, metric_key: str | None = None) -> float:
    """Extract a representative score for a known standard benchmark output."""
    if metric_key is not None:
        return extract_metric(data, metric_key)
    normalized = bench.casefold().replace("_", "-")
    if normalized.startswith("lm-eval") or normalized in {"mmlu", "mmlu-pro", "gsm8k", "hellaswag"}:
        return extract_lm_eval_score(data)
    if normalized.startswith("llm-jp"):
        return extract_common_score(data, scalar_paths=COMMON_SCALAR_PATHS)
    if normalized.startswith("vlmeval") or normalized.startswith("vlm-eval"):
        return extract_common_score(data, scalar_paths=COMMON_SCALAR_PATHS)
    if normalized.startswith("aider"):
        return extract_common_score(data, scalar_paths=AIDER_SCALAR_PATHS)
    return extract_common_score(data, scalar_paths=COMMON_SCALAR_PATHS)


def extract_lm_eval_score(data: Any, metrics: Sequence[str] = LLM_EVAL_METRICS) -> float:
    """Extract the mean score from lm-evaluation-harness style results."""
    if not isinstance(data, dict):
        raise ValueError("lm-eval output must be a mapping")
    raw_results = data.get("results")
    if not isinstance(raw_results, dict):
        raise ValueError("lm-eval output must contain a results mapping")
    scores = [_first_numeric(task_result, metrics) for task_result in raw_results.values()]
    return _mean_present(scores, "lm-eval score")


def extract_common_score(data: Any, *, scalar_paths: Sequence[str]) -> float:
    """Extract a scalar score or average common per-case result scores."""
    for path in scalar_paths:
        try:
            return extract_metric(data, path)
        except (KeyError, TypeError, IndexError):
            continue
    if isinstance(data, dict):
        for collection_key in ("results", "testCases", "cases", "records"):
            values = data.get(collection_key)
            scores = _collect_scores(values, COMMON_SCORE_KEYS)
            if scores:
                return statistics.mean(scores)
    raise ValueError("no supported benchmark score found")


def _collect_scores(values: object, keys: Sequence[str]) -> list[float]:
    if isinstance(values, list):
        return _collect_from_records(values, keys)
    if isinstance(values, dict):
        return _collect_from_records(values.values(), keys)
    return []


def _collect_from_records(records: Iterable[object], keys: Sequence[str]) -> list[float]:
    scores: list[float] = []
    for record in records:
        value = _first_numeric(record, keys)
        if value is not None:
            scores.append(value)
    return scores


def _first_numeric(record: object, keys: Sequence[str]) -> float | None:
    if not isinstance(record, Mapping):
        return None
    for key in keys:
        value = record.get(key)
        if isinstance(value, int | float):
            return float(value)
    return None


def _mean_present(values: Iterable[float | None], label: str) -> float:
    present = [value for value in values if value is not None]
    if not present:
        raise ValueError(f"no {label} values found")
    return statistics.mean(present)
