#!/usr/bin/env python3
"""Validate that the current branch follows this repository's naming policy."""

from __future__ import annotations

import os
import re
import subprocess
import sys

ALLOWED_BRANCHES = {"main"}
ALLOWED_PATTERNS = (
    re.compile(r"^(feat|fix|exp|env|docs|chore)/[a-z0-9][a-z0-9-]*$"),
    re.compile(r"^model/[a-z0-9][a-z0-9-]*$"),
)


def current_branch() -> str:
    env_branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if env_branch:
        return env_branch

    result = subprocess.run(  # noqa: S603 - static read-only git invocation.
        ["/usr/bin/git", "branch", "--show-current"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def is_valid_branch(branch: str) -> bool:
    if not branch:
        return True
    if branch in ALLOWED_BRANCHES:
        return True
    return any(pattern.fullmatch(branch) for pattern in ALLOWED_PATTERNS)


def main() -> int:
    branch = current_branch()
    if is_valid_branch(branch):
        return 0

    print("Invalid branch name:", branch, file=sys.stderr)
    print(
        "Use docs/conventions.md prefixes: feat/, fix/, exp/, model/, env/, docs/, chore/.",
        file=sys.stderr,
    )
    print(
        "Do not use tool-origin prefixes such as codex/ or claude/.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
