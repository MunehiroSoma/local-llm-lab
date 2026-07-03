"""Run fit, speed, capability, and task layers for a newly onboarded model."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from harness.capability.adapters import extract_benchmark_score
from harness.common.measure import ChatPrompt, benchmark_chat_completion, measure_chat_completion
from harness.common.multimodal import build_user_content
from harness.common.openai_client import OpenAICompatClient
from harness.common.registry import load_registry, model_defaults
from harness.common.results import append_result
from harness.common.types import FitStatus, ResultRow
from harness.fit.openai import classify_fit
from harness.task.promptfoo.summary_tags_eval import (
    DEFAULT_TASK_SET,
    SummaryTagTaskSet,
    load_task_set,
    run_tasks,
    score_outputs,
    summarize_results,
)

DEFAULT_TASK_PROFILE = "summary-tags-public-v1"


@dataclass(frozen=True)
class OnboardingResult:
    """Aggregated onboarding outputs for report and CSV row generation."""

    row: ResultRow
    fit_error: str | None
    capability: dict[str, Any] | None
    task: dict[str, Any] | None

    def to_json_record(self) -> dict[str, Any]:
        """Return a JSON-serializable onboarding report."""
        return {
            "row": self.row.to_csv_record(),
            "fit_error": self.fit_error,
            "capability": self.capability,
            "task": self.task,
        }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for an end-to-end onboarding run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--model", required=True)
    parser.add_argument("--env", required=True)
    parser.add_argument("--runtime")
    parser.add_argument("--profile")
    parser.add_argument("--quantization")
    parser.add_argument("--revision")
    parser.add_argument("--max-model-len", type=int)
    parser.add_argument("--prompt", default="日本語で、ローカルLLM評価の目的を3文で説明してください。")
    parser.add_argument("--image", type=Path, help="Optional image path for VLM fit and speed runs.")
    parser.add_argument("--image-detail", help="Optional OpenAI image detail hint, such as low or high.")
    parser.add_argument("--stop", action="append", help="Optional stop sequence; repeat to pass multiple values.")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout-s", type=float, default=120.0)
    parser.add_argument("--non-streaming", action="store_true")
    parser.add_argument("--capability-bench", help="Layer 3 benchmark name, e.g. llm-jp-eval.")
    parser.add_argument("--capability-score", type=float, help="Layer 3 score already produced by a benchmark.")
    parser.add_argument("--capability-score-json", type=Path, help="Layer 3 benchmark JSON to parse locally.")
    parser.add_argument("--capability-metric-key", help="Dot path override inside --capability-score-json.")
    parser.add_argument("--task-set", type=Path, default=DEFAULT_TASK_SET)
    parser.add_argument("--task-outputs", type=Path, help="Layer 4 outputs JSON to score without a live task run.")
    parser.add_argument("--skip-task", action="store_true")
    parser.add_argument("--raw-dir", type=Path, help="Optional raw report directory, typically results/raw.")
    parser.add_argument("--output-json", type=Path, help="Optional report JSON path.")
    parser.add_argument(
        "--dry-run-row",
        action="store_true",
        help="Generate a row from local inputs without live fit/speed.",
    )
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    args = parser.parse_args(argv)

    if args.base_url is None and not args.dry_run_row:
        parser.error("--base-url is required unless --dry-run-row is set")
    if args.capability_bench is None and (args.capability_score is not None or args.capability_score_json is not None):
        parser.error("--capability-bench is required with capability score inputs")

    registry = load_registry()
    defaults = model_defaults(registry, args.model, args.env)
    result = run_onboarding(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        env=args.env,
        runtime=args.runtime or str(defaults["runtime"]),
        profile=args.profile or str(defaults["profile"]),
        quantization=args.quantization or _optional_string(defaults["quantization"]),
        revision=args.revision or _optional_string(defaults["revision"]),
        max_model_len=args.max_model_len or _optional_int(defaults["max_model_len"]),
        prompt_text=args.prompt,
        image=args.image,
        image_detail=args.image_detail,
        stop=args.stop,
        max_tokens=args.max_tokens,
        repeats=args.repeats,
        warmups=args.warmups,
        timeout_s=args.timeout_s,
        stream=not args.non_streaming,
        capability_bench=args.capability_bench,
        capability_score=args.capability_score,
        capability_score_json=args.capability_score_json,
        capability_metric_key=args.capability_metric_key,
        task_set_path=args.task_set,
        task_outputs=args.task_outputs,
        skip_task=args.skip_task,
        dry_run_row=args.dry_run_row,
    )

    if args.append_results:
        append_result(args.results, result.row)
    report_path = args.output_json or _default_report_path(args.raw_dir, args.model)
    if report_path is not None:
        _write_json(report_path, result.to_json_record())
    sys.stdout.write(json.dumps(result.row.to_csv_record(), ensure_ascii=False) + "\n")
    return _exit_code(result.row.fit, result.task)


def run_onboarding(
    *,
    base_url: str | None,
    api_key: str | None,
    model: str,
    env: str,
    runtime: str,
    profile: str,
    quantization: str | None,
    revision: str | None,
    max_model_len: int | None,
    prompt_text: str,
    image: Path | None,
    image_detail: str | None,
    stop: Sequence[str] | None,
    max_tokens: int,
    repeats: int,
    warmups: int,
    timeout_s: float,
    stream: bool,
    capability_bench: str | None,
    capability_score: float | None,
    capability_score_json: Path | None,
    capability_metric_key: str | None,
    task_set_path: Path,
    task_outputs: Path | None,
    skip_task: bool,
    dry_run_row: bool,
) -> OnboardingResult:
    """Run available onboarding layers and build one final/revised results row."""
    client = None
    if not dry_run_row:
        if base_url is None:
            raise ValueError("base_url is required unless dry_run_row is true")
        client = OpenAICompatClient(base_url=base_url, api_key=api_key, timeout_s=timeout_s)
    fit, fit_error, speed = _run_fit_speed(
        client=client,
        model=model,
        prompt_text=prompt_text,
        image=image,
        image_detail=image_detail,
        stop=stop,
        max_tokens=max_tokens,
        repeats=repeats,
        warmups=warmups,
        stream=stream,
        dry_run_row=dry_run_row,
    )
    capability = _run_capability(
        capability_bench,
        score=capability_score,
        score_json=capability_score_json,
        metric_key=capability_metric_key,
    )
    task = _run_task(
        client=client,
        model=model,
        task_set_path=task_set_path,
        task_outputs=task_outputs,
        skip_task=skip_task,
        max_tokens=max_tokens,
        stop=stop,
        stream=stream,
        enabled=fit == "yes" or dry_run_row,
    )
    row = ResultRow(
        model=model,
        revision=revision,
        runtime=runtime,
        env=env,
        profile=profile,
        quantization=quantization,
        fit=fit,
        max_model_len=max_model_len,
        tok_s=speed["tok_s"] if speed else None,
        ttft_ms=speed["ttft_ms"] if speed else None,
        std_bench=_optional_float(capability, "score"),
        task_score=_optional_float(task, "mean_score"),
        notes=_notes(fit_error=fit_error, capability=capability, task=task, dry_run_row=dry_run_row),
    )
    return OnboardingResult(row=row, fit_error=fit_error, capability=capability, task=task)


def _run_fit_speed(
    *,
    client: OpenAICompatClient | None,
    model: str,
    prompt_text: str,
    image: Path | None,
    image_detail: str | None,
    stop: Sequence[str] | None,
    max_tokens: int,
    repeats: int,
    warmups: int,
    stream: bool,
    dry_run_row: bool,
) -> tuple[FitStatus, str | None, dict[str, float | None] | None]:
    if dry_run_row:
        return "unknown", None, None
    if client is None:
        raise ValueError("client is required for fit/speed")
    user_content = build_user_content(prompt_text, image=image, image_detail=image_detail)
    messages = [{"role": "user", "content": user_content}]
    fit_sample = measure_chat_completion(
        client,
        ChatPrompt(model=model, messages=messages, max_tokens=1, stop=stop),
        stream=stream,
    )
    fit = classify_fit(fit_sample.error)
    if fit != "yes":
        return fit, fit_sample.error, None
    summary = benchmark_chat_completion(
        client,
        ChatPrompt(model=model, messages=messages, max_tokens=max_tokens, stop=stop),
        repeats=repeats,
        warmups=warmups,
        stream=stream,
    )
    return fit, None, {"tok_s": summary.median_tok_s, "ttft_ms": summary.median_ttft_ms}


def _run_capability(
    bench: str | None,
    *,
    score: float | None,
    score_json: Path | None,
    metric_key: str | None,
) -> dict[str, Any] | None:
    if bench is None:
        return None
    resolved_score = score
    if resolved_score is None and score_json is not None:
        resolved_score = extract_benchmark_score(
            json.loads(score_json.read_text(encoding="utf-8")),
            bench,
            metric_key=metric_key,
        )
    if resolved_score is None:
        return {"bench": bench, "status": "skipped", "score": None}
    return {"bench": bench, "status": "ok", "score": resolved_score}


def _run_task(
    *,
    client: OpenAICompatClient | None,
    model: str,
    task_set_path: Path,
    task_outputs: Path | None,
    skip_task: bool,
    max_tokens: int,
    stop: Sequence[str] | None,
    stream: bool,
    enabled: bool,
) -> dict[str, Any] | None:
    if skip_task:
        return None
    task_set = load_task_set(task_set_path)
    if task_outputs is not None:
        results = score_outputs(task_set.tasks, _load_outputs(task_outputs))
    elif enabled and client is not None:
        results = run_tasks(task_set.tasks, client, model=model, max_tokens=max_tokens, stop=stop, stream=stream)
    else:
        return {"version": task_set.version, "judge": task_set.judge, "status": "skipped"}
    summary = summarize_results(task_set, results)
    return _compact_task_summary(task_set, summary)


def _compact_task_summary(task_set: SummaryTagTaskSet, summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "version": task_set.version,
        "judge": task_set.judge,
        "status": "ok",
        "task_count": int(summary["task_count"]),
        "passed_count": int(summary["passed_count"]),
        "mean_score": float(summary["mean_score"]),
        "median_tok_s": cast(float | None, summary["median_tok_s"]),
        "median_ttft_ms": cast(float | None, summary["median_ttft_ms"]),
    }


def _load_outputs(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return _load_outputs_from_json(data["results"])
    return _load_outputs_from_json(data)


def _load_outputs_from_json(data: object) -> dict[str, str]:
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
    raise ValueError("task outputs JSON must be a mapping or list")


def _record_id(record: Mapping[str, object]) -> str:
    value = record.get("id") or record.get("task_id")
    if not isinstance(value, str) or not value:
        raise ValueError("task output record must contain id")
    return value


def _record_output(record: Mapping[str, object]) -> str:
    value = record.get("output") or record.get("content") or record.get("response")
    if isinstance(value, str):
        return value
    raise ValueError("task output record must contain output, content, or response")


def _notes(
    *,
    fit_error: str | None,
    capability: Mapping[str, Any] | None,
    task: Mapping[str, Any] | None,
    dry_run_row: bool,
) -> str:
    parts = ["onboarding"]
    if dry_run_row:
        parts.append("dry-run-row")
    if fit_error:
        parts.append(f"fit_error={fit_error}")
    if capability is not None:
        parts.append(f"capability={capability['bench']}:{capability['status']}")
    if task is not None:
        status = task.get("status")
        if status == "ok":
            parts.append(f"task={task['version']}:pass={task['passed_count']}/{task['task_count']}")
        else:
            parts.append(f"task={task.get('version', DEFAULT_TASK_PROFILE)}:{status}")
    return "; ".join(parts)


def _default_report_path(raw_dir: Path | None, model: str) -> Path | None:
    if raw_dir is None:
        return None
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    return raw_dir / f"{timestamp}-{model}-onboarding.json"


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _exit_code(fit: FitStatus, task: Mapping[str, Any] | None) -> int:
    if fit not in {"yes", "unknown"}:
        return 1
    if task is None or task.get("status") != "ok":
        return 0
    return 0 if task["passed_count"] == task["task_count"] else 1


def _optional_float(mapping: Mapping[str, Any] | None, key: str) -> float | None:
    if mapping is None:
        return None
    value = mapping.get(key)
    return float(value) if isinstance(value, int | float) else None


def _optional_string(value: object | None) -> str | None:
    return None if value is None else str(value)


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return int(str(value))


if __name__ == "__main__":
    raise SystemExit(main())
