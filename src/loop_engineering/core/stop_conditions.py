"""Predicates that decide whether a candidate final answer is acceptable.

A `StopCondition` is checked only once the model has produced a response with
no tool calls. It decides whether that response is good enough to return, or
whether the loop should keep going (e.g. by nudging the model with another
user message). The iteration cap itself lives on `Loop`, not here.
"""

from __future__ import annotations

from collections.abc import Callable

from loop_engineering.core.state import LoopState

StopCondition = Callable[[LoopState], bool]


def always() -> StopCondition:
    """Accept any final answer as soon as the model stops calling tools."""
    return lambda state: True


def goal_reached(predicate: Callable[[LoopState], bool]) -> StopCondition:
    """Wrap an arbitrary predicate over `LoopState` as a stop condition."""
    return predicate


def any_of(*conditions: StopCondition) -> StopCondition:
    return lambda state: any(condition(state) for condition in conditions)


def all_of(*conditions: StopCondition) -> StopCondition:
    return lambda state: all(condition(state) for condition in conditions)
