"""Run and score summarize/tag golden tasks through promptfoo-style rubrics."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from harness.common.measure import ChatPrompt, TimedCompletion, measure_chat_completion
from harness.common.openai_client import OpenAICompatClient
from harness.common.results import append_result
from harness.common.types import ResultRow
from harness.task.promptfoo.evaluate_json import score_summary_tags
from harness.task.vlm.markers import MarkerGroup, MarkerScore, score_markers

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TASK_SET = REPO_ROOT / "datasets/golden/samples/summary-tags-public-v1.yaml"
DEFAULT_JUDGE = "deterministic-marker-rubric-v1"
SCHEMA_WEIGHT = 0.2
SUMMARY_WEIGHT = 0.4
TAGS_WEIGHT = 0.4


@dataclass(frozen=True)
class SummaryTagTask:
    """One summarize/tag golden task."""

    task_id: str
    input_text: str
    expected_summary: str
    summary_markers: tuple[MarkerGroup, ...]
    tag_markers: tuple[MarkerGroup, ...]
    threshold: float
    source: str


@dataclass(frozen=True)
class SummaryTagTaskSet:
    """A versioned summarize/tag task set with a fixed judge rubric."""

    version: str
    judge: str
    tasks: tuple[SummaryTagTask, ...]


@dataclass(frozen=True)
class SummaryTagTaskResult:
    """Scored output for one summarize/tag task."""

    task: SummaryTagTask
    output: str
    parsed: dict[str, Any] | None
    schema_score: float
    summary_score: MarkerScore
    tag_score: MarkerScore
    score: float
    total_ms: float | None = None
    ttft_ms: float | None = None
    tok_s: float | None = None
    error: str | None = None

    @property
    def passed(self) -> bool:
        """Whether the output passed the fixed rubric threshold."""
        return self.error is None and self.score >= self.task.threshold

    def to_json_record(self) -> dict[str, Any]:
        """Return a JSON-serializable record."""
        return {
            "id": self.task.task_id,
            "source": self.task.source,
            "passed": self.passed,
            "score": self.score,
            "threshold": self.task.threshold,
            "schema_score": self.schema_score,
            "summary_score": _marker_score_record(self.summary_score),
            "tag_score": _marker_score_record(self.tag_score),
            "expected_summary": self.task.expected_summary,
            "parsed": self.parsed,
            "output": self.output,
            "total_ms": self.total_ms,
            "ttft_ms": self.ttft_ms,
            "tok_s": self.tok_s,
            "error": self.error,
        }


def load_task_set(path: Path = DEFAULT_TASK_SET) -> SummaryTagTaskSet:
    """Load summarize/tag golden tasks from YAML."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("task set must be a YAML mapping")
    tasks = raw.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("task set must contain a tasks list")
    return SummaryTagTaskSet(
        version=_required_str(raw, "version"),
        judge=str(raw.get("judge") or DEFAULT_JUDGE),
        tasks=tuple(_parse_task(item) for item in tasks),
    )


def score_output(task: SummaryTagTask, output: str, sample: TimedCompletion | None = None) -> SummaryTagTaskResult:
    """Score one model output against the schema and fixed marker rubric."""
    parsed = _parse_valid_summary_tags(output)
    schema_score = score_summary_tags(output)
    error = None
    if parsed is None:
        error = "output failed summary/tag JSON schema"
        summary_score = score_markers("", task.summary_markers)
        tag_score = score_markers("", task.tag_markers)
    else:
        summary_score = score_markers(str(parsed["summary"]), task.summary_markers)
        tag_score = score_markers(" ".join(cast(list[str], parsed["tags"])), task.tag_markers)
    score = _weighted_score(schema_score, summary_score.ratio, tag_score.ratio)
    if sample is not None and sample.error is not None:
        error = sample.error
    return SummaryTagTaskResult(
        task=task,
        output=output,
        parsed=parsed,
        schema_score=schema_score,
        summary_score=summary_score,
        tag_score=tag_score,
        score=score,
        total_ms=sample.total_ms if sample else None,
        ttft_ms=sample.ttft_ms if sample else None,
        tok_s=sample.tok_s if sample else None,
        error=error,
    )


