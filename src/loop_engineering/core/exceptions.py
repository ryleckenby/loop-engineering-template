"""Exceptions raised by the agentic loop."""

from __future__ import annotations


class LoopError(Exception):
    """Base class for all loop-related errors."""


class MaxIterationsExceeded(LoopError):
    """Raised when the loop runs out of iterations without reaching a stop condition."""


class ToolExecutionError(LoopError):
    """Raised when a tool handler raises during dispatch."""

    def __init__(self, tool_name: str, original: Exception) -> None:
        super().__init__(f"Tool '{tool_name}' raised {original.__class__.__name__}: {original}")
        self.tool_name = tool_name
        self.original = original


class ProviderError(LoopError):
    """Raised when an LLM provider call fails."""
