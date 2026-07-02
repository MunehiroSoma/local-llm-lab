"""Marker-based scoring helpers for lightweight VLM task checks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

MarkerGroup = str | Sequence[str]


@dataclass(frozen=True)
class MarkerScore:
    """A marker scoring result."""

    matched: tuple[str, ...]
    missing: tuple[tuple[str, ...], ...]
    ratio: float
    passed: bool


def score_markers(output: str, marker_groups: Sequence[MarkerGroup], *, threshold: float = 1.0) -> MarkerScore:
    """Score output by requiring one matched alias from each marker group."""
    normalized_output = _normalize(output)
    matched: list[str] = []
    missing: list[tuple[str, ...]] = []
    groups = tuple(_as_group(group) for group in marker_groups)
    for group in groups:
        found = next((marker for marker in group if _normalize(marker) in normalized_output), None)
        if found is None:
            missing.append(group)
        else:
            matched.append(found)
    ratio = len(matched) / len(groups) if groups else 1.0
    return MarkerScore(
        matched=tuple(matched),
        missing=tuple(missing),
        ratio=ratio,
        passed=ratio >= threshold,
    )


def _as_group(group: MarkerGroup) -> tuple[str, ...]:
    if isinstance(group, str):
        return (group,)
    return tuple(group)


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())
