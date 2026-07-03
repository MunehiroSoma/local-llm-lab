"""Run and score public spec-driven coding-agent task sets."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from harness.common.measure import ChatPrompt, TimedCompletion, measure_chat_completion
from harness.common.openai_client import OpenAICompatClient
from harness.common.results import append_result
from harness.common.types import ResultRow
from harness.task.vlm.markers import MarkerGroup, MarkerScore, score_markers

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TASK_SET = REPO_ROOT / "datasets/golden/samples/coding-agent-public-v1.yaml"
DEFAULT_JUDGE = "deterministic-json-files-pytest-rubric-v1"
SCHEMA_WEIGHT = 0.25
FILES_WEIGHT = 0.25
MARKERS_WEIGHT = 0.25
TESTS_WEIGHT = 0.25


@dataclass(frozen=True)
class ExpectedFile:
    """One required generated file and its marker rubric."""

    path: str
    marker_groups: tuple[MarkerGroup, ...]


@dataclass(frozen=True)
class TestFile:
    """One file written to the temporary test workspace."""

    path: str
    content: str


@dataclass(frozen=True)
class CodingTask:
    """One public spec-driven coding task."""

    task_id: str
    title: str
    source: str
    prompt: str
    expected_files: tuple[ExpectedFile, ...]
    test_files: tuple[TestFile, ...]
    test_command: tuple[str, ...]
    threshold: float


@dataclass(frozen=True)
class CodingTaskSet:
    """A versioned coding-agent task set with a fixed deterministic judge."""

    version: str
    judge: str
    tasks: tuple[CodingTask, ...]


@dataclass(frozen=True)
class GeneratedFile:
    """One file emitted by a model response."""

    path: str
    content: str


@dataclass(frozen=True)
class ParsedPatch:
    """Parsed model response in the fixed public patch schema."""

    files: tuple[GeneratedFile, ...]
    notes: str


@dataclass(frozen=True)
class CodingTaskResult:
    """Scored output for one coding task."""

    task: CodingTask
    output: str
    parsed: ParsedPatch | None
    schema_score: float
    files_score: float
    marker_score: MarkerScore
    tests_score: float
    score: float
    passed: bool
    test_exit: int | None = None
    test_stdout: str = ""
    test_stderr: str = ""
    total_ms: float | None = None
    ttft_ms: float | None = None
    tok_s: float | None = None
    error: str | None = None

    def to_json_record(self) -> dict[str, Any]:
        """Return a JSON-serializable raw evidence record."""
        return {
            "id": self.task.task_id,
            "title": self.task.title,
            "source": self.task.source,
            "passed": self.passed,
            "score": self.score,
            "threshold": self.task.threshold,
            "schema_score": self.schema_score,
            "files_score": self.files_score,
            "marker_score": {
                "matched": list(self.marker_score.matched),
                "missing": [list(group) for group in self.marker_score.missing],
                "ratio": self.marker_score.ratio,
                "passed": self.marker_score.passed,
            },
            "tests_score": self.tests_score,
            "test_exit": self.test_exit,
            "test_stdout": self.test_stdout,
            "test_stderr": self.test_stderr,
            "generated_files": _generated_file_records(self.parsed),
            "output": self.output,
            "total_ms": self.total_ms,
            "ttft_ms": self.ttft_ms,
            "tok_s": self.tok_s,
            "error": self.error,
        }


def load_task_set(path: Path = DEFAULT_TASK_SET) -> CodingTaskSet:
    """Load a versioned coding-agent task set from YAML."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("task set must be a YAML mapping")
    tasks = raw.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("task set must contain a tasks list")
    return CodingTaskSet(
        version=_required_str(raw, "version"),
        judge=str(raw.get("judge") or DEFAULT_JUDGE),
        tasks=tuple(_parse_task(item) for item in tasks),
    )


def score_output(task: CodingTask, output: str, sample: TimedCompletion | None = None) -> CodingTaskResult:
    """Score one model output against the fixed coding-agent rubric."""
    parsed, parse_error = parse_patch_output(output)
    schema_score = 1.0 if parsed is not None else 0.0
    files_score = _score_required_files(task, parsed)
    marker_score = _score_file_markers(task, parsed)
    tests_score, test_exit, test_stdout, test_stderr, test_error = _score_tests(task, parsed)
    error = parse_error or test_error
    if sample is not None and sample.error is not None:
        error = sample.error
    score = _weighted_score(schema_score, files_score, marker_score.ratio, tests_score)
    passed = error is None and score >= task.threshold
    return CodingTaskResult(
        task=task,
        output=output,
        parsed=parsed,
        schema_score=schema_score,
        files_score=files_score,
        marker_score=marker_score,
        tests_score=tests_score,
        score=score,
        passed=passed,
        test_exit=test_exit,
        test_stdout=test_stdout,
        test_stderr=test_stderr,
        total_ms=sample.total_ms if sample else None,
        ttft_ms=sample.ttft_ms if sample else None,
        tok_s=sample.tok_s if sample else None,
        error=error,
    )


