# Knowledge base

This folder is the shared memory that loops (see `domains/`) read and write between runs. It's
plain markdown + frontmatter in git — diffable, reviewable, and writable by both you and an
agent. There's no database; ripgrep and `git log` are the query and audit tools.

## The model

Two ideas:

1. **Artifacts are organized by kind, not by domain.** Each artifact has exactly one home, decided
   by *what it is* — a `signal/` lives in `signals/`, a `note/` lives in `notes/`. If something is
   relevant to more than one domain, it gets tagged with multiple `domain:` values in its
   frontmatter; it is never duplicated or nested under a domain folder.
2. **A domain is a loop, not a folder of content.** `domains/<name>/README.md` holds that loop's
   charter (goal, cadence/trigger, backlog) and links out to the signals/notes relevant to it. It
   never contains the artifacts themselves.

This keeps cross-cutting information in exactly one place, and keeps a domain's folder small
enough to read in one sitting.

## Kinds

| kind | folder | what it captures |
|---|---|---|
| `signal` | `signals/` | A piece of evidence — feedback, an observation, a recurring pattern — with a frequency count and source list |
| `note` | `notes/` | Durable knowledge — an analysis, a decision, something you learned that should outlive any one task |

Start with just these two. Each folder's own `README.md` is that kind's schema — read it before
adding an artifact of that kind. Add a new kind only once you can name a status machine,
queryable frontmatter fields, and a body shape that genuinely don't fit `signal` or `note`.

## The Timeline convention

Every artifact is a normal body plus an optional, append-only `## Timeline` section at the
bottom:

```markdown
## Timeline
- 2026-06-20 | task-refinement loop — first flagged: description was missing acceptance criteria
- 2026-06-22 | task-refinement loop — re-checked, still unresolved
```

The body answers "what's true now"; the Timeline answers "what happened, in order." This is also
how a `signal`'s frequency grows — each new Timeline line is one more occurrence of the same
evidence, instead of a duplicate file.

## LOG.md

The root `LOG.md` is the global activity feed — one line per run, across every domain. Detail
belongs in the artifact's own Timeline; `LOG.md` is just "what ran, when, and where to look."

## Spinning up a new loop

Run the `new-loop` skill (`.claude/skills/new-loop/SKILL.md`) to scaffold a new
`domains/<name>/README.md` from the template, rather than copying an existing domain by hand.
