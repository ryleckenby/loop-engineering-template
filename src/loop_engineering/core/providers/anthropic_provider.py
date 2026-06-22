"""LLMProvider implementation backed by the Claude API."""

from __future__ import annotations

import os
from typing import Any

import anthropic

from loop_engineering.core.exceptions import ProviderError
from loop_engineering.core.providers.base import ProviderResponse, ToolCall
from loop_engineering.core.state import Message

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096


class AnthropicProvider:
    """Sends the loop's conversation to Claude via the `anthropic` SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: anthropic.Anthropic | None = None,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = client or anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
        system: str | None = None,
    ) -> ProviderResponse:
        try:
            # Loop/Tool keep messages and tools as plain dicts so the core package
            # stays provider-agnostic; the SDK's TypedDicts are structurally
            # compatible at runtime but mypy can't see that through `dict[str, Any]`.
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system or anthropic.NOT_GIVEN,  # type: ignore[arg-type]
                messages=messages,  # type: ignore[arg-type]
                tools=tools or anthropic.NOT_GIVEN,  # type: ignore[arg-type]
            )
        except anthropic.APIError as exc:
            raise ProviderError(str(exc)) from exc

        content_blocks = [block.model_dump() for block in response.content]
        text_parts = [block["text"] for block in content_blocks if block["type"] == "text"]
        tool_calls = [
            ToolCall(id=block["id"], name=block["name"], input=block["input"])
            for block in content_blocks
            if block["type"] == "tool_use"
        ]
        return ProviderResponse(
            content_blocks=content_blocks,
            text="\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls,
        )
