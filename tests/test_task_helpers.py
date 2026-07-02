from __future__ import annotations

from harness.capability.run import extract_metric
from harness.task.deepeval.rubric import aggregate_scores
from harness.task.promptfoo.evaluate_json import score_summary_tags
from harness.task.vlm.markers import score_markers


def test_score_summary_tags_accepts_expected_schema() -> None:
    assert score_summary_tags('{"summary":"要約","tags":["llm"]}') == 1.0
    assert score_summary_tags('{"summary":"","tags":[]}') == 0.0


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
