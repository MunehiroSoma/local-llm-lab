from __future__ import annotations

from harness.capability.run import extract_metric
from harness.task.deepeval.rubric import aggregate_scores
from harness.task.promptfoo.evaluate_json import score_summary_tags


def test_score_summary_tags_accepts_expected_schema() -> None:
    assert score_summary_tags('{"summary":"要約","tags":["llm"]}') == 1.0
    assert score_summary_tags('{"summary":"","tags":[]}') == 0.0


def test_aggregate_deepeval_scores() -> None:
    assert aggregate_scores({"testCases": [{"score": 0.5}, {"score": 1.0}]}) == 0.75


def test_extract_metric_from_nested_json() -> None:
    assert extract_metric({"results": {"mmlu": {"acc": 0.61}}}, "results.mmlu.acc") == 0.61
