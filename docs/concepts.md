# Loop engineering, explained from zero

This doc assumes no prior context. If you've read `architecture.md` already, skip to [examples.md](examples.md) instead — this one is slower and more basic.

## The problem this solves

A single call to an LLM is a one-shot exchange: you send a prompt, you get a response, done. That's fine for "summarize this paragraph" but breaks down for "find out X and act on it" — the model can't look anything up, run code, or correct itself mid-task in a single call.

An **agentic loop** fixes this by repeating a cycle instead of doing one exchange:

```
1. THINK   — send the conversation so far to the model
2. ACT     — if the model asked to use a tool, run it
3. OBSERVE — feed the tool's result back into the conversation
4. repeat until the model gives a final answer with no more tool calls
```

This is sometimes called ReAct (Reason + Act), or just "the agent loop." "Loop engineering" is the practice of designing that loop well: what tools you give it, when to stop, how to handle errors, how much context to keep.

## Walking through one real call

Say you ask: *"What is 17 * 4, and what's the capital of Peru?"* — this is the exact example in `examples/research_agent.py`. Here's what happens, iteration by iteration, mapped to the actual code in `src/loop_engineering/core/loop.py`:

**Iteration 1.**
- `Loop.run()` puts your question into `LoopState.messages` as a `user` turn.
- It calls `provider.complete(...)` — this is the actual network request to Claude, via `AnthropicProvider`.
- The model can't do arithmetic reliably and doesn't know Peru's capital from a tool, so it responds with a **tool call**: `{"name": "calculator", "input": {"expression": "17 * 4"}}`.
- `Loop` sees this isn't a plain text answer (`response.has_tool_calls` is true), so it doesn't stop. It runs the tool: `ToolRegistry.dispatch("calculator", {"expression": "17 * 4"})` → returns `68.0`.
- That result gets appended back into `LoopState.messages` as a `tool_result` block — this is the "observe" step.

**Iteration 2.**
- The conversation now includes: your question, the model's tool call, and the tool's result (68.0).
- `Loop` calls `provider.complete(...)` again with this longer conversation.
- The model now calls a second tool: `fake_search` with `{"query": "capital of peru"}` → returns `"Lima"`.
- Again, this gets appended as an observation, and the loop continues.

**Iteration 3.**
- Now the model has both answers in its context (68.0 and "Lima") and responds with plain text — no tool call. Something like: *"17 * 4 is 68, and the capital of Peru is Lima."*
- `Loop` sees no tool calls in this response, checks `stop_condition(state)` (by default, `always()` — meaning "any tool-free answer is acceptable"), and since that passes, it calls `state.mark_done(...)` and returns.

That's the whole pattern. Three iterations, two tool calls, one final answer. If the question only needed one tool call, it'd be two iterations. If it needed five, it'd be six.

## The four pieces, and why each exists

| Piece | File | Job | Why it's separate |
|---|---|---|---|
| `Loop` | `core/loop.py` | Runs the think/act/observe cycle | This is the only piece that orchestrates — everything else plugs into it |
| `LLMProvider` | `core/providers/base.py` | Talks to the actual model | Defined as an interface (`Protocol`), so `Loop` doesn't care *which* model it's talking to |
| `Tool` / `ToolRegistry` | `core/tools.py` | Describes what the model can do, and runs it when asked | Keeps "what can this agent do" as data (a list of `Tool` objects), not scattered if/else logic |
| `StopCondition` | `core/stop_conditions.py` | Decides when a tool-free answer is "good enough" | Lets you require more than "model stopped calling tools" — e.g. "only stop once the output passes a check" |

`LoopState` (`core/state.py`) is the glue — it's the one object that gets passed through every iteration, holding the growing message history plus bookkeeping (iteration count, whether we're done, the final answer).

## Why a `Protocol` for the provider?

This is the one piece of "why is it built this way" that's worth understanding early. `LLMProvider` in `base.py` isn't a real class with logic — it's a typing-only contract:

```python
class LLMProvider(Protocol):
    def complete(self, messages, tools, system=None) -> ProviderResponse: ...
```

`AnthropicProvider` implements this contract for real, by calling the Claude API. `FakeProvider` (in `tests/fakes.py`) implements the same contract by returning pre-scripted answers instead of calling anything. `Loop` only ever calls `self.provider.complete(...)` — it has no idea, and doesn't need to know, which one it's talking to. That's what makes the test suite free and fast: it runs the exact same `Loop` code against `FakeProvider` instead of the real API.

If you ever wanted to swap in a different model vendor, you'd write one new class implementing `complete(...)`, and `Loop` wouldn't change at all.

## What "iteration" and "stop condition" actually control

Two settings on `Loop` matter most when you're starting out:

- **`max_iterations`** (default 10) — a hard ceiling. If the model keeps calling tools and never settles on a final answer, the loop raises `MaxIterationsExceeded` instead of running forever (and costing you money on every iteration). Lower this for quick tasks, raise it for genuinely multi-step research.
- **`stop_condition`** (default `always()`) — by default, *any* tool-free response is accepted as done. You can tighten this — e.g. `goal_reached(lambda state: "TODO" not in state.final_answer)` — to reject answers that don't meet a bar, which makes the loop nudge the model to try again (see the `state.add_user_message("Continue working towards the goal.")` line in `loop.py`).

## Where to go next

- [`examples.md`](examples.md) — concrete things you could build with this besides the calculator demo.
- [`getting_started.md`](getting_started.md) — how to actually run it, including against the real API.
- [`architecture.md`](architecture.md) — the file-by-file reference, once the above clicks.
