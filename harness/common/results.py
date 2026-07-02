"""Append-only writer for ``results/results.csv``."""

from __future__ import annotations

import csv
from pathlib import Path

from harness.common.types import RESULT_COLUMNS, ResultRow


class ResultsSchemaError(ValueError):
    """Raised when ``results/results.csv`` does not match the fixed schema."""


def ensure_results_file(path: Path) -> None:
    """Create a results CSV with the fixed header when it does not exist."""
    if path.exists():
        _validate_header(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(RESULT_COLUMNS)


def append_result(path: Path, row: ResultRow) -> None:
    """Append one result row without modifying existing rows."""
    ensure_results_file(path)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writerow(row.to_csv_record())


def _validate_header(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ResultsSchemaError(f"{path} is empty") from exc
    if tuple(header) != RESULT_COLUMNS:
        expected = ",".join(RESULT_COLUMNS)
        actual = ",".join(header)
        raise ResultsSchemaError(f"{path} header mismatch: expected {expected!r}, got {actual!r}")