def score_outputs(tasks: Sequence[CodingTask], outputs: Mapping[str, str]) -> tuple[CodingTaskResult, ...]:
    """Score known model outputs without calling a model."""
    return tuple(score_output(task, outputs.get(task.task_id, "")) for task in tasks)


def run_tasks(
    tasks: Sequence[CodingTask],
    client: OpenAICompatClient,
    *,
    model: str,
    max_tokens: int = 1024,
    stop: Sequence[str] | None = None,
    stream: bool = True,
) -> tuple[CodingTaskResult, ...]:
    """Run coding tasks against an OpenAI-compatible endpoint and score outputs."""
    results: list[CodingTaskResult] = []
    for task in tasks:
        sample = _run_one_task(task, client, model=model, max_tokens=max_tokens, stop=stop, stream=stream)
        results.append(score_output(task, sample.content, sample))
    return tuple(results)


def parse_patch_output(output: str) -> tuple[ParsedPatch | None, str | None]:
    """Parse a model response into the fixed JSON patch schema."""
    try:
        return _parse_patch_output_strict(output), None
    except ValueError as exc:
        return None, str(exc)


def _parse_patch_output_strict(output: str) -> ParsedPatch:
    if not output:
        raise ValueError("missing output")
    data = _extract_json_object(output)
    generated = _parse_generated_files(data)
    notes = data.get("notes")
    return ParsedPatch(files=tuple(generated), notes=notes if isinstance(notes, str) else "")


def _parse_generated_files(data: Mapping[str, object]) -> list[GeneratedFile]:
    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("output JSON must contain a non-empty files list")
    return [_parse_generated_file(item) for item in files]


def _parse_generated_file(item: object) -> GeneratedFile:
    if not isinstance(item, dict):
        raise ValueError("each files item must be an object")
    path = item.get("path")
    content = item.get("content")
    if not isinstance(path, str) or not path:
        raise ValueError("each files item must contain a non-empty path")
    if not isinstance(content, str):
        raise ValueError("each files item must contain string content")
    _safe_relative_path(path)
    return GeneratedFile(path=path, content=content)


def summarize_results(task_set: CodingTaskSet, results: Sequence[CodingTaskResult]) -> dict[str, Any]:
    """Summarize scored coding-agent task results."""
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
        "weights": {
            "schema": SCHEMA_WEIGHT,
            "files": FILES_WEIGHT,
            "markers": MARKERS_WEIGHT,
            "tests": TESTS_WEIGHT,
        },
        "results": [result.to_json_record() for result in results],
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for public coding-agent task evaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, help="Backward-compatible alias for --task-set.")
    parser.add_argument("--task-set", type=Path, default=DEFAULT_TASK_SET)
    parser.add_argument("--outputs", type=Path, help="JSON outputs to score without calling a model.")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL for live model evaluation.")
    parser.add_argument("--api-key")
    parser.add_argument("--model")
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--timeout-s", type=float, default=300.0)
    parser.add_argument("--stop", action="append", help="Optional stop sequence; repeat to pass multiple values.")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    parser.add_argument("--env")
    parser.add_argument("--runtime")
    parser.add_argument("--profile", default="coding")
    args = parser.parse_args(argv)

    task_set = load_task_set(args.case or args.task_set)
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
    task: CodingTask,
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
                "content": (
                    "You are a coding model under deterministic evaluation. "
                    "Return only one JSON object with files[].path and files[].content."
                ),
            },
            {"role": "user", "content": _task_prompt(task)},
        ],
        max_tokens=max_tokens,
        temperature=0.0,
        stop=stop,
    )
    return measure_chat_completion(client, prompt, stream=stream)


def _task_prompt(task: CodingTask) -> str:
    required = "\n".join(f"- {item.path}" for item in task.expected_files)
    return (
        f"Task ID: {task.task_id}\n"
        f"Title: {task.title}\n\n"
        f"{task.prompt}\n\n"
        "Return JSON only in this schema:\n"
        '{"files":[{"path":"relative/path.py","content":"full file content"}],"notes":"optional"}\n'
        "Required generated files:\n"
        f"{required}\n"
        "Do not include Markdown fences or prose outside the JSON object."
    )


