"""Generate static Markdown summaries from ``results/results.csv``."""

from __future__ import annotations

import argparse
import csv
import platform
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from harness.common.results import ResultsSchemaError
from harness.common.types import RESULT_COLUMNS

REPORT_COLUMNS: tuple[str, ...] = (
    "model",
    "runtime",
    "env",
    "profile",
    "fit",
    "tok_s",
    "ttft_ms",
    "std_bench",
    "task_score",
    "date",
    "verdict",
)


@dataclass(frozen=True)
class ReportRow:
    """One parsed result row used by the summary report."""

    model: str
    revision: str
    runtime: str
    env: str
    profile: str
    quantization: str
    fit: str
    max_model_len: str
    tok_s: float | None
    ttft_ms: float | None
    std_bench: float | None
    task_score: float | None
    date: str
    notes: str

    @property
    def key(self) -> tuple[str, str, str, str]:
        """Return the representative grouping key."""
        return (self.model, self.runtime, self.env, self.profile)

    @property
    def verdict(self) -> str:
        """Return the verdict prefix from notes when present."""
        first = self.notes.split(";", maxsplit=1)[0].strip()
        return first if first in {"adopt", "hold", "reject"} else ""


@dataclass(frozen=True)
class ReportMetadata:
    """Metadata stamped into generated reports."""

    source_path: Path
    output_path: Path
    git_sha: str
    generated_date: str
    command: str
    python_version: str
    quarto_version: str
    plotly_version: str
    kaleido_version: str


def read_results(path: Path) -> list[ReportRow]:
    """Read and validate a results CSV file."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(row for row in handle if not row.startswith("#"))
        if tuple(reader.fieldnames or ()) != RESULT_COLUMNS:
            expected = ",".join(RESULT_COLUMNS)
            actual = ",".join(reader.fieldnames or ())
            raise ResultsSchemaError(f"{path} header mismatch: expected {expected!r}, got {actual!r}")
        return [_parse_row(row) for row in reader]


def choose_representative_rows(rows: list[ReportRow]) -> list[ReportRow]:
    """Return the latest row for each model/runtime/env/profile tuple."""
    latest: dict[tuple[str, str, str, str], ReportRow] = {}
    for row in rows:
        previous = latest.get(row.key)
        if previous is None or _sort_key(row) >= _sort_key(previous):
            latest[row.key] = row
    return sorted(latest.values(), key=lambda row: (row.env, row.profile, row.model, row.runtime))


def build_markdown(rows: list[ReportRow], metadata: ReportMetadata) -> str:
    """Build a Markdown report body."""
    representatives = choose_representative_rows(rows)
    lines = [
        "# Results summary report",
        "",
        "## Metadata",
        "",
        f"- Generated date: `{metadata.generated_date}`",
        f"- Source data: `{metadata.source_path}`",
        f"- Source rows: `{len(rows)}`",
        f"- Representative rows: `{len(representatives)}`",
        f"- Git commit: `{metadata.git_sha}`",
        f"- Command: `{metadata.command}`",
        f"- Python: `{metadata.python_version}`",
        f"- Quarto: `{metadata.quarto_version}`",
        f"- Plotly: `{metadata.plotly_version}`",
        f"- kaleido: `{metadata.kaleido_version}`",
        "",
        "## Representative Results",
        "",
        _markdown_table(REPORT_COLUMNS, [_report_record(row) for row in representatives]),
        "",
        "## Speed Chart",
        "",
        "Text bar chart for `tok_s` among representative rows with numeric speed data.",
        "",
        *(_speed_chart(representatives) or ["No numeric `tok_s` values found."]),
        "",
        "## Notes",
        "",
        "- This report reads `results/results.csv` only.",
        "- `results/raw/` is not an input and remains local evidence only.",
        "- `results/results.csv` remains append-only; this command does not modify it.",
        "",
    ]
    return "\n".join(lines)


def write_report(source_path: Path, output_path: Path, command: str) -> None:
    """Generate and write a Markdown report."""
    rows = read_results(source_path)
    metadata = ReportMetadata(
        source_path=source_path,
        output_path=output_path,
        git_sha=_git_sha(),
        generated_date=date.today().isoformat(),
        command=command,
        python_version=platform.python_version(),
        quarto_version=_external_version("quarto", ["quarto", "--version"]),
        plotly_version=_python_package_version("plotly"),
        kaleido_version=_python_package_version("kaleido"),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_markdown(rows, metadata), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Run the results summary CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/results.csv"), help="Input results CSV path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(f"results/reports/{date.today().isoformat()}-results-summary.md"),
        help="Output Markdown report path.",
    )
    args = parser.parse_args(argv)
    command = f"python3 -m harness.reporting.results_summary --input {args.input} --output {args.output}"
    write_report(args.input, args.output, command)
    return 0


def _parse_row(row: dict[str, str]) -> ReportRow:
    return ReportRow(
        model=row["model"],
        revision=row["revision"],
        runtime=row["runtime"],
        env=row["env"],
        profile=row["profile"],
        quantization=row["quantization"],
        fit=row["fit"],
        max_model_len=row["max_model_len"],
        tok_s=_optional_float(row["tok_s"]),
        ttft_ms=_optional_float(row["ttft_ms"]),
        std_bench=_optional_float(row["std_bench"]),
        task_score=_optional_float(row["task_score"]),
        date=row["date"],
        notes=row["notes"],
    )


def _optional_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def _sort_key(row: ReportRow) -> tuple[str, bool, bool, bool]:
    return (
        row.date,
        row.std_bench is not None,
        row.task_score is not None,
        row.tok_s is not None,
    )


def _report_record(row: ReportRow) -> dict[str, str]:
    return {
        "model": row.model,
        "runtime": row.runtime,
        "env": row.env,
        "profile": row.profile,
        "fit": row.fit,
        "tok_s": _format_number(row.tok_s),
        "ttft_ms": _format_number(row.ttft_ms),
        "std_bench": _format_number(row.std_bench),
        "task_score": _format_number(row.task_score),
        "date": row.date,
        "verdict": row.verdict,
    }


def _markdown_table(columns: tuple[str, ...], records: list[dict[str, str]]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(_escape_cell(record[column]) for column in columns) + " |" for record in records]
    return "\n".join([header, separator, *body])


def _speed_chart(rows: list[ReportRow]) -> list[str]:
    numeric = [row for row in rows if row.tok_s is not None]
    if not numeric:
        return []
    max_speed = max(row.tok_s or 0 for row in numeric)
    chart = []
    for row in sorted(numeric, key=lambda candidate: candidate.tok_s or 0, reverse=True):
        width = round(((row.tok_s or 0) / max_speed) * 30) if max_speed else 0
        label = f"{row.model} / {row.runtime} / {row.env}"
        chart.append(f"- `{label}` {_bar(width)} `{_format_number(row.tok_s)} tok/s`")
    return chart


def _bar(width: int) -> str:
    return "#" * max(width, 1)


def _format_number(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6g}"


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def _git_sha() -> str:
    try:
        return subprocess.check_output(  # noqa: S603
            ["git", "rev-parse", "HEAD"],  # noqa: S607
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _external_version(name: str, command: list[str]) -> str:
    if shutil.which(name) is None:
        return "not installed"
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip().splitlines()[0]  # noqa: S603
    except (OSError, subprocess.CalledProcessError, IndexError):
        return "unknown"


def _python_package_version(package: str) -> str:
    try:
        import importlib.metadata

        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


if __name__ == "__main__":
    raise SystemExit(main())
