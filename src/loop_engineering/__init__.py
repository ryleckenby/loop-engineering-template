"""loop-engineering: a small, reusable implementation of the agentic loop pattern."""

from loop_engineering.core import (
    Loop,
    LoopState,
    Tool,
    ToolRegistry,
)
from loop_engineering.core.providers import AnthropicProvider

__version__ = "0.1.0"

__all__ = [
    "Loop",
    "LoopState",
    "Tool",
    "ToolRegistry",
    "AnthropicProvider",
    "__version__",
]
