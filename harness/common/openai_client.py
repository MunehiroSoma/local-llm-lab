"""Small OpenAI-compatible HTTP client used by harness layers."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, cast


class OpenAICompatError(RuntimeError):
    """Raised when an OpenAI-compatible endpoint returns an error."""


@dataclass(frozen=True)
class OpenAICompatClient:
    """Minimal client for ``/v1/chat/completions`` endpoints."""

    base_url: str
    api_key: str | None = None
    timeout_s: float = 120.0

    def chat_completion(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Send a non-streaming chat completion request."""
        request = self._request(payload)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:  # noqa: S310
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise OpenAICompatError(_http_error_message(exc)) from exc
        except urllib.error.URLError as exc:
            raise OpenAICompatError(str(exc.reason)) from exc
        data = json.loads(body)
        if not isinstance(data, dict):
            raise OpenAICompatError("chat completion response must be a JSON object")
        return cast(dict[str, Any], data)

    def stream_chat_completion(self, payload: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
        """Yield streaming chat completion JSON chunks from server-sent events."""
        request = self._request({**payload, "stream": True, "stream_options": {"include_usage": True}})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:  # noqa: S310
                while True:
                    raw_line = response.readline()
                    if not raw_line:
                        break
                    line = raw_line.decode("utf-8").strip()
                    if not line.startswith("data:"):
                        continue
                    data_text = line.removeprefix("data:").strip()
                    if data_text == "[DONE]":
                        break
                    parsed = json.loads(data_text)
                    if isinstance(parsed, dict):
                        yield cast(dict[str, Any], parsed)
        except urllib.error.HTTPError as exc:
            raise OpenAICompatError(_http_error_message(exc)) from exc
        except urllib.error.URLError as exc:
            raise OpenAICompatError(str(exc.reason)) from exc

    def _request(self, payload: Mapping[str, Any]) -> urllib.request.Request:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return urllib.request.Request(_chat_completions_url(self.base_url), data=body, headers=headers, method="POST")  # noqa: S310


def _chat_completions_url(base_url: str) -> str:
    cleaned = base_url.rstrip("/")
    parsed = urllib.parse.urlparse(cleaned)
    if parsed.scheme not in {"http", "https"}:
        raise OpenAICompatError(f"unsupported URL scheme: {parsed.scheme}")
    if cleaned.endswith("/chat/completions"):
        return cleaned
    if cleaned.endswith("/v1"):
        return f"{cleaned}/chat/completions"
    return f"{cleaned}/v1/chat/completions"


def _http_error_message(exc: urllib.error.HTTPError) -> str:
    body = exc.read().decode("utf-8", errors="replace")
    return f"HTTP {exc.code}: {body}"
