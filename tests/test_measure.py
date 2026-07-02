from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from harness.common.measure import ChatPrompt, measure_chat_completion


def test_chat_prompt_payload_includes_stop_when_set() -> None:
    prompt = ChatPrompt(
        model="fake",
        messages=[{"role": "user", "content": "hi"}],
        stop=["<|end|>"],
    )

    assert prompt.payload(stream=True)["stop"] == ["<|end|>"]


class FakeClient:
    def stream_chat_completion(self, _payload: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
        yield {"choices": [{"delta": {"content": "hello"}}]}
        yield {"choices": [{"delta": {"content": " world"}}], "usage": {"completion_tokens": 2, "prompt_tokens": 3}}

    def chat_completion(self, _payload: Mapping[str, Any]) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "hello world"}}], "usage": {"completion_tokens": 2}}


def test_measure_streaming_completion_uses_usage_tokens() -> None:
    timed = measure_chat_completion(
        FakeClient(),  # type: ignore[arg-type]
        ChatPrompt(model="fake", messages=[{"role": "user", "content": "hi"}]),
    )

    assert timed.content == "hello world"
    assert timed.completion_tokens == 2
    assert timed.tok_s is not None
