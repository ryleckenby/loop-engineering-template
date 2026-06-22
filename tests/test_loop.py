from __future__ import annotations

import pytest

from loop_engineering.core.exceptions import MaxIterationsExceeded
from loop_engineering.core.loop import Loop
from loop_engineering.core.tools import Tool, ToolRegistry
from tests.fakes import FakeProvider, text_response, tool_call_response


def test_returns_final_answer_when_model_calls_no_tools():
    provider = FakeProvider([text_response("hello there")])
    loop = Loop(provider=provider)

    state = loop.run("hi")

    assert state.done is True
    assert state.final_answer == "hello there"


def test_dispatches_tool_call_then_returns_final_answer():
    provider = FakeProvider(
        [
            tool_call_response("add", {"a": 1, "b": 2}, call_id="call_1"),
            text_response("3"),
        ]
    )
    tools = ToolRegistry(
        [
            Tool(
                name="add",
                description="add two numbers",
                input_schema={"type": "object", "properties": {}},
                handler=lambda a, b: a + b,
            )
        ]
    )
    loop = Loop(provider=provider, tools=tools)

    state = loop.run("what is 1 + 2?")

    assert state.final_answer == "3"
    tool_result_message = state.messages[2]
    assert tool_result_message["role"] == "user"
    assert tool_result_message["content"][0]["content"] == "3"
    assert tool_result_message["content"][0]["is_error"] is False


def test_tool_handler_exception_is_reported_as_error_observation_and_loop_continues():
    def boom(**_: object) -> None:
        raise ValueError("kaboom")

    provider = FakeProvider(
        [
            tool_call_response("boom", {}, call_id="call_1"),
            text_response("done"),
        ]
    )
    tools = ToolRegistry(
        [
            Tool(
                name="boom",
                description="always fails",
                input_schema={"type": "object", "properties": {}},
                handler=boom,
            )
        ]
    )
    loop = Loop(provider=provider, tools=tools)

    state = loop.run("trigger the bug")

    tool_result = state.messages[2]["content"][0]
    assert tool_result["is_error"] is True
    assert "kaboom" in tool_result["content"]
    assert state.final_answer == "done"


def test_raises_max_iterations_exceeded_when_stop_condition_never_satisfied():
    provider = FakeProvider([text_response("not yet"), text_response("still not yet")])
    loop = Loop(provider=provider, stop_condition=lambda state: False, max_iterations=2)

    with pytest.raises(MaxIterationsExceeded):
        loop.run("keep trying")
