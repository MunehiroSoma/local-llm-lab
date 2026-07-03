from __future__ import annotations

from harness.capability.adapters import (
    extract_benchmark_score,
    extract_common_score,
    extract_lm_eval_score,
    extract_metric,
)


def test_extract_metric_supports_nested_dicts_and_lists() -> None:
    data = {"results": [{"score": 0.4}, {"score": 0.8}]}

    assert extract_metric(data, "results.1.score") == 0.8


def test_extract_lm_eval_score_prefers_acc_norm_average() -> None:
    data = {
        "results": {
            "mmlu_pro": {"acc": 0.5, "acc_norm": 0.6},
            "gsm8k": {"exact_match": 0.8},
        }
    }

    assert extract_lm_eval_score(data) == 0.7


def test_extract_llm_jp_style_summary_score() -> None:
    data = {"summary": {"accuracy": 0.73}}

    assert extract_benchmark_score(data, "llm-jp-eval") == 0.73


def test_extract_llm_jp_eval_v2_average_score() -> None:
    data = {"evaluation": {"scores": {"AVG": 0.95}}}

    assert extract_benchmark_score(data, "llm-jp-eval") == 0.95


def test_extract_vlmevalkit_style_case_average() -> None:
    data = {"results": [{"score": 0.5}, {"score": 1.0}]}

    assert extract_benchmark_score(data, "VLMEvalKit") == 0.75


def test_extract_aider_style_pass_rate() -> None:
    data = {"summary": {"pass_rate": 0.42}}

    assert extract_benchmark_score(data, "aider-polyglot") == 0.42


def test_extract_common_score_raises_for_unknown_shape() -> None:
    try:
        extract_common_score({"metadata": {"score_text": "high"}}, scalar_paths=("score",))
    except ValueError as exc:
        assert "no supported benchmark score" in str(exc)
    else:
        raise AssertionError("expected ValueError")
