# loop-engineering

[![CI](https://github.com/ryleckenby/loop-engineering-template/actions/workflows/ci.yml/badge.svg)](https://github.com/ryleckenby/loop-engineering-template/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A template for **loop engineering**: building agents that run on their own — triggered by a
schedule or an event, doing work, and remembering what they learned for next time — instead of
being prompted task-by-task. It combines two layers:

- **Orchestration** (`knowledge/`, `CLAUDE.md`, `.claude/skills/`) — a markdown knowledge base
  loops read and write between runs, plus Claude Code skills to scaffold a new loop
  (`new-loop`) and ship a verified code change (`ship-loop-change`).
- **Execution** (`src/loop_engineering/`) — a small, swappable implementation of the **agentic
  loop** pattern (think → act → observe) for the steps that need a model to autonomously call
  tools, built on the Claude API.

```
   think (provider.complete) ──tool calls──▶ act (dispatch tools)
        ▲                                          │
        │                                  observe (tool results)
        │                                          │
        └──────────────────────────────────────────┘
                         no tool calls
                              │
                    stop_condition satisfied?
                         │           │
                        yes          no (nudge, loop again)
                         ▼
                  return final answer
```

Read [`docs/loop-engineer-pattern.md`](docs/loop-engineer-pattern.md) first — it explains how the
two layers fit together and when a loop needs the execution engine vs. a plain Claude Code skill.

## The execution layer

Most agent demos hardcode a `while True` loop directly against one model's
SDK. This repo pulls that loop apart into small, swappable pieces so you can
reason about (and test) each one independently:

- **`Loop`** — orchestrates the cycle and enforces an iteration cap.
- **`LLMProvider`** — a `Protocol`, so the model backend is swappable without touching `Loop`. Only `AnthropicProvider` (Claude) is implemented here.
- **`Tool` / `ToolRegistry`** — declare tools as JSON schema + a Python handler; dispatch and error-handling are generic.
- **`StopCondition`** — a plain `Callable[[LoopState], bool]`; compose with `any_of` / `all_of` instead of writing bespoke control flow per agent.

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown, or
[`docs/concepts.md`](docs/concepts.md) if you're new to agentic loops and want
a slower, beginner-level walkthrough of what happens on each iteration.

## Quickstart

```bash
pip install -e ".[dev]"
pytest   # runs offline against a scripted FakeProvider, no API key needed
```

```python
from loop_engineering import Loop, Tool, ToolRegistry
from loop_engineering.core.providers import AnthropicProvider

def get_weather(city: str) -> str:
    return f"It's sunny in {city}."

tools = ToolRegistry([
    Tool(
        name="get_weather",
        description="Get the current weather for a city.",
        input_schema={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
        handler=get_weather,
    ),
])

loop = Loop(provider=AnthropicProvider(), tools=tools, max_iterations=5)
state = loop.run("What's the weather in Lima?")
print(state.final_answer)
```

A fuller runnable example lives in [`examples/research_agent.py`](examples/research_agent.py), and
[`scripts/task_refinement_loop.py`](scripts/task_refinement_loop.py) shows the execution engine
being called from inside an orchestration-layer loop (see the `task-refinement` domain below).

## The orchestration layer

```
knowledge/
  README.md            schema: artifact kinds (signal, note), domains as loops, the Timeline convention
  signals/              evidence/feedback, frequency-counted
  notes/                 durable knowledge and decisions
  domains/
    task-refinement/    EXAMPLE: a scheduled loop that needs the execution engine
    dev-trigger/        EXAMPLE: an event-driven loop that doesn't
CLAUDE.md               template every session reads — fill in the {{PLACEHOLDER}}s for your project
LOG.md                  global one-line-per-run activity feed
.claude/skills/
  new-loop/             scaffold a new knowledge/domains/<name>/README.md
  ship-loop-change/     verify (test/lint), then commit + PR — never ship unverified
```

Copy either example domain as a starting point, or run the `new-loop` skill to scaffold a blank
one. Triggers (cron/webhook) aren't reimplemented here — wire a domain's cadence to Claude Code's
own `/schedule` or `/loop` skill; see [`docs/loop-engineer-pattern.md`](docs/loop-engineer-pattern.md).

## Using this as a template

Click **"Use this template"** on GitHub, or:

```bash
gh repo create my-new-agent --template ryleckenby/loop-engineering-template --public
```

Then rename the `loop_engineering` package, swap in your own tools, and go.

## Docs

- [The loop engineer pattern (start here)](docs/loop-engineer-pattern.md) — how orchestration and execution fit together
- [Concepts](docs/concepts.md) — the execution engine, beginner-level walkthrough
- [Example use cases](docs/examples.md)
- [Architecture](docs/architecture.md)
- [Getting started](docs/getting_started.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
