from __future__ import annotations

import pytest

from loop_engineering.core.exceptions import ToolExecutionError
from loop_engineering.core.tools import Tool, ToolRegistry


def make_tool(name: str, handler) -> Tool:
    return Tool(
        name=name,
        description=f"{name} tool",
        input_schema={"type": "object", "properties": {}},
        handler=handler,
    )


def test_register_and_get_round_trip():
    tool = make_tool("echo", lambda value: value)
    registry = ToolRegistry([tool])

    assert registry.get("echo") is tool
    assert "echo" in registry


def test_dispatch_calls_handler_with_keyword_arguments():
    registry = ToolRegistry([make_tool("add", lambda a, b: a + b)])

    result = registry.dispatch("add", {"a": 2, "b": 3})

    assert result == 5


def test_dispatch_unknown_tool_raises_tool_execution_error():
    registry = ToolRegistry()

    with pytest.raises(ToolExecutionError):
        registry.dispatch("missing", {})


def test_dispatch_wraps_handler_exception():
    def handler() -> None:
        raise RuntimeError("nope")

    registry = ToolRegistry([make_tool("fails", handler)])

    with pytest.raises(ToolExecutionError) as exc_info:
        registry.dispatch("fails", {})

    assert exc_info.value.tool_name == "fails"
    assert isinstance(exc_info.value.original, RuntimeError)


def test_to_anthropic_tools_shape():
    registry = ToolRegistry([make_tool("ping", lambda: "pong")])

    [spec] = registry.to_anthropic_tools()

    assert spec == {
        "name": "ping",
        "description": "ping tool",
        "input_schema": {"type": "object", "properties": {}},
    }