def score_outputs(
    tasks: Sequence[SummaryTagTask],
    outputs: Mapping[str, str],
) -> tuple[SummaryTagTaskResult, ...]:
    """Score known model outputs without calling a model."""
    return tuple(score_output(task, outputs.get(task.task_id, "")) for task in tasks)


def run_tasks(
    tasks: Sequence[SummaryTagTask],
    client: OpenAICompatClient,
    *,
    model: str,
    max_tokens: int = 256,
    stop: Sequence[str] | None = None,
    stream: bool = True,
) -> tuple[SummaryTagTaskResult, ...]:
    """Run summarize/tag tasks against an OpenAI-compatible endpoint and score outputs."""
    results: list[SummaryTagTaskResult] = []
    for task in tasks:
        sample = _run_one_task(task, client, model=model, max_tokens=max_tokens, stop=stop, stream=stream)
        results.append(score_output(task, sample.content, sample))
    return tuple(results)


def summarize_results(task_set: SummaryTagTaskSet, results: Sequence[SummaryTagTaskResult]) -> dict[str, Any]:
    """Summarize scored summarize/tag task results."""
    scores = [result.score for result in results]
    passed = [result for result in results if result.passed]
    tok_s_values = [result.tok_s for result in results if result.tok_s is not None]
    ttft_values = [result.ttft_ms for result in results if result.ttft_ms is not None]
    return {
        "version": task_set.version,
        "judge": task_set.judge,
        "task_count": len(results),
        "passed_count": len(passed),
        "mean_score": statistics.mean(scores) if scores else 0.0,
        "median_tok_s": statistics.median(tok_s_values) if tok_s_values else None,
        "median_ttft_ms": statistics.median(ttft_values) if ttft_values else None,
        "weights": {"schema": SCHEMA_WEIGHT, "summary": SUMMARY_WEIGHT, "tags": TAGS_WEIGHT},
        "results": [result.to_json_record() for result in results],
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for summarize/tag golden task evaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-set", type=Path, default=DEFAULT_TASK_SET)
    parser.add_argument("--outputs", type=Path, help="JSON outputs to score without calling a model.")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL for live model evaluation.")
    parser.add_argument("--api-key")
    parser.add_argument("--model")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout-s", type=float, default=300.0)
    parser.add_argument("--stop", action="append", help="Optional stop sequence; repeat to pass multiple values.")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    parser.add_argument("--env")
    parser.add_argument("--runtime")
    parser.add_argument("--profile", default="summarize")
    args = parser.parse_args(argv)

    task_set = load_task_set(args.task_set)
    if args.outputs is not None:
        results = score_outputs(task_set.tasks, _load_outputs(args.outputs))
    else:
        if args.base_url is None or args.model is None:
            parser.error("--outputs or (--base-url and --model) is required")
        client = OpenAICompatClient(base_url=args.base_url, api_key=args.api_key, timeout_s=args.timeout_s)
        results = run_tasks(
            task_set.tasks,
            client,
            model=args.model,
            max_tokens=args.max_tokens,
            stop=args.stop,
            stream=not args.no_stream,
        )

    summary = summarize_results(task_set, results)
    if args.append_results:
        if args.model is None or args.env is None or args.runtime is None:
            parser.error("--append-results requires --model, --env, and --runtime")
        append_result(
            args.results,
            _summary_row(summary, model=args.model, env=args.env, runtime=args.runtime, profile=args.profile),
        )
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload + "\n")
    return 0 if summary["passed_count"] == summary["task_count"] else 1


def _run_one_task(
    task: SummaryTagTask,
    client: OpenAICompatClient,
    *,
    model: str,
    max_tokens: int,
    stop: Sequence[str] | None,
    stream: bool,
) -> TimedCompletion:
    prompt = ChatPrompt(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "あなたは評価用の要約・タグ付け器です。必ず JSON オブジェクトのみを返します。",
            },
            {"role": "user", "content": _task_prompt(task.input_text)},
        ],
        max_tokens=max_tokens,
        temperature=0.0,
        stop=stop,
    )
    return measure_chat_completion(client, prompt, stream=stream)


