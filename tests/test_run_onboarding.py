from __future__ import annotations

import csv
import json
from pathlib import Path

from pytest import CaptureFixture

from harness.run_onboarding import main, run_onboarding


def test_run_onboarding_dry_run_row_scores_local_layers(tmp_path: Path) -> None:
    task_set = _write_task_set(tmp_path)
    task_outputs = tmp_path / "outputs.json"
    task_outputs.write_text(
        json.dumps({"sample": {"output": '{"summary":"ローカル評価を行う。","tags":["評価"]}'}}),
        encoding="utf-8",
    )

    result = run_onboarding(
        base_url=None,
        api_key=None,
        model="qwen3-8b",
        env="mac",
        runtime="ollama",
        profile="summarize",
        quantization="q4_k_m",
        revision=None,
        max_model_len=131072,
        prompt_text="hello",
        image=None,
        image_detail=None,
        stop=None,
        max_tokens=32,
        repeats=1,
        warmups=0,
        timeout_s=1.0,
        stream=True,
        capability_bench="llm-jp-eval",
        capability_score=0.73,
        capability_score_json=None,
        capability_metric_key=None,
        task_set_path=task_set,
        task_outputs=task_outputs,
        skip_task=False,
        dry_run_row=True,
    )

    row = result.row.to_csv_record()
    assert row["fit"] == "unknown"
    assert row["std_bench"] == "0.73"
    assert row["task_score"] == "1"
    assert "dry-run-row" in row["notes"]
    assert "task=summary-tags-public-v1:pass=1/1" in row["notes"]


def test_main_does_not_append_results_without_flag(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    results_path = tmp_path / "results.csv"

    code = main(
        [
            "--model",
            "qwen3-8b",
            "--env",
            "mac",
            "--dry-run-row",
            "--capability-bench",
            "llm-jp-eval",
            "--capability-score",
            "0.5",
            "--skip-task",
            "--results",
            str(results_path),
        ]
    )

    assert code == 0
    assert not results_path.exists()
    captured = capsys.readouterr()
    assert json.loads(captured.out)["std_bench"] == "0.5"


def test_main_appends_results_only_with_flag(tmp_path: Path) -> None:
    results_path = tmp_path / "results.csv"

    code = main(
        [
            "--model",
            "qwen3-8b",
            "--env",
            "mac",
            "--dry-run-row",
            "--skip-task",
            "--results",
            str(results_path),
            "--append-results",
        ]
    )

    assert code == 0
    rows = list(csv.DictReader(results_path.read_text(encoding="utf-8").splitlines()))
    assert len(rows) == 1
    assert rows[0]["model"] == "qwen3-8b"
    assert rows[0]["fit"] == "unknown"


def _write_task_set(tmp_path: Path) -> Path:
    path = tmp_path / "summary-tags.yaml"
    path.write_text(
        """
version: summary-tags-public-v1
judge: deterministic-marker-rubric-v1
tasks:
  - id: sample
    input: ローカル LLM 評価を行う。
    expected_summary: ローカル評価。
    summary_markers:
      - ローカル
    tag_markers:
      - 評価
    threshold: 1.0
    source: public-sample
""".lstrip(),
        encoding="utf-8",
    )
    return path
