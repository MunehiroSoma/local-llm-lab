from __future__ import annotations

from harness.capability.adapters import extract_metric
from harness.task.deepeval.rubric import aggregate_scores
from harness.task.promptfoo.evaluate_json import score_summary_tags
from harness.task.promptfoo.summary_tags_eval import (
    DEFAULT_TASK_SET as SUMMARY_TAGS_TASK_SET,
)
from harness.task.promptfoo.summary_tags_eval import (
    load_task_set as load_summary_tags_task_set,
)
from harness.task.promptfoo.summary_tags_eval import (
    score_output as score_summary_tags_output,
)
from harness.task.promptfoo.summary_tags_eval import (
    summarize_results as summarize_summary_tags_results,
)
from harness.task.vlm.markers import score_markers
from harness.task.vlm.screenshot_eval import DEFAULT_TASK_SET, load_task_set, score_outputs, summarize_results


def test_score_summary_tags_accepts_expected_schema() -> None:
    assert score_summary_tags('{"summary":"要約","tags":["llm"]}') == 1.0
    assert score_summary_tags('{"summary":"","tags":[]}') == 0.0


def test_load_summary_tags_task_set() -> None:
    task_set = load_summary_tags_task_set(SUMMARY_TAGS_TASK_SET)

    assert task_set.version == "summary-tags-public-v1"
    assert task_set.judge == "deterministic-marker-rubric-v1"
    assert {task.task_id for task in task_set.tasks} >= {"local-llm-eval-ops", "results-governance"}


def test_score_summary_tags_output_with_fixed_rubric() -> None:
    task_set = load_summary_tags_task_set(SUMMARY_TAGS_TASK_SET)
    task = task_set.tasks[0]
    output = (
        '{"summary":"ローカル LLM を OpenAI 互換 API で評価し、同じプロンプトと固定ルーブリックで比較する。",'
        '"tags":["ローカル LLM","OpenAI 互換 API","評価"]}'
    )

    result = score_summary_tags_output(task, output)
    summary = summarize_summary_tags_results(task_set, [result])

    assert result.passed is True
    assert result.score == 1.0
    assert summary["passed_count"] == 1
    assert summary["mean_score"] == 1.0


def test_aggregate_deepeval_scores() -> None:
    assert aggregate_scores({"testCases": [{"score": 0.5}, {"score": 1.0}]}) == 0.75


def test_extract_metric_from_nested_json() -> None:
    assert extract_metric({"results": {"mmlu": {"acc": 0.61}}}, "results.mmlu.acc") == 0.61


def test_score_markers_accepts_alias_groups() -> None:
    score = score_markers(
        "The chart says most water is saline, while freshwater is in glaciers and ground water.",
        ["fresh", ("salt", "saline"), "glacier", ("groundwater", "ground water")],
    )

    assert score.passed is True
    assert score.ratio == 1.0
    assert score.missing == ()


def test_score_markers_applies_threshold() -> None:
    score = score_markers("The page title is Intellipdia and it has navigation.", ["Intellipedia", "navigation"])

    assert score.passed is False
    assert score.ratio == 0.5


def test_load_screenshot_task_set() -> None:
    tasks = load_task_set(DEFAULT_TASK_SET)

    assert len(tasks) == 10
    assert {task.task_id for task in tasks} >= {"synthetic-ci-failure", "synthetic-chart-tooltip"}
    assert all(task.image.exists() for task in tasks)


def test_score_screenshot_outputs() -> None:
    tasks = load_task_set(DEFAULT_TASK_SET)
    outputs = {
        "synthetic-ci-failure": (
            "The unit-tests job failed with TypeError because None is not iterable. "
            "Run pytest tests/test_task_helpers.py next."
        )
    }

    results = score_outputs(tasks[:1], outputs)
    summary = summarize_results(results)

    assert results[0].score.passed is True
    assert results[0].error is None
    assert summary["passed_count"] == 1
    assert summary["mean_score"] == 1.0
