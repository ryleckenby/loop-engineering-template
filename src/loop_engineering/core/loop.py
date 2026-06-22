"""The core agentic loop: think -> act -> observe, repeated until the answer sticks."""

from __future__ import annotations

import logging
from typing import Any

from loop_engineering.core.exceptions import MaxIterationsExceeded, ToolExecutionError
from loop_engineering.core.providers.base import LLMProvider, ToolCall
from loop_engineering.core.state import LoopState
from loop_engineering.core.stop_conditions import StopCondition, always
from loop_engineering.core.tools import ToolRegistry

logger = logging.getLogger(__name__)


class Loop:
    """Drives one agent conversation through repeated think/act/observe cycles.

    Each iteration: the provider produces a response (a "thought" and,
    optionally, tool calls). Tool calls are dispatched ("act") and their
    results fed back in ("observe"). Once the model answers without calling
    a tool, `stop_condition` decides whether that answer is accepted.
    """

    def __init__(
        self,
        provider: LLMProvider,
        tools: ToolRegistry | None = None,
        system_prompt: str | None = None,
        stop_condition: StopCondition | None = None,
        max_iterations: int = 10,
    ) -> None:
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.system_prompt = system_prompt
        self.stop_condition = stop_condition or always()
        self.max_iterations = max_iterations

    def run(self, user_input: str, state: LoopState | None = None) -> LoopState:
        """Run the loop to completion and return the final `LoopState`.

        Raises `MaxIterationsExceeded` if no accepted answer is reached in
        `max_iterations` cycles. On success, `state.final_answer` holds the
        model's answer and `state.done` is `True`.
        """
        state = state or LoopState()
        state.add_user_message(user_input)

        while True:
            if state.iteration >= self.max_iterations:
                raise MaxIterationsExceeded(
                    f"loop exceeded {self.max_iterations} iterations without a final answer"
                )
            state.iteration += 1

            response = self.provider.complete(
                messages=state.messages,
                tools=self.tools.to_anthropic_tools(),
                system=self.system_prompt,
            )
            state.add_assistant_message(response.content_blocks)
            logger.info(
                "iteration=%d thought=%r tool_calls=%s",
                state.iteration,
                response.text,
                [call.name for call in response.tool_calls],
            )

            if response.has_tool_calls:
                tool_results = [self._execute_tool_call(call) for call in response.tool_calls]
                state.add_user_message(tool_results)
                continue

            if self.stop_condition(state):
                state.mark_done(response.text or "")
                return state

            # The model stopped calling tools but the answer wasn't accepted
            # yet (e.g. it failed a goal check) - nudge it instead of silently
            # spinning forever on the same unaccepted answer.
            state.add_user_message("Continue working towards the goal.")

    def _execute_tool_call(self, tool_call: ToolCall) -> dict[str, Any]:
        logger.info("action=%s input=%r", tool_call.name, tool_call.input)
        try:
            result = self.tools.dispatch(tool_call.name, tool_call.input)
            content, is_error = str(result), False
        except ToolExecutionError as exc:
            content, is_error = str(exc), True
        logger.info("observation=%r is_error=%s", content, is_error)
        return {
            "type": "tool_result",
            "tool_use_id": tool_call.id,
            "content": content,
            "is_error": is_error,
        }
