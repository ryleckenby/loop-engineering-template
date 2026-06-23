# The loop engineer pattern: orchestration + execution

This template combines two layers that solve different problems. Confusing them is the most
common way to over- or under-build a loop, so this doc exists to keep the boundary clear.

## The two layers

| Layer | Lives in | Answers |
|---|---|---|
| **Orchestration** | `knowledge/`, `CLAUDE.md`, `.claude/skills/` | When does a loop run, what does it remember between runs, and how does work compound across loops? |
| **Execution** | `src/loop_engineering/` | When a loop's *step* needs to reason over multiple tool calls autonomously, what runs that reasoning? |

A loop is not, by itself, the Python `Loop` class — that would conflate the two layers. A loop is
a Claude Code session (or a script it invokes) triggered on some cadence or event, that reads
`knowledge/domains/<name>/README.md` for context, does work, and writes back to `knowledge/` and
`LOG.md`. *Some* loops need the Python execution engine for their work; *some* don't.

## How triggers actually work

Nothing in this template implements cron or webhook listening — that would duplicate
infrastructure Claude Code already has:

- **Scheduled loops** (e.g. `task-refinement`, which runs periodically regardless of what's
  happening) — wire the domain's cadence to Claude Code's built-in `/schedule` skill (cron) or
  `/loop` skill (simple interval).
- **Event-driven loops** (e.g. `dev-trigger`, which only runs when something specific happens) —
  wire the event source (a webhook, a polling check, another loop's completion) to invoke a
  Claude Code session for that task. The mechanism for "listen for a webhook and invoke Claude
  Code" is infrastructure you own (a small server, a GitHub Action, etc.) — this template's job
  is what happens *after* that invocation, not the listening itself.

Either way, `knowledge/domains/<name>/README.md`'s `## Trigger` section is where you write down
*which* mechanism you chose and its exact cadence/event — so a human (or another loop) can tell
how this loop gets woken up without reverse-engineering it from infrastructure config.

## When a loop needs the execution engine, and when it doesn't

Ask: **does this step need to autonomously call tools in a loop, deciding for itself which tools
to call and when, based on results it can't predict in advance?**

- **Yes** → reach for `src/loop_engineering`. Example: `task-refinement` needs to look at however
  many open tasks exist, decide which ones lack acceptance criteria, and write criteria for each
  — an unknown, data-dependent number of tool calls. See `scripts/task_refinement_loop.py`.
- **No** → it's a plain Claude Code skill, using Claude Code's own built-in tools (read, write,
  edit, bash). Example: `dev-trigger`'s "implement this specific task, run tests, ship a PR" is a
  fixed sequence Claude Code already does well without a separate agent loop — see
  `.claude/skills/ship-loop-change/SKILL.md`.

Most domains will be the second kind. Reach for the Python engine when a step's tool-calling
shape is genuinely open-ended, not by default.

## Putting it together: one full cycle

Using `task-refinement` as the example:

1. **Orchestration**: Claude Code's `/schedule` skill fires on the cadence written in
   `knowledge/domains/task-refinement/README.md`.
2. **Orchestration**: the triggered session reads `CLAUDE.md` (project context) and that domain's
   README (charter + backlog) for context.
3. **Execution**: the session runs `scripts/task_refinement_loop.py`, which builds a `Loop` with
   `list_open_tasks`/`refine_task` tools and lets the model iterate until every task has
   acceptance criteria.
4. **Orchestration**: the session writes a `## Timeline` entry to the domain README, optionally
   files a `knowledge/signals/` entry if it noticed a recurring pattern (e.g. "tasks from team X
   are consistently underspecified"), and appends one line to `LOG.md`.

Next run, step 2 picks up exactly where this one left off — that's the compounding the orchestration
layer exists to provide; the execution layer never needs to know about it.

## Should you build out a library of skills?

This template ships three: `new-loop`, `ship-loop-change`, and `review-signals`. That's
deliberately small. The same "earn complexity" rule that governs `knowledge/domains/` (don't
scaffold a domain until a real recurring task needs it — see `knowledge/README.md`) applies here:
a shelf of speculative, never-run skills for needs your project doesn't have yet just goes stale
and gives false confidence that they're tested.

The three included skills earned their place differently than a speculative catalog would:
`new-loop` and `ship-loop-change` are needed by *any* domain (scaffolding, shipping); `review-signals`
is needed by *any* project that accumulates signals, regardless of domain content. None of them
assume a specific domain's subject matter.

When a project's actual need turns out to be domain-specific — a PR-review step, a support-triage
checklist, anything tied to one domain's content — write that skill when the need is real, using
this recipe instead of reaching for a pre-built one that won't fit:

1. Name it after the action it performs, not the domain (`triage-support-ticket`, not
   `support-domain-skill`) — skills are verbs, domains are nouns.
2. Frontmatter: `name` (matches the folder), `description` (one sentence stating *what it does*
   and *when to use it*, including a phrase a user might actually type — this is what Claude Code
   matches against to decide whether to invoke it).
3. Body: a short intro paragraph on why this skill exists, then a numbered `## Steps` section
   specific enough that two different runs produce the same shape of result, then a `## Do not`
   section for the failure modes you've already thought of (skipping verification, inventing data
   the user didn't give you, acting outside the one folder it should touch).
4. Test it on a throwaway case before trusting it on something real — see how this repo dogfooded
   `new-loop` and `ship-loop-change` in `LOG.md`'s `smoke-test` entry.

## See also

- [`concepts.md`](concepts.md) — what the execution-layer `Loop` itself is doing, iteration by iteration.
- [`examples.md`](examples.md) — more shapes the execution engine can take on its own.
- [`../knowledge/README.md`](../knowledge/README.md) — the orchestration layer's schema in full.