def _parse_task(raw: object) -> CodingTask:
    if not isinstance(raw, dict):
        raise ValueError("each task must be a mapping")
    return CodingTask(
        task_id=_required_str(raw, "id"),
        title=_required_str(raw, "title"),
        source=_required_str(raw, "source"),
        prompt=_required_str(raw, "prompt"),
        expected_files=tuple(_parse_expected_file(item) for item in _required_list(raw, "expected_files")),
        test_files=tuple(_parse_test_file(item) for item in _required_list(raw, "test_files")),
        test_command=tuple(str(item) for item in _required_list(raw, "test_command")),
        threshold=float(raw.get("threshold", 1.0)),
    )


def _parse_expected_file(raw: object) -> ExpectedFile:
    if not isinstance(raw, dict):
        raise ValueError("expected_files entries must be mappings")
    return ExpectedFile(
        path=_required_str(raw, "path"),
        marker_groups=tuple(_parse_marker_group(item) for item in _required_list(raw, "markers")),
    )


def _parse_test_file(raw: object) -> TestFile:
    if not isinstance(raw, dict):
        raise ValueError("test_files entries must be mappings")
    path = _required_str(raw, "path")
    _safe_relative_path(path)
    return TestFile(path=path, content=_required_str(raw, "content"))


def _parse_marker_group(value: object) -> MarkerGroup:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(cast(list[str], value))
    raise ValueError("markers must be strings or string lists")


def _score_required_files(task: CodingTask, parsed: ParsedPatch | None) -> float:
    if parsed is None:
        return 0.0
    generated_paths = {file.path for file in parsed.files}
    matched = sum(1 for expected in task.expected_files if expected.path in generated_paths)
    return matched / len(task.expected_files) if task.expected_files else 1.0


def _score_file_markers(task: CodingTask, parsed: ParsedPatch | None) -> MarkerScore:
    marker_groups: list[MarkerGroup] = []
    output_parts: list[str] = []
    generated = {file.path: file.content for file in parsed.files} if parsed else {}
    for expected in task.expected_files:
        marker_groups.extend(expected.marker_groups)
        output_parts.append(generated.get(expected.path, ""))
    return score_markers("\n".join(output_parts), marker_groups)


def _score_tests(task: CodingTask, parsed: ParsedPatch | None) -> tuple[float, int | None, str, str, str | None]:
    if parsed is None:
        return 0.0, None, "", "", "tests skipped because output schema failed"
    with tempfile.TemporaryDirectory(prefix="coding-agent-eval-") as tmp:
        root = Path(tmp)
        try:
            _write_generated_files(root, parsed.files)
            _write_test_files(root, task.test_files)
        except ValueError as exc:
            return 0.0, None, "", "", str(exc)
        completed = subprocess.run(  # noqa: S603
            list(task.test_command),
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=60.0,
        )
    score = 1.0 if completed.returncode == 0 else 0.0
    return score, completed.returncode, completed.stdout, completed.stderr, None


def _write_generated_files(root: Path, files: Sequence[GeneratedFile]) -> None:
    for file in files:
        path = root / _safe_relative_path(file.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file.content, encoding="utf-8")


def _write_test_files(root: Path, files: Sequence[TestFile]) -> None:
    for file in files:
        path = root / _safe_relative_path(file.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file.content, encoding="utf-8")


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"path must be a safe relative path: {value}")
    return path


def _extract_json_object(output: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    stripped = output.strip()
    candidates = [stripped]
    if "```" in stripped:
        candidates.extend(part.strip() for part in stripped.split("```") if part.strip())
    for candidate in candidates:
        normalized = candidate[4:].strip() if candidate.startswith("json") else candidate
        direct = _try_decode_json_object(decoder, normalized)
        if direct is not None:
            return direct
        embedded = _try_decode_embedded_json_object(decoder, normalized)
        if embedded is not None:
            return embedded
    raise ValueError("output did not contain a JSON object")


def _try_decode_json_object(decoder: json.JSONDecoder, candidate: str) -> dict[str, Any] | None:
    try:
        data, _ = decoder.raw_decode(candidate)
    except json.JSONDecodeError:
        return None
    return cast(dict[str, Any], data) if isinstance(data, dict) else None


def _try_decode_embedded_json_object(decoder: json.JSONDecoder, candidate: str) -> dict[str, Any] | None:
    for index, char in enumerate(candidate):
        if char != "{":
            continue
        data = _try_decode_json_object(decoder, candidate[index:])
        if data is not None:
            return data
    return None


def _weighted_score(schema_score: float, files_score: float, marker_score: float, tests_score: float) -> float:
    return round(
        (SCHEMA_WEIGHT * schema_score)
        + (FILES_WEIGHT * files_score)
        + (MARKERS_WEIGHT * marker_score)
        + (TESTS_WEIGHT * tests_score),
        6,
    )


def _generated_file_records(parsed: ParsedPatch | None) -> list[dict[str, str]]:
    if parsed is None:
        return []
    return [{"path": file.path, "content": file.content} for file in parsed.files]


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
