"""Provider-agnostic interface the loop talks to."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from loop_engineering.core.state import Message


@dataclass
class ToolCall:
    """A single tool invocation requested by the model."""

    id: str
    name: str
    input: dict[str, Any]


@dataclass
class ProviderResponse:
    """Normalized result of one `LLMProvider.complete` call.

    `content_blocks` is kept verbatim so it can be appended back into the
    message history as the assistant turn, exactly as the provider returned it.
    """

    content_blocks: list[dict[str, Any]]
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMProvider(Protocol):
    """Anything that can turn a conversation + tool definitions into a response.

    Implement this to plug in a different model or vendor without touching `Loop`.
    """

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
        system: str | None = None,
    ) -> ProviderResponse: ...
