"""Test doubles for exercising the loop without a real LLM provider."""

from __future__ import annotations

from typing import Any

from loop_engineering.core.providers.base import ProviderResponse, ToolCall
from loop_engineering.core.state import Message


class FakeProvider:
    """Returns a pre-scripted sequence of responses, one per `complete` call."""

    def __init__(self, responses: list[ProviderResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
        system: str | None = None,
    ) -> ProviderResponse:
        self.calls.append({"messages": messages, "tools": tools, "system": system})
        if not self._responses:
            raise AssertionError("FakeProvider ran out of scripted responses")
        return self._responses.pop(0)


def text_response(text: str) -> ProviderResponse:
    return ProviderResponse(
        content_blocks=[{"type": "text", "text": text}], text=text, tool_calls=[]
    )


def tool_call_response(
    name: str, input: dict[str, Any], call_id: str = "call_1"
) -> ProviderResponse:
    return ProviderResponse(
        content_blocks=[{"type": "tool_use", "id": call_id, "name": name, "input": input}],
        text=None,
        tool_calls=[ToolCall(id=call_id, name=name, input=input)],
    )
