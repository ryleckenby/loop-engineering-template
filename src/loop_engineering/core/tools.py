"""Tool definitions and dispatch for the agentic loop."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from loop_engineering.core.exceptions import ToolExecutionError


@dataclass(frozen=True)
class Tool:
    """A function the model can call, described as JSON schema plus a handler.

    `input_schema` follows the JSON Schema subset used by the Anthropic
    Messages API `tools` parameter (an object schema with `properties`).
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]

    def to_anthropic_tool(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    """Holds the set of tools available to a `Loop` and dispatches calls to them."""

    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError:
            raise ToolExecutionError(name, KeyError(f"no tool registered as '{name}'")) from None

    def dispatch(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self.get(name)
        try:
            return tool.handler(**arguments)
        except Exception as exc:  # noqa: BLE001 - surfaced to the model as an observation
            raise ToolExecutionError(name, exc) from exc

    def to_anthropic_tools(self) -> list[dict[str, Any]]:
        return [tool.to_anthropic_tool() for tool in self._tools.values()]

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __iter__(self):
        return iter(self._tools.values())
