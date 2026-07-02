"""Timing helpers for single-request OpenAI-compatible benchmarks."""

from __future__ import annotations

import statistics
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from harness.common.openai_client import OpenAICompatClient, OpenAICompatError

MS_PER_SECOND = 1000.0
MIN_DECODE_SECONDS = 1.0e-9


@dataclass(frozen=True)
class ChatPrompt:
    """A chat prompt and generation parameters for one benchmark request."""

    model: str
    messages: Sequence[Mapping[str, Any]]
    max_tokens: int = 256
    temperature: float = 0.0
    stop: Sequence[str] | None = None

    def payload(self, *, stream: bool) -> dict[str, Any]:
        """Build an OpenAI-compatible chat completion payload."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": list(self.messages),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": stream,
        }
        if self.stop is not None:
            payload["stop"] = list(self.stop)
        return payload


@dataclass(frozen=True)
class TimedCompletion:
    """Timing data from a single chat completion."""

    content: str
    total_ms: float
    ttft_ms: float | None
    completion_tokens: int | None
    prompt_tokens: int | None
    tok_s: float | None
    error: str | None = None


@dataclass(frozen=True)
class BenchmarkSummary:
    """Median summary for repeated single-request measurements."""

    samples: tuple[TimedCompletion, ...]
    median_total_ms: float
    median_ttft_ms: float | None
    median_tok_s: float | None


def measure_chat_completion(
    client: OpenAICompatClient,
    prompt: ChatPrompt,
    *,
    stream: bool = True,
) -> TimedCompletion:
    """Measure one OpenAI-compatible chat completion."""
    return _measure_streaming(client, prompt) if stream else _measure_non_streaming(client, prompt)


def benchmark_chat_completion(
    client: OpenAICompatClient,
    prompt: ChatPrompt,
    *,
    repeats: int = 3,
    warmups: int = 1,
    stream: bool = True,
) -> BenchmarkSummary:
    """Run warmups and return median timing for repeated requests."""
    for _ in range(warmups):
        measure_chat_completion(client, prompt, stream=stream)
    samples = tuple(measure_chat_completion(client, prompt, stream=stream) for _ in range(repeats))
    return BenchmarkSummary(
        samples=samples,
        median_total_ms=statistics.median(sample.total_ms for sample in samples),
        median_ttft_ms=_median_optional(sample.ttft_ms for sample in samples),
        median_tok_s=_median_optional(sample.tok_s for sample in samples),
    )


def _measure_streaming(client: OpenAICompatClient, prompt: ChatPrompt) -> TimedCompletion:
    started = time.perf_counter()
    first_token_at: float | None = None
    chunks: list[str] = []
    usage: Mapping[str, Any] = {}
    try:
        for chunk in client.stream_chat_completion(prompt.payload(stream=True)):
            delta = _extract_content_delta(chunk)
            if delta and first_token_at is None:
                first_token_at = time.perf_counter()
            chunks.append(delta)
            chunk_usage = chunk.get("usage")
            if isinstance(chunk_usage, dict):
                usage = chunk_usage
    except OpenAICompatError as exc:
        ended = time.perf_counter()
        return TimedCompletion(
            content="",
            total_ms=(ended - started) * MS_PER_SECOND,
            ttft_ms=None,
            completion_tokens=None,
            prompt_tokens=None,
            tok_s=None,
            error=str(exc),
        )
    ended = time.perf_counter()
    content = "".join(chunks)
    total_ms = (ended - started) * MS_PER_SECOND
    ttft_ms = (first_token_at - started) * MS_PER_SECOND if first_token_at is not None else None
    completion_tokens = _optional_int(usage.get("completion_tokens")) or _estimate_tokens(content)
    prompt_tokens = _optional_int(usage.get("prompt_tokens"))
    return TimedCompletion(
        content=content,
        total_ms=total_ms,
        ttft_ms=ttft_ms,
        completion_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
        tok_s=_tokens_per_second(completion_tokens, total_ms, ttft_ms),
    )


def _measure_non_streaming(client: OpenAICompatClient, prompt: ChatPrompt) -> TimedCompletion:
    started = time.perf_counter()
    try:
        response = client.chat_completion(prompt.payload(stream=False))
    except OpenAICompatError as exc:
        ended = time.perf_counter()
        return TimedCompletion(
            content="",
            total_ms=(ended - started) * MS_PER_SECOND,
            ttft_ms=None,
            completion_tokens=None,
            prompt_tokens=None,
            tok_s=None,
            error=str(exc),
        )
    ended = time.perf_counter()
    content = _extract_message_content(response)
    usage = response.get("usage")
    usage_map = usage if isinstance(usage, dict) else {}
    completion_tokens = _optional_int(usage_map.get("completion_tokens")) or _estimate_tokens(content)
    total_ms = (ended - started) * MS_PER_SECOND
    return TimedCompletion(
        content=content,
        total_ms=total_ms,
        ttft_ms=None,
        completion_tokens=completion_tokens,
        prompt_tokens=_optional_int(usage_map.get("prompt_tokens")),
        tok_s=_tokens_per_second(completion_tokens, total_ms, None),
    )


def _extract_content_delta(chunk: Mapping[str, Any]) -> str:
    choices = chunk.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    delta = first.get("delta")
    if not isinstance(delta, dict):
        return ""
    content = delta.get("content")
    if isinstance(content, str) and content:
        return content
    reasoning = delta.get("reasoning")
    return reasoning if isinstance(reasoning, str) else ""


def _extract_message_content(response: Mapping[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str) and content:
        return content
    reasoning = message.get("reasoning")
    return reasoning if isinstance(reasoning, str) else ""


def _tokens_per_second(completion_tokens: int | None, total_ms: float, ttft_ms: float | None) -> float | None:
    if completion_tokens is None:
        return None
    decode_ms = total_ms - ttft_ms if ttft_ms is not None else total_ms
    return completion_tokens / max(decode_ms / MS_PER_SECOND, MIN_DECODE_SECONDS)


def _estimate_tokens(content: str) -> int | None:
    if not content:
        return None
    return max(1, len(content.split()))


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return int(str(value))


def _median_optional(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.median(present) if present else None
