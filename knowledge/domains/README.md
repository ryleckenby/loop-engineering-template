# Domains (loops)

A domain is one loop: a separable thread of work with its own goal, cadence or trigger, and
owner. `domains/<name>/README.md` is that loop's charter and live state — it links out to
`signals/` and `notes/` relevant to it, but never contains artifacts itself (see the top-level
`knowledge/README.md` for why).

## What belongs in a domain's README

- **Charter** — goal, in one or two sentences. What is this loop for?
- **Trigger** — scheduled (cron, via Claude Code's `/schedule`), interval (via `/loop`), or
  event-driven (a webhook, a label change, another loop finishing). Be specific: "every 30
  minutes" or "on `issue.labeled: ready-for-dev`," not "periodically."
- **Backlog** — a plain list of pending work items for this loop. Promote to a dedicated `task`
  kind only once the backlog has outgrown a markdown list (see `knowledge/README.md` → "Add a new
  kind only once...").
- **Links** — `signals/` and `notes/` this loop reads or has produced.
- **`## Timeline`** — one terse, dated line per run: what happened, what changed. This is the
  loop's own run-log; it is not a place for rich detail (that belongs in whichever signal/note the
  run touched).

## Two example domains in this template

- [`task-refinement/README.md`](task-refinement/README.md) — a **scheduled** loop: periodically
  reviews newly added tasks and refines them before they're picked up for implementation.
- [`dev-trigger/README.md`](dev-trigger/README.md) — an **event-driven** loop: when a task is
  marked ready, implements it, verifies it, and ships a PR.

Copy either one as a starting point for your own domain, or run the `new-loop` skill to scaffold
a fresh one from a blank template.

## Spinning up a new domain

```
/new-loop
```

This skill (`.claude/skills/new-loop/SKILL.md`) asks for the domain's name, goal, and trigger,
scaffolds `domains/<name>/README.md`, and appends an entry to the root `LOG.md`.
