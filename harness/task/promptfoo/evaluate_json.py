"""Validate summarize/tag JSON outputs before promptfoo rubric scoring."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def score_summary_tags(output: str) -> float:
    """Return a schema-adherence score for a summarize/tag JSON output."""
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return 0.0
    if not isinstance(data, dict):
        return 0.0
    summary = data.get("summary")
    tags = data.get("tags")
    if not isinstance(summary, str) or not summary.strip():
        return 0.0
    if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag.strip() for tag in tags):
        return 0.0
    return 1.0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for schema-only promptfoo output scoring."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--output-file", type=Path)
    args = parser.parse_args(argv)
    output = args.output if args.output is not None else args.output_file.read_text(encoding="utf-8")
    score = score_summary_tags(output)
    sys.stdout.write(json.dumps({"score": score}, ensure_ascii=False) + "\n")
    return 0 if score > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
