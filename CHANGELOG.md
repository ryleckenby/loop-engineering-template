# Changelog

## 0.1.0 — 2026-06-22

Initial release.

- `Loop`, `LoopState`, `Tool`, `ToolRegistry` core abstractions.
- `LLMProvider` protocol + `AnthropicProvider` (Claude API) implementation.
- Composable stop conditions (`always`, `goal_reached`, `any_of`, `all_of`).
- `examples/research_agent.py` runnable demo.
- Test suite using a scripted `FakeProvider` (no API key required).
- CI (ruff, mypy, pytest) on Python 3.10–3.12.
