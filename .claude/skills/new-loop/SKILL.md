---
name: new-loop
description: Scaffold a new domain (loop) in the knowledge base — asks for the domain's name, goal, and trigger, creates knowledge/domains/<name>/README.md from the charter template, and appends an entry to LOG.md. Use when the user wants to start tracking a new recurring or event-driven loop (e.g. "set up a new loop for X", "I want a domain that watches Y").
---

# new-loop

Scaffolds a new entry under `knowledge/domains/` so a new loop has a charter before it starts
running. This does not start any automation itself — it only creates the README that documents
the loop's goal, trigger, and backlog. Wiring the actual trigger (a `/schedule` cron, a `/loop`
interval, or an event hook) is a separate, explicit step the user does after this.

## Steps

1. Ask the user for three things, if not already given in their request:
   - **Name** — a short, kebab-case slug (e.g. `support-triage`). This becomes the folder name
     under `knowledge/domains/`.
   - **Goal** — one or two sentences: what is this loop for?
   - **Trigger shape** — scheduled (give a cadence) or event-driven (give the triggering event).
2. Check `knowledge/domains/<name>/` doesn't already exist. If it does, ask whether to edit the
   existing one instead of creating a duplicate.
3. Create `knowledge/domains/<name>/README.md` using the same shape as the two example domains in
   this template (`knowledge/domains/task-refinement/README.md` for a scheduled example,
   `knowledge/domains/dev-trigger/README.md` for an event-driven one) — frontmatter (`title`,
   `type: domain`, `trigger`, cadence/event, `status: active`), then `## Charter`, `## Trigger`,
   `## Backlog` (start empty), `## Links` (start empty), `## Timeline` (one entry: domain
   created).
4. Append one line to the root `LOG.md`: `YYYY-MM-DD HH:MM | <name> | domain created | [[knowledge/domains/<name>/README.md]]`.
5. Tell the user the domain is scaffolded, and remind them this didn't wire up the actual trigger
   — point them at Claude Code's `/schedule` or `/loop` skill (or their event source) to do that
   next.

## Do not

- Do not invent a goal or trigger the user didn't give you — ask rather than guess.
- Do not create the domain folder under anything other than `knowledge/domains/`.
- Do not start running the loop's automation as part of scaffolding it.