def _task_prompt(input_text: str) -> str:
    return (
        "次の文章を日本語で要約し、内容を表すタグを付けて JSON のみで返してください。\n"
        '形式: {"summary": string, "tags": string[]}\n'
        "制約:\n"
        "- summary は1文から2文で、本文の重要語を落とさない\n"
        "- tags は3個から5個\n"
        "- Markdown、コードフェンス、説明文は出力しない\n\n"
        f"文章:\n{input_text}"
    )


def _parse_task(raw: object) -> SummaryTagTask:
    if not isinstance(raw, dict):
        raise ValueError("each task must be a mapping")
    return SummaryTagTask(
        task_id=_required_str(raw, "id"),
        input_text=_required_str(raw, "input"),
        expected_summary=_required_str(raw, "expected_summary"),
        summary_markers=tuple(_parse_marker_group(item) for item in _required_list(raw, "summary_markers")),
        tag_markers=tuple(_parse_marker_group(item) for item in _required_list(raw, "tag_markers")),
        threshold=float(raw.get("threshold", 1.0)),
        source=_required_str(raw, "source"),
    )


def _parse_marker_group(value: object) -> MarkerGroup:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(cast(list[str], value))
    raise ValueError("markers must be strings or string lists")


def _parse_valid_summary_tags(output: str) -> dict[str, Any] | None:
    if score_summary_tags(output) <= 0:
        return None
    data = json.loads(output)
    if not isinstance(data, dict):
        return None
    return cast(dict[str, Any], data)


def _weighted_score(schema_score: float, summary_score: float, tag_score: float) -> float:
    return round((SCHEMA_WEIGHT * schema_score) + (SUMMARY_WEIGHT * summary_score) + (TAGS_WEIGHT * tag_score), 6)


def _marker_score_record(score: MarkerScore) -> dict[str, Any]:
    return {
        "matched": list(score.matched),
        "missing": [list(group) for group in score.missing],
        "ratio": score.ratio,
        "passed": score.passed,
    }


def _required_str(raw: Mapping[str, object], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_list(raw: Mapping[str, object], key: str) -> list[object]:
    value = raw.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return cast(list[object], value)


def _load_outputs(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return _outputs_from_json(data)


def _outputs_from_json(data: object) -> dict[str, str]:
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return _outputs_from_json(data["results"])
    if isinstance(data, list):
        return {_record_id(item): _record_output(item) for item in data if isinstance(item, dict)}
    if isinstance(data, dict):
        outputs: dict[str, str] = {}
        for key, value in data.items():
            if isinstance(value, str):
                outputs[str(key)] = value
            elif isinstance(value, dict):
                outputs[str(key)] = _record_output(value)
        return outputs
    raise ValueError("outputs JSON must be a mapping or list")


def _record_id(record: Mapping[str, object]) -> str:
    value = record.get("id") or record.get("task_id")
    if not isinstance(value, str) or not value:
        raise ValueError("output record must contain id")
    return value


def _record_output(record: Mapping[str, object]) -> str:
    value = record.get("output") or record.get("content") or record.get("response")
    if isinstance(value, str):
        return value
    raise ValueError("output record must contain output, content, or response")


def _summary_row(summary: Mapping[str, Any], *, model: str, env: str, runtime: str, profile: str) -> ResultRow:
    task_count = int(summary["task_count"])
    passed_count = int(summary["passed_count"])
    notes = f"{summary['version']}; judge={summary['judge']}; pass={passed_count}/{task_count}"
    return ResultRow(
        model=model,
        runtime=runtime,
        env=env,
        profile=profile,
        fit="yes" if passed_count > 0 else "error",
        tok_s=cast(float | None, summary["median_tok_s"]),
        ttft_ms=cast(float | None, summary["median_ttft_ms"]),
        task_score=float(summary["mean_score"]),
        notes=notes,
    )


if __name__ == "__main__":
    raise SystemExit(main())
