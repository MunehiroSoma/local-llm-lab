#!/usr/bin/env python3
"""Keep Codex and Claude Code skill directories in copy-sync."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_SKILLS = REPO_ROOT / ".agents" / "skills"
CLAUDE_SKILLS = REPO_ROOT / ".claude" / "skills"


def iter_files(root: Path) -> set[Path]:
    """Return relative file paths under root."""
    if not root.exists():
        return set()
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}


def validate_skill_root(root: Path) -> list[str]:
    """Return validation errors for a skills root."""
    errors: list[str] = []
    if not root.is_dir():
        return [f"{root.relative_to(REPO_ROOT)} does not exist"]

    for skill_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if not (skill_dir / "SKILL.md").is_file():
            errors.append(f"{skill_dir.relative_to(REPO_ROOT)} has no SKILL.md")
    return errors


def compare_trees(source: Path, target: Path) -> list[str]:
    """Return human-readable copy-sync differences."""
    errors = validate_skill_root(source) + validate_skill_root(target)
    source_files = iter_files(source)
    target_files = iter_files(target)

    for missing in sorted(source_files - target_files):
        errors.append(f"missing from {target.relative_to(REPO_ROOT)}: {missing}")
    for extra in sorted(target_files - source_files):
        errors.append(f"extra in {target.relative_to(REPO_ROOT)}: {extra}")
    for common in sorted(source_files & target_files):
        if not filecmp.cmp(source / common, target / common, shallow=False):
            errors.append(f"content differs: {common}")
    return errors


def sync_tree(source: Path, target: Path) -> None:
    """Replace target with a copy of source."""
    source_errors = validate_skill_root(source)
    if source_errors:
        for error in source_errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="only verify that .agents/skills and .claude/skills are identical",
    )
    parser.add_argument(
        "--source",
        choices=("agents", "claude"),
        default="agents",
        help="copy direction for sync mode; default copies .agents/skills to .claude/skills",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.source == "agents":
        source, target = AGENTS_SKILLS, CLAUDE_SKILLS
    else:
        source, target = CLAUDE_SKILLS, AGENTS_SKILLS

    if args.check:
        errors = compare_trees(AGENTS_SKILLS, CLAUDE_SKILLS)
        if errors:
            print("Skill copies are out of sync:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            print(
                "Run `make sync-skills` after editing .agents/skills.",
                file=sys.stderr,
            )
            return 1
        print("Skill copies are in sync.")
        return 0

    sync_tree(source, target)
    print(f"Copied {source.relative_to(REPO_ROOT)} -> {target.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
