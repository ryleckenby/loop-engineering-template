# loop-engineering

[![CI](https://github.com/ryleckenby/loop-engineering-template/actions/workflows/ci.yml/badge.svg)](https://github.com/ryleckenby/loop-engineering-template/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A small, opinionated, reusable implementation of the **agentic loop**
pattern — think → act → observe, repeated until the model produces an
answer worth keeping — built on the Claude API. Use this repo as a
GitHub template to start new agent projects without re-deriving the same
plumbing every time.

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

## Why this exists

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

A fuller runnable example lives in [`examples/research_agent.py`](examples/research_agent.py).

## Using this as a template

Click **"Use this template"** on GitHub, or:

```bash
gh repo create my-new-agent --template ryleckenby/loop-engineering-template --public
```

Then rename the `loop_engineering` package, swap in your own tools, and go.

## Docs

- [Concepts (start here if you're new)](docs/concepts.md)
- [Example use cases](docs/examples.md)
- [Architecture](docs/architecture.md)
- [Getting started](docs/getting_started.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
