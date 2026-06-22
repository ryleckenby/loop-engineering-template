# Notes

A `note` is durable knowledge: an analysis, a decision and the reasoning behind it, or something
a loop learned that should outlive the task that produced it. This is the "named `notes/` instead
of `docs/`" kind mentioned in the top-level `knowledge/README.md` — kept separate from this
repo's own `docs/` (which documents this template itself, not project knowledge) so the two never
get confused.

## Frontmatter

```yaml
---
title: Short, specific title
type: note
domain: []        # which domain(s) this is relevant to
status: adopted   # draft | adopted | superseded — omit for pure observations with no lifecycle
links: []         # related artifacts, by [[slug]]
---
```

## Body

Write it like you'd want to read it cold in six months: what's true, why, and — for a decision —
what alternatives were considered and rejected. See `docs/architecture.md` in this repo's own
`docs/` folder for an example of that shape (it documents a different decision, but the shape is
the one to copy: state the model, then "options considered, and why not").

## Timeline

Append-only, dated, one line per event that changed or reaffirmed this note:

```markdown
## Timeline
- 2026-05-02 | created from dev-trigger loop's first three runs
- 2026-06-10 | superseded by [[new-deploy-strategy]] — see that note for why
```

## One concept, one home

If a piece of knowledge is relevant to three domains, it still lives in exactly one `note` file —
tag it with all three `domain:` values and link to it from each domain's README. Don't duplicate
it under multiple domains.
