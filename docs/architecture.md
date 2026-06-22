# Architecture

## The agentic loop

An "agentic loop" is the pattern behind most LLM agents: the model isn't
asked once and done, it's run inside a loop that keeps feeding it the
results of its own actions until it produces an answer worth keeping.

```
            ┌─────────────────────────────────────────┐
            │                                          │
            ▼                                          │
   ┌─────────────────┐      tool calls?     ┌──────────────────┐
   │  provider.complete│ ───── yes ────────▶ │  dispatch tools   │
   │   ("think")       │                     │   ("act")         │
   └─────────────────┘                       └──────────────────┘
            │                                          │
            │ no tool calls                  tool results appended
            ▼                                  as observations
   ┌─────────────────┐                                  │
   │ stop_condition?   │ ◀────────────────────────────────┘
   └─────────────────┘
       │         │
      yes        no
       │         │
       ▼         ▼
    return    nudge model, loop again
```

## Components (`src/loop_engineering/core`)

| Module | Responsibility |
|---|---|
| `state.py` | `LoopState` — message history, iteration count, scratchpad, done flag. The single mutable object passed through a run. |
| `tools.py` | `Tool` + `ToolRegistry` — describes callable tools as JSON schema and dispatches model-requested calls to Python handlers. |
| `stop_conditions.py` | Predicates over `LoopState` that decide whether a tool-free response is an acceptable final answer (`always`, `goal_reached`, `any_of`, `all_of`). |
| `providers/base.py` | `LLMProvider` protocol + `ProviderResponse`/`ToolCall` — the seam between the loop and any specific model API. |
| `providers/anthropic_provider.py` | The only concrete provider: calls Claude via the `anthropic` SDK. |
| `loop.py` | `Loop` — the orchestrator. Owns the think/act/observe cycle and the iteration cap. |
| `exceptions.py` | `LoopError` and friends (`MaxIterationsExceeded`, `ToolExecutionError`, `ProviderError`). |

## Why a `Protocol` for the provider

`Loop` only depends on `LLMProvider.complete(messages, tools, system) -> ProviderResponse`.
Swapping providers (a different model, a mocked one for tests, a future
non-Anthropic backend) never requires touching `Loop` itself — see
`tests/fakes.py::FakeProvider` for the pattern used throughout the test suite.

## Why tool errors don't crash the loop

A tool handler raising an exception is dispatched-and-caught inside
`Loop._execute_tool_call`, turned into a `tool_result` block with
`is_error: True`, and fed back to the model as an observation. This mirrors
how the Claude API expects tool failures to be communicated, and lets the
model retry or recover instead of the whole run dying on one bad call.
