"""Layer 1 fit smoke test through an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness.common.measure import ChatPrompt, measure_chat_completion
from harness.common.openai_client import OpenAICompatClient
from harness.common.registry import load_registry, model_defaults
from harness.common.results import append_result
from harness.common.types import FitStatus, ResultRow

OOM_MARKERS = ("out of memory", "oom", "cuda error", "memoryerror", "kv cache")


def classify_fit(error: str | None) -> FitStatus:
    """Classify a fit probe error string."""
    if error is None:
        return "yes"
    lowered = error.lower()
    if any(marker in lowered for marker in OOM_MARKERS):
        return "oom"
    return "error"


def run_probe(
    *,
    base_url: str,
    api_key: str | None,
    model: str,
    prompt: str,
    timeout_s: float,
) -> tuple[FitStatus, str]:
    """Run a short completion to verify the model is loaded and usable."""
    client = OpenAICompatClient(base_url=base_url, api_key=api_key, timeout_s=timeout_s)
    timed = measure_chat_completion(
        client,
        ChatPrompt(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1),
        stream=False,
    )
    return classify_fit(timed.error), timed.error or ""


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Layer 1 fit checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key")
    parser.add_argument("--model", required=True)
    parser.add_argument("--env", required=True)
    parser.add_argument("--runtime")
    parser.add_argument("--profile")
    parser.add_argument("--quantization")
    parser.add_argument("--revision")
    parser.add_argument("--max-model-len", type=int)
    parser.add_argument("--prompt", default="Reply with OK.")
    parser.add_argument("--timeout-s", type=float, default=120.0)
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    args = parser.parse_args(argv)

    registry = load_registry()
    defaults = model_defaults(registry, args.model, args.env)
    fit, error = run_probe(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        prompt=args.prompt,
        timeout_s=args.timeout_s,
    )
    row = ResultRow(
        model=args.model,
        revision=args.revision or _optional_string(defaults["revision"]),
        runtime=args.runtime or str(defaults["runtime"]),
        env=args.env,
        profile=args.profile or str(defaults["profile"]),
        quantization=args.quantization or _optional_string(defaults["quantization"]),
        fit=fit,
        max_model_len=args.max_model_len or _optional_int(defaults["max_model_len"]),
        notes=error,
    )
    if args.append_results:
        append_result(args.results, row)
    sys.stdout.write(json.dumps(row.to_csv_record(), ensure_ascii=False) + "\n")
    return 0 if fit == "yes" else 1


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
