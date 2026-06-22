---
title: Dev trigger
type: domain
trigger: event-driven
event: "{{e.g. issue labeled 'ready-for-dev', or a webhook from your tracker}}"
status: active
---

# Dev trigger loop

## Charter

Goal: when a task is marked ready for implementation, pick it up automatically — implement the
change, verify it (tests/lint), and ship a PR — without someone manually starting a Claude Code
session for it.

## Trigger

**Event-driven**, not scheduled. Wire the event ({{a webhook, a polling check on a label, another
loop finishing}}) to invoke Claude Code on this task. The README for the triggered task is the
input; this domain's README just records the loop's own charter and run history.

## Why this doesn't need the Python execution engine

Unlike `task-refinement`, this loop's work — read the task, edit files, run tests, open a PR — is
exactly what Claude Code's own built-in tools (read/write/edit/bash) already do. There's no
custom multi-tool reasoning loop to build in Python here; the orchestration is "Claude Code, do
the task, then run the `ship-loop-change` skill." Use the Python engine (`src/loop_engineering`)
only if a *specific* step needs autonomous tool-calling beyond Claude Code's own tools (e.g.
calling out to an external service with a custom retry/observation loop).

## Verify-before-ship

This domain's implementation step should always end by running
`.claude/skills/ship-loop-change/SKILL.md` — it runs the project's test/lint commands and only
commits/opens a PR if they pass.

## Backlog

- {{Tasks currently picked up by this loop, or "none — purely event-driven, no standing backlog"}}

## Links

- Signals: {{link any `knowledge/signals/*` about recurring implementation friction}}
- Notes: {{link any `knowledge/notes/*` decisions about how this loop should implement changes}}

## Timeline

- {{YYYY-MM-DD}} | domain created from the loop-engineer-template scaffold
