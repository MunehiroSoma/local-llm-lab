"""Shared typed records for harness results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

FitStatus = Literal["yes", "no", "oom", "error", "unknown"]

RESULT_COLUMNS: tuple[str, ...] = (
    "model",
    "revision",
    "runtime",
    "env",
    "profile",
    "quantization",
    "fit",
    "max_model_len",
    "tok_s",
    "ttft_ms",
    "mm_preprocess_ms",
    "std_bench",
    "task_score",
    "tok_per_j",
    "date",
    "notes",
)


@dataclass(frozen=True)
class ResultRow:
    """One append-only result row for ``results/results.csv``."""

    model: str
    runtime: str
    env: str
    profile: str = ""
    revision: str | None = None
    quantization: str | None = None
    fit: FitStatus = "unknown"
    max_model_len: int | None = None
    tok_s: float | None = None
    ttft_ms: float | None = None
    mm_preprocess_ms: float | None = None
    std_bench: float | None = None
    task_score: float | None = None
    tok_per_j: float | None = None
    run_date: date | None = None
    notes: str = ""

    def to_csv_record(self) -> dict[str, str]:
        """Return a CSV-ready mapping that follows ``RESULT_COLUMNS`` exactly."""
        record = {
            "model": self.model,
            "revision": _format_value(self.revision),
            "runtime": self.runtime,
            "env": self.env,
            "profile": self.profile,
            "quantization": _format_value(self.quantization),
            "fit": self.fit,
            "max_model_len": _format_value(self.max_model_len),
            "tok_s": _format_value(self.tok_s),
            "ttft_ms": _format_value(self.ttft_ms),
            "mm_preprocess_ms": _format_value(self.mm_preprocess_ms),
            "std_bench": _format_value(self.std_bench),
            "task_score": _format_value(self.task_score),
            "tok_per_j": _format_value(self.tok_per_j),
            "date": (self.run_date or date.today()).isoformat(),
            "notes": self.notes,
        }
        return {column: record[column] for column in RESULT_COLUMNS}


def _format_value(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
