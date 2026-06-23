---
name: review-signals
description: Scan knowledge/signals/ for evidence that has built up enough frequency or sources to act on, and either promote it to a knowledge/notes/ decision, add it to a domain's backlog, or leave it open. Use periodically (wire to /schedule or /loop) or when the user asks "what's been piling up?" / "anything we should act on from signals?". Domain-agnostic — works the same regardless of which loops are running.
---

# review-signals

Signals are evidence captured once and reinforced over time (see `knowledge/signals/README.md`).
Left alone, they just accumulate — nothing in this template automatically promotes one once it's
"enough." This skill is that review step: a cross-cutting pass any project using this template can
run, independent of which domains it has.

## Steps

1. Read every `knowledge/signals/*/README.md` (or `.md` file, depending on how the project named
   them) with `status: open` or `status: investigating`.
2. For each one, look at its `frequency` and `Timeline` length, and judge whether it's crossed the
   point of being worth acting on. There's no fixed number — a `frequency: 2` signal spanning three
   months is different from `frequency: 2` twice in one day. Use judgment, not a hard threshold.
3. For each signal that's crossed that point, do exactly one of:
   - **Promote to a note** — if it's become a decision or durable knowledge, write a
     `knowledge/notes/<slug>.md` per that folder's schema, link back to the signal with `[[slug]]`,
     and add a Timeline line to the signal noting the promotion.
   - **Add to a domain's backlog** — if it's actionable work for an existing loop, append it to
     that domain's `## Backlog` and link the signal from the domain's `## Links`.
   - **Leave it open** — if it hasn't crossed the threshold yet, do nothing except note in your
     summary to the user that you looked and it's not there yet.
4. Append one line per signal you acted on to that signal's own `## Timeline` (per
   `knowledge/signals/README.md`'s convention) — never edit a Timeline's existing lines.
5. Append one line to the root `LOG.md` summarizing what this pass did:
   `YYYY-MM-DD HH:MM | review-signals | promoted N, backlogged N, left M open | [[knowledge/signals/...]]`.
6. Report back to the user which signals you acted on and why, and which you left open.

## Do not

- Do not delete or edit existing Timeline lines on a signal — only append.
- Do not promote a signal to a note just because it's old; promote because it's actionable or
  decided, not because of age alone.
- Do not invent a `domain:` or `category:` value for a signal that doesn't have one — ask, or
  leave it untagged.
