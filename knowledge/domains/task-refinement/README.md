---
title: Task refinement
type: domain
trigger: scheduled
cadence: "{{e.g. every 30 minutes}}"
status: active
---

# Task refinement loop

## Charter

Goal: review tasks/features as they're added to {{ISSUE_TRACKER, e.g. "the GitHub Issues board"}},
and refine each one — fill in missing acceptance criteria, flag ambiguous scope, ask a clarifying
question — before it's picked up for implementation.

## Trigger

**Scheduled** — runs on a cadence, not in response to a specific event. Wire this up with Claude
Code's built-in `/schedule` skill (cron, e.g. `0 */1 * * *` for hourly) or `/loop` (simple
interval). This domain does not need its own cron implementation.

## Why this needs the Python execution engine

This loop's work is genuinely multi-step and tool-using: fetch open tasks, decide which need
refinement, write back a comment or edit, possibly look something up. That's exactly the shape
`src/loop_engineering` is for. See `scripts/task_refinement_loop.py` for a runnable example using
`Loop`/`Tool`/`ToolRegistry` with `{{get_open_tasks}}` / `{{update_task}}` tools wired to your
real issue tracker's API.

## Backlog

- {{Pending refinement work items go here as a plain list, or promote to a `task` kind once this
  outgrows a list — see `knowledge/README.md`.}}

## Links

- Signals: {{link any `knowledge/signals/*` this loop has raised}}
- Notes: {{link any `knowledge/notes/*` decisions that shape how this loop refines tasks}}

## Timeline

- {{YYYY-MM-DD}} | domain created from the loop-engineer-template scaffold
