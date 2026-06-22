"""Runnable demo: an agent that can do arithmetic and look up canned facts.

Run with `ANTHROPIC_API_KEY` set:

    python examples/research_agent.py "What is 17 * 4, and what's the capital of Peru?"
"""

from __future__ import annotations

import ast
import logging
import operator
import sys

from loop_engineering import Loop, Tool, ToolRegistry
from loop_engineering.core.providers import AnthropicProvider

FACTS = {
    "capital of peru": "Lima",
    "capital of japan": "Tokyo",
    "tallest mountain": "Mount Everest",
}

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"unsupported expression element: {ast.dump(node)}")


def calculator(expression: str) -> float:
    """Evaluate a simple arithmetic expression, e.g. '17 * 4', without using `eval`."""
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def fake_search(query: str) -> str:
    """Look up a canned fact by keyword - stands in for a real search/RAG tool."""
    match = FACTS.get(query.strip().lower())
    return match or f"No canned fact found for '{query}'."


def build_loop() -> Loop:
    tools = ToolRegistry(
        [
            Tool(
                name="calculator",
                description="Evaluate an arithmetic expression and return the numeric result.",
                input_schema={
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
                handler=calculator,
            ),
            Tool(
                name="fake_search",
                description="Look up a short factual answer for a query from a canned dataset.",
                input_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
                handler=fake_search,
            ),
        ]
    )
    provider = AnthropicProvider()
    return Loop(
        provider=provider,
        tools=tools,
        system_prompt=(
            "You are a research assistant. Use the calculator and fake_search "
            "tools when they help answer the question. Answer concisely."
        ),
        max_iterations=6,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    question = " ".join(sys.argv[1:]) or "What is 17 * 4, and what's the capital of Peru?"
    loop = build_loop()
    state = loop.run(question)
    print("\n--- final answer ---")
    print(state.final_answer)


if __name__ == "__main__":
    main()
