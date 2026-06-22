# Example use cases

The calculator/fake-search demo in `examples/research_agent.py` is deliberately trivial — it exists to prove the loop wiring works without needing real credentials or external services. Here are more realistic things this template is shaped for. None of these are built — they're sketches showing what `tools`, `system_prompt`, and `stop_condition` you'd plug in.

## 1. Codebase Q&A / code review assistant

**Tools**: `read_file(path)`, `list_files(glob_pattern)`, `grep(pattern)`.

```python
tools = ToolRegistry([
    Tool(name="read_file", description="Read a file's contents by path.",
         input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
         handler=lambda path: open(path).read()),
    Tool(name="list_files", description="List files matching a glob pattern.",
         input_schema={"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]},
         handler=lambda pattern: "\n".join(glob.glob(pattern, recursive=True))),
])

loop = Loop(
    provider=AnthropicProvider(),
    tools=tools,
    system_prompt="You review Python code for bugs. Read the relevant files before commenting.",
    max_iterations=8,
)
state = loop.run("Are there any obvious bugs in src/payments/?")
```

Why a loop and not one call: the model doesn't know which files matter until it starts reading, and a real review needs multiple file reads chained together.

## 2. Customer support ticket triage

**Tools**: `lookup_order(order_id)`, `lookup_customer(email)`, `create_refund(order_id, amount)` (gated — see note below).

```python
def lookup_order(order_id: str) -> str:
    return db.query("SELECT * FROM orders WHERE id = ?", order_id)

tools = ToolRegistry([
    Tool(name="lookup_order", description="Look up an order by ID.", ...),
    Tool(name="lookup_customer", description="Look up a customer by email.", ...),
])

loop = Loop(
    provider=AnthropicProvider(),
    tools=tools,
    system_prompt="You triage support tickets. Look up order/customer details before responding. Never issue refunds — escalate those to a human.",
    max_iterations=5,
)
```

Note the system prompt explicitly tells the model **not** to do the risky action (refunds) — for anything with real side effects, either leave the tool out entirely (as here) or require a human-confirmation step before the handler executes. This codebase doesn't include an approval gate; you'd add one inside the tool's `handler` (e.g. write a pending-approval row and return "awaiting approval" instead of executing immediately).

## 3. Structured data extraction with a quality bar

**Tools**: none necessarily — but a custom `stop_condition` to enforce output quality.

```python
import json
from loop_engineering.core.stop_conditions import goal_reached

def looks_like_valid_json(state) -> bool:
    try:
        json.loads(state.messages[-1]["content"] if isinstance(state.messages[-1]["content"], str) else "")
        return True
    except (json.JSONDecodeError, TypeError):
        return False

loop = Loop(
    provider=AnthropicProvider(),
    system_prompt="Extract the invoice number, total, and due date as JSON. Respond with JSON only.",
    stop_condition=goal_reached(lambda state: looks_like_valid_json(state)),
    max_iterations=4,
)
```

If the model's answer isn't valid JSON, `stop_condition` returns `False`, `Loop` sends `"Continue working towards the goal."`, and the model gets another shot — instead of your downstream code crashing on bad output.

## 4. Multi-step research with a real search tool

Swap `fake_search` in the existing demo for a real one (e.g. wrapping a web search API), and raise `max_iterations` since open-ended research can take more steps:

```python
def web_search(query: str) -> str:
    response = requests.get("https://api.example.com/search", params={"q": query})
    return response.json()["summary"]

tools = ToolRegistry([
    Tool(name="web_search", description="Search the web for current information.",
         input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
         handler=web_search),
])

loop = Loop(provider=AnthropicProvider(), tools=tools, max_iterations=12)
state = loop.run("Summarize the latest news on X, with sources.")
```

## 5. DevOps / on-call assistant (read-only)

**Tools**: `get_logs(service, since)`, `get_metrics(service, metric)`, `get_recent_deploys(service)`. All read-only by design — this pattern is good for "help me understand what's happening" agents where you don't want the model able to restart anything.

```python
loop = Loop(
    provider=AnthropicProvider(),
    tools=tools,
    system_prompt="You help diagnose incidents. You can only read logs/metrics/deploys, never restart or modify anything.",
    max_iterations=10,
)
state = loop.run("The checkout service is returning 500s, what changed recently?")
```

## What changes between these examples, and what doesn't

Every example above reuses the exact same `Loop`, `Tool`, `ToolRegistry`, and `AnthropicProvider` classes from `src/loop_engineering/core/`. What changes per use case:

- **Which tools you register** (the "what can it do" surface)
- **The system prompt** (the "how should it behave" instructions, including hard boundaries like "never issue refunds")
- **`max_iterations`** (short for simple lookups, longer for open-ended research)
- **`stop_condition`** (default is "any tool-free answer is fine"; tighten it when you need to validate the shape or quality of the answer before accepting it)

Nothing in `core/loop.py` itself needs to change — that's the point of having pulled the loop apart into pieces.
