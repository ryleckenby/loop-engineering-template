"""Mutable state carried across iterations of an agentic loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Message = dict[str, Any]
"""A single conversation turn, shaped like an Anthropic Messages API entry."""


@dataclass
class LoopState:
    """Everything the loop needs to remember between iterations.

    `scratchpad` is free-form storage tools/stop-conditions can read or write
    (e.g. a running total, a list of visited URLs) without it becoming part
    of the conversation sent back to the model.
    """

    messages: list[Message] = field(default_factory=list)
    scratchpad: dict[str, Any] = field(default_factory=dict)
    iteration: int = 0
    done: bool = False
    final_answer: str | None = None

    def add_message(self, role: str, content: Any) -> None:
        self.messages.append({"role": role, "content": content})

    def add_user_message(self, content: Any) -> None:
        self.add_message("user", content)

    def add_assistant_message(self, content: Any) -> None:
        self.add_message("assistant", content)

    def mark_done(self, final_answer: str) -> None:
        self.done = True
        self.final_answer = final_answer
