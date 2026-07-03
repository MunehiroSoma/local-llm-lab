from __future__ import annotations

from pathlib import Path

import pytest

from harness.common.results import ResultsSchemaError
from harness.common.types import RESULT_COLUMNS
from harness.reporting.results_summary import ReportMetadata, build_markdown, read_results, write_report


def test_read_results_skips_comment_lines(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"
    path.write_text(
        ",".join(RESULT_COLUMNS)
        + "\n"
        + "# comment\n"
        + "model-a,,ollama,mac,summarize,q4,yes,4096,12.5,100,,0.8,0.9,,2026-07-03,adopt; ok\n",
        encoding="utf-8",
    )

    rows = read_results(path)

    assert len(rows) == 1
    assert rows[0].model == "model-a"
    assert rows[0].tok_s == 12.5


def test_read_results_rejects_header_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"
    path.write_text("wrong,header\n", encoding="utf-8")

    with pytest.raises(ResultsSchemaError):
        read_results(path)


def test_build_markdown_contains_metadata_and_speed_chart(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"
    path.write_text(
        ",".join(RESULT_COLUMNS)
        + "\n"
        + "model-a,,ollama,mac,summarize,q4,yes,4096,12.5,100,,0.8,0.9,,2026-07-03,adopt; ok\n"
        + "model-b,,mlx-vlm,mac,vlm,4bit,yes,,25,200,,,1,,2026-07-03,hold; ok\n",
        encoding="utf-8",
    )
    rows = read_results(path)
    metadata = ReportMetadata(
        source_path=path,
        output_path=tmp_path / "report.md",
        git_sha="abc123",
        generated_date="2026-07-03",
        command="generate",
        python_version="3.11",
        quarto_version="not installed",
        plotly_version="not installed",
        kaleido_version="not installed",
    )

    markdown = build_markdown(rows, metadata)

    assert "Git commit: `abc123`" in markdown
    assert "| model | runtime | env | profile | fit | tok_s |" in markdown
    assert "`model-b / mlx-vlm / mac`" in markdown
    assert "`25 tok/s`" in markdown
    assert "results/raw/" in markdown


def test_write_report_creates_parent_directory(tmp_path: Path) -> None:
    source = tmp_path / "results.csv"
    output = tmp_path / "nested" / "report.md"
    source.write_text(
        ",".join(RESULT_COLUMNS)
        + "\n"
        + "model-a,,ollama,mac,summarize,q4,yes,4096,12.5,100,,0.8,0.9,,2026-07-03,adopt; ok\n",
        encoding="utf-8",
    )

    write_report(source, output, "generate")

    assert output.exists()
    assert "Source rows: `1`" in output.read_text(encoding="utf-8")
