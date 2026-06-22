# Getting started

## Install

```bash
pip install -e ".[dev]"
```

## Run the test suite (no API key needed)

```bash
pytest
```

The suite exercises `Loop` against `tests/fakes.py::FakeProvider`, a
scripted stand-in for the Claude API, so it runs offline and in CI without
secrets.

## Run the example agent (needs a real API key)

```bash
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
export $(grep -v '^#' .env | xargs)   # or use your shell/dotenv tool of choice
python examples/research_agent.py "What is 17 * 4, and what's the capital of Peru?"
```

You'll see structured log lines for each iteration (`thought`, `action`,
`observation`) followed by the final answer.

## Build your own agent

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

loop = Loop(
    provider=AnthropicProvider(),
    tools=tools,
    system_prompt="You are a helpful weather assistant.",
    max_iterations=5,
)

state = loop.run("What's the weather in Lima?")
print(state.final_answer)
```

## Extending

- **New tool**: write a Python function, describe its arguments as a JSON
  schema, wrap both in a `Tool`, and pass it to `ToolRegistry`.
- **New stop condition**: write a `Callable[[LoopState], bool]` — see
  `core/stop_conditions.py` for `goal_reached`, `any_of`, `all_of`.
- **New provider**: implement `LLMProvider.complete(...)` against another
  model's API and pass an instance into `Loop(provider=...)`. Nothing else
  changes.
