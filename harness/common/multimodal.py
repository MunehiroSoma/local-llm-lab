"""Helpers for OpenAI-compatible multimodal chat payloads."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any


def build_user_content(
    prompt: str, *, image: Path | None = None, image_detail: str | None = None
) -> str | list[dict[str, Any]]:
    """Build a text-only or image+text OpenAI-compatible user message content."""
    if image is None:
        return prompt

    image_url: dict[str, Any] = {"url": image_data_url(image)}
    if image_detail is not None:
        image_url["detail"] = image_detail
    return [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": image_url},
    ]


def image_data_url(path: Path) -> str:
    """Encode an image file as a data URL for OpenAI-compatible chat APIs."""
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
