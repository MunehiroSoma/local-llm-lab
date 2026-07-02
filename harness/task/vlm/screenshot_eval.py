"""Run and score lightweight VLM screenshot task sets."""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from harness.common.measure import ChatPrompt, TimedCompletion, measure_chat_completion
from harness.common.multimodal import build_user_content
from harness.common.openai_client import OpenAICompatClient
from harness.common.results import append_result
from harness.common.types import ResultRow
from harness.task.vlm.markers import MarkerGroup, MarkerScore, score_markers

DEFAULT_TASK_SET = Path(__file__).with_name("screenshot_tasks.yaml")


@dataclass(frozen=True)
class ScreenshotTask:
    """One screenshot VLM task."""

    task_id: str
    image: Path
    category: str
    prompt: str
    expected: str
    marker_groups: tuple[MarkerGroup, ...]
    threshold: float
    source: str


@dataclass(frozen=True)
class ScreenshotTaskResult:
    """Scored output for one screenshot task."""

    task: ScreenshotTask
    output: str
    score: MarkerScore
    total_ms: float | None = None
    ttft_ms: float | None = None
    tok_s: float | None = None
    error: str | None = None

    def to_json_record(self) -> dict[str, Any]:
        """Return a JSON-serializable record."""
        return {
            "id": self.task.task_id,
            "category": self.task.category,
            "image": str(self.task.image),
            "passed": self.score.passed and self.error is None,
            "score": self.score.ratio,
            "threshold": self.task.threshold,
            "matched": list(self.score.matched),
            "missing": [list(group) for group in self.score.missing],
            "output": self.output,
            "total_ms": self.total_ms,
            "ttft_ms": self.ttft_ms,
            "tok_s": self.tok_s,
            "error": self.error,
        }


