from __future__ import annotations

import csv
from pathlib import Path

import pytest

from harness.common.results import ResultsSchemaError, append_result
from harness.common.types import RESULT_COLUMNS, ResultRow


def test_append_result_creates_fixed_header(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"

    append_result(path, ResultRow(model="qwen3-8b", runtime="ollama", env="mac", fit="yes", tok_s=42.0))

    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    assert tuple(rows[0]) == RESULT_COLUMNS
    assert rows[1][0] == "qwen3-8b"
    assert rows[1][8] == "42"
    assert "\r" not in path.read_text(encoding="utf-8")


def test_append_result_rejects_header_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"
    path.write_text("wrong,header\n", encoding="utf-8")

    with pytest.raises(ResultsSchemaError):
        append_result(path, ResultRow(model="qwen3-8b", runtime="ollama", env="mac"))
