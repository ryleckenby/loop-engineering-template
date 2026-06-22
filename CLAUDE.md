# {{PROJECT_NAME}}

This file is read by every Claude Code session in this repo, including every triggered loop run.
Fill in every `{{PLACEHOLDER}}` before relying on this as a real project — an agent reading
unfilled placeholders has no real context to act on.

## What this project is

{{One or two sentences: what this project does, who it's for.}}

## Stack

{{e.g. "Python 3.11, FastAPI, Postgres" or "TypeScript, Next.js" — whatever a session needs to
know before touching code.}}

## How this repo is organized

- `src/loop_engineering/` — the Python ReAct-style agent engine (`Loop`, `Tool`, `ToolRegistry`,
  `AnthropicProvider`). Use this when a loop's step needs autonomous, multi-tool reasoning beyond
  what Claude Code's own built-in tools already do. See `docs/loop-engineer-pattern.md` for when
  to reach for this vs. a plain Claude Code skill.
- `knowledge/` — the shared memory loops read and write between runs (`signals/`, `notes/`,
  `domains/`). Read `knowledge/README.md` once; it's short.
- `.claude/skills/` — `new-loop` (scaffold a domain) and `ship-loop-change` (verify-before-ship).
- `LOG.md` — the global activity feed. Append one line here right before you commit a bulk of
  work from any loop run.

## What every loop run should do

1. Read this file and the relevant `knowledge/domains/<x>/README.md` for the domain you're
   running as.
2. Do the work described in that domain's charter and backlog.
3. Write findings/decisions to `knowledge/signals/` or `knowledge/notes/` as appropriate — not
   into the domain README itself (the domain README links out, it doesn't hold content).
4. Append a dated line to that domain's `## Timeline`, and a one-line summary to the root
   `LOG.md`.
5. If the run touched code, finish by running `.claude/skills/ship-loop-change/SKILL.md` rather
   than committing directly.

## Project-specific rules

{{Add anything an agent should always/never do in this specific project — coding conventions,
things that require human approval, services it should never call, etc.}}
