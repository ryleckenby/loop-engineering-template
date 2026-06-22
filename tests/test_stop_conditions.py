from __future__ import annotations

from loop_engineering.core.state import LoopState
from loop_engineering.core.stop_conditions import all_of, always, any_of, goal_reached


def test_always_accepts_any_state():
    assert always()(LoopState()) is True


def test_goal_reached_wraps_arbitrary_predicate():
    condition = goal_reached(lambda state: state.scratchpad.get("done") is True)

    assert condition(LoopState()) is False
    assert condition(LoopState(scratchpad={"done": True})) is True


def test_any_of_is_true_if_one_condition_passes():
    condition = any_of(lambda _: False, lambda _: True)

    assert condition(LoopState()) is True


def test_all_of_requires_every_condition():
    condition = all_of(lambda _: True, lambda _: False)

    assert condition(LoopState()) is False
