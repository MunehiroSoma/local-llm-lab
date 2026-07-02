"""Layer 2 speed benchmark through an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness.common.measure import ChatPrompt, benchmark_chat_completion
from harness.common.multimodal import build_user_content
from harness.common.openai_client import OpenAICompatClient
from harness.common.registry import load_registry, model_defaults
from harness.common.results import append_result
from harness.common.types import FitStatus, ResultRow


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Layer 2 speed benchmarks."""
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
    parser.add_argument("--prompt", default="日本語で、ローカルLLM評価の要点を3文で説明してください。")
    parser.add_argument("--image", type=Path, help="Optional image path for VLM speed benchmarks.")
    parser.add_argument("--image-detail", help="Optional OpenAI image detail hint, such as low or high.")
    parser.add_argument("--stop", action="append", help="Optional stop sequence; repeat to pass multiple values.")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout-s", type=float, default=120.0)
    parser.add_argument("--non-streaming", action="store_true")
    parser.add_argument("--mm-preprocess-ms", type=float)
    parser.add_argument("--results", type=Path, default=Path("results/results.csv"))
    parser.add_argument("--append-results", action="store_true")
    args = parser.parse_args(argv)

    registry = load_registry()
    defaults = model_defaults(registry, args.model, args.env)
    client = OpenAICompatClient(base_url=args.base_url, api_key=args.api_key, timeout_s=args.timeout_s)
    summary = benchmark_chat_completion(
        client,
        ChatPrompt(
            model=args.model,
            messages=[
                {
                    "role": "user",
                    "content": build_user_content(args.prompt, image=args.image, image_detail=args.image_detail),
                }
            ],
            max_tokens=args.max_tokens,
            stop=args.stop,
        ),
        repeats=args.repeats,
        warmups=args.warmups,
        stream=not args.non_streaming,
    )
    errors = [sample.error for sample in summary.samples if sample.error]
    fit: FitStatus = "error" if errors else "yes"
    row = ResultRow(
        model=args.model,
        revision=args.revision or _optional_string(defaults["revision"]),
        runtime=args.runtime or str(defaults["runtime"]),
        env=args.env,
        profile=args.profile or str(defaults["profile"]),
        quantization=args.quantization or _optional_string(defaults["quantization"]),
        fit=fit,
        max_model_len=args.max_model_len or _optional_int(defaults["max_model_len"]),
        tok_s=summary.median_tok_s,
        ttft_ms=summary.median_ttft_ms,
        mm_preprocess_ms=args.mm_preprocess_ms,
        notes="; ".join(errors),
    )
    if args.append_results:
        append_result(args.results, row)
    sys.stdout.write(json.dumps(row.to_csv_record(), ensure_ascii=False) + "\n")
    return 0 if not errors else 1


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