def load_task_set(path: Path = DEFAULT_TASK_SET) -> tuple[ScreenshotTask, ...]:
    """Load screenshot tasks from YAML."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("task set must be a YAML mapping")
    tasks = raw.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("task set must contain a tasks list")
    return tuple(_parse_task(path.parent, item) for item in tasks)


def score_outputs(
    tasks: Sequence[ScreenshotTask],
    outputs: Mapping[str, str],
) -> tuple[ScreenshotTaskResult, ...]:
    """Score known model outputs against screenshot tasks."""
    results: list[ScreenshotTaskResult] = []
    for task in tasks:
        output = outputs.get(task.task_id, "")
        marker_score = score_markers(output, task.marker_groups, threshold=task.threshold)
        error = None if output else "missing output"
        results.append(ScreenshotTaskResult(task=task, output=output, score=marker_score, error=error))
    return tuple(results)


def run_tasks(
    tasks: Sequence[ScreenshotTask],
    client: OpenAICompatClient,
    *,
    model: str,
    max_tokens: int = 320,
    image_detail: str | None = None,
    stream: bool = True,
) -> tuple[ScreenshotTaskResult, ...]:
    """Run screenshot tasks against an OpenAI-compatible endpoint and score outputs."""
    results: list[ScreenshotTaskResult] = []
    for task in tasks:
        sample = _run_one_task(
            task, client, model=model, max_tokens=max_tokens, image_detail=image_detail, stream=stream
        )
        marker_score = score_markers(sample.content, task.marker_groups, threshold=task.threshold)
        results.append(
            ScreenshotTaskResult(
                task=task,
                output=sample.content,
                score=marker_score,
                total_ms=sample.total_ms,
                ttft_ms=sample.ttft_ms,
                tok_s=sample.tok_s,
                error=sample.error,
            )
        )
    return tuple(results)


def rasterize_svg_tasks(tasks: Sequence[ScreenshotTask], output_dir: Path) -> tuple[ScreenshotTask, ...]:
    """Render SVG task images to PNG files for endpoints that do not accept SVG data URLs."""
    renderer = shutil.which("sips")
    if renderer is None:
        raise RuntimeError("SVG rasterization requires macOS sips in PATH")
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[ScreenshotTask] = []
    for task in tasks:
        if task.image.suffix.casefold() != ".svg":
            rendered.append(task)
            continue
        output_path = (output_dir / f"{task.task_id}.png").resolve()
        completed = subprocess.run(  # noqa: S603
            [renderer, "-s", "format", "png", str(task.image), "--out", str(output_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"failed to rasterize {task.image}: {completed.stderr.strip()}")
        rendered.append(replace(task, image=output_path))
    return tuple(rendered)


def summarize_results(results: Sequence[ScreenshotTaskResult]) -> dict[str, Any]:
    """Summarize scored screenshot task results."""
    scores = [result.score.ratio for result in results]
    passed = [result for result in results if result.score.passed and result.error is None]
    tok_s_values = [result.tok_s for result in results if result.tok_s is not None]
    ttft_values = [result.ttft_ms for result in results if result.ttft_ms is not None]
    return {
        "task_count": len(results),
        "passed_count": len(passed),
        "mean_score": statistics.mean(scores) if scores else 0.0,
        "median_tok_s": statistics.median(tok_s_values) if tok_s_values else None,
        "median_ttft_ms": statistics.median(ttft_values) if ttft_values else None,
        "results": [result.to_json_record() for result in results],
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for screenshot VLM task evaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-set", type=Path, default=DEFAULT_TASK_SET)
    parser.add_argument("--outputs", type=Path, help="JSON outputs to score without calling a model.")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL for live model evaluation.")
    parser.add_argument("--api-key")
    parser.add_argument("--model")
    parser.add_argument("--image-detail")
    parser.add_argument("--raster-dir", type=Path, help="Render SVG task images to PNG files in this directory.")
    parser.add_argument("--max-tokens", type=int, default=320)
    parser.add_argument("--timeout-s", type=float, default=300.0)
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    parser.add_argument("--env")
    parser.add_argument("--runtime")
    parser.add_argument("--profile", default="vlm-screenshot")
    args = parser.parse_args(argv)

    tasks = load_task_set(args.task_set)
    if args.raster_dir is not None:
        tasks = rasterize_svg_tasks(tasks, args.raster_dir)
    if args.outputs is not None:
        results = score_outputs(tasks, _load_outputs(args.outputs))
    else:
        if args.base_url is None or args.model is None:
            parser.error("--outputs or (--base-url and --model) is required")
        client = OpenAICompatClient(base_url=args.base_url, api_key=args.api_key, timeout_s=args.timeout_s)
        results = run_tasks(
            tasks,
            client,
            model=args.model,
            max_tokens=args.max_tokens,
            image_detail=args.image_detail,
            stream=not args.no_stream,
        )

    summary = summarize_results(results)
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
    task: ScreenshotTask,
    client: OpenAICompatClient,
    *,
    model: str,
    max_tokens: int,
    image_detail: str | None,
    stream: bool,
) -> TimedCompletion:
    content = build_user_content(task.prompt, image=task.image, image_detail=image_detail)
    prompt = ChatPrompt(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return measure_chat_completion(client, prompt, stream=stream)


def _parse_task(base_dir: Path, raw: object) -> ScreenshotTask:
    if not isinstance(raw, dict):
        raise ValueError("each task must be a mapping")
    return ScreenshotTask(
        task_id=_required_str(raw, "id"),
        image=(base_dir / _required_str(raw, "image")).resolve(),
        category=_required_str(raw, "category"),
        prompt=_required_str(raw, "prompt"),
        expected=_required_str(raw, "expected"),
        marker_groups=tuple(_parse_marker_group(item) for item in _required_list(raw, "markers")),
        threshold=float(raw.get("threshold", 1.0)),
        source=_required_str(raw, "source"),
    )


def _parse_marker_group(value: object) -> MarkerGroup:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(cast(list[str], value))
    raise ValueError("markers must be strings or string lists")


def _required_str(raw: Mapping[str, object], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_list(raw: Mapping[str, object], key: str) -> list[object]:
    value = raw.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return value


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
    verification = record.get("verification")
    if isinstance(verification, dict):
        nested = verification.get("content") or verification.get("output") or verification.get("response")
        if isinstance(nested, str):
            return nested
    raise ValueError("output record must contain output, content, response, or verification.content")


def _summary_row(summary: Mapping[str, Any], *, model: str, env: str, runtime: str, profile: str) -> ResultRow:
    task_count = int(summary["task_count"])
    passed_count = int(summary["passed_count"])
    notes = f"vlm-screenshot-task-set-v1; pass={passed_count}/{task_count}"
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
