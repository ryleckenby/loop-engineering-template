# Signals

A `signal` is a piece of evidence — feedback, an observation, a recurring pattern someone or some
loop noticed — captured once and then reinforced over time, rather than re-recorded as a new file
each time it happens again.

## Frontmatter

```yaml
---
title: Short, specific description of the observation
type: signal
category: <free text, e.g. "onboarding-friction", "perf", "feature-request">
frequency: 1            # increment each time a new Timeline entry confirms this signal again
sources: []             # where this came from: a ticket ID, a domain name, a person
domain: []              # which domain(s) this is relevant to (a list, not a folder)
status: open            # open | investigating | resolved | wontfix
---
```

## Body

A short description of the observation itself — what was noticed, and why it matters. Keep it
factual; save interpretation and decisions for a linked `note`.

## Timeline

Append one line per reinforcement, oldest first:

```markdown
## Timeline
- 2026-06-15 | support-triage loop — first report, ticket #4821
- 2026-06-19 | support-triage loop — third occurrence this week, bumping frequency to 3
```

## When to promote a signal to something else

If a signal turns into a decision or a piece of durable knowledge, write a `note` and link back
to the signal (`[[slug]]`) rather than expanding the signal's body — the signal stays "this kept
happening," the note becomes "here's what we decided to do about it."
