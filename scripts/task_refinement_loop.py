"""Example: the task-refinement domain's automation, backed by the Python execution engine.

This is the concrete tie-in described in `knowledge/domains/task-refinement/README.md` and
`docs/loop-engineer-pattern.md`: a scheduled loop (wired via Claude Code's `/schedule` or `/loop`
skill — not implemented here) whose actual work is multi-step and tool-using, so it's built on
`Loop`/`Tool`/`ToolRegistry` instead of being a plain Claude Code instruction.

Uses an in-memory task list instead of a real issue tracker so it's runnable standalone. Swap
`TASKS`/`list_open_tasks`/`refine_task` for real API calls to wire this to GitHub Issues, Linear,
Jira, etc.

Run with `ANTHROPIC_API_KEY` set:

    python scripts/task_refinement_loop.py
"""

from __future__ import annotations

import logging

from loop_engineering import Loop, Tool, ToolRegistry
from loop_engineering.core.providers import AnthropicProvider

TASKS = [
    {
        "id": "TASK-1",
        "title": "Add CSV export to the reports page",
        "description": "Users want to export report data.",
        "acceptance_criteria": None,
    },
    {
        "id": "TASK-2",
        "title": "Fix flaky login test",
        "description": "test_login_redirect intermittently fails in CI.",
        "acceptance_criteria": "test_login_redirect passes 20/20 consecutive CI runs.",
    },
]


def list_open_tasks() -> str:
    """List tasks that are missing acceptance criteria and need refinement."""
    needs_refinement = [t for t in TASKS if not t["acceptance_criteria"]]
    if not needs_refinement:
        return "No tasks need refinement."
    return "\n".join(f"{t['id']}: {t['title']} — {t['description']}" for t in needs_refinement)


def refine_task(task_id: str, acceptance_criteria: str) -> str:
    """Set acceptance criteria on a task by ID."""
    for task in TASKS:
        if task["id"] == task_id:
            task["acceptance_criteria"] = acceptance_criteria
            return f"Updated {task_id} with acceptance criteria."
    return f"No such task: {task_id}"


def build_loop() -> Loop:
    tools = ToolRegistry(
        [
            Tool(
                name="list_open_tasks",
                description="List tasks that are missing acceptance criteria.",
                input_schema={"type": "object", "properties": {}},
                handler=list_open_tasks,
            ),
            Tool(
                name="refine_task",
                description="Set acceptance criteria on a task, identified by its ID.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "acceptance_criteria": {"type": "string"},
                    },
                    "required": ["task_id", "acceptance_criteria"],
                },
                handler=refine_task,
            ),
        ]
    )
    return Loop(
        provider=AnthropicProvider(),
        tools=tools,
        system_prompt=(
            "You refine engineering tasks before they're picked up for implementation. "
            "List tasks needing refinement, write clear, testable acceptance criteria for each "
            "one based on its title and description, and call refine_task to save them."
        ),
        max_iterations=8,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    loop = build_loop()
    state = loop.run("Review the backlog and refine any task missing acceptance criteria.")
    print("\n--- final answer ---")
    print(state.final_answer)
    print("\n--- task state ---")
    for task in TASKS:
        print(task)


if __name__ == "__main__":
    main()
