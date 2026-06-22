# Contributing

This is a personal template repo, but contributions/suggestions are welcome.

1. Fork and clone the repo.
2. `pip install -e ".[dev]"`
3. Make your change with tests. Keep `Loop`/`LLMProvider`/`Tool` provider-agnostic — don't leak Anthropic-specific shapes outside `providers/anthropic_provider.py`.
4. Before opening a PR: `ruff check .`, `mypy src`, `pytest` should all pass.
5. Open a PR describing the change and why.

## Style

- Type hints on all public functions.
- Prefer small, composable functions over large ones (see `stop_conditions.py` for the pattern).
- No comments explaining *what* code does — only *why*, when it's non-obvious.
