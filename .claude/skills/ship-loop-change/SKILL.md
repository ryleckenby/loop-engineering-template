---
name: ship-loop-change
description: Verify-before-ship workflow for a loop that just made a code change — run the project's test and lint commands, only commit and open a PR if they pass, and append a LOG.md entry either way. Use at the end of any loop run that edited code (e.g. the dev-trigger domain), or when the user says "ship this" / "verify and PR this change".
---

# ship-loop-change

A loop that edits code should never commit blind. This skill is the generalized version of the
`pytest` / `ruff check` / `mypy` commands already used in this repo's own CI
(`.github/workflows/ci.yml`) — turned into a reusable gate any loop's code-change step can call.

## Steps

1. **Detect the project's verification commands.** Look for, in order of preference:
   - A `Makefile` target like `test` or `verify`.
   - `package.json` `scripts.test` (Node projects).
   - `pyproject.toml` with `pytest`/`ruff`/`mypy` configured (Python projects — see this repo's
     own `pyproject.toml` for the pattern).
   - If none of the above is unambiguous, ask the user what command(s) verify this project.
2. **Run them.** Run lint first (fast, catches obvious problems cheaply), then type-check if
   configured, then tests.
3. **If any step fails:** stop. Do not commit. Report which command failed and the relevant error
   output. Append a `LOG.md` line noting the failed verification, so the loop's run is recorded
   even though it didn't ship.
4. **If all steps pass:** stage only the files this run actually changed (never `git add -A`
   blind — see the git safety rules already in effect for this session), commit with a message
   describing what changed and why, and push.
5. **Open a PR** via `gh pr create` if the user's workflow uses PRs (ask if unclear whether this
   repo merges directly to main or always goes through review).
6. **Append a `LOG.md` line** either way: `YYYY-MM-DD HH:MM | <domain> | shipped <summary> | <PR link or commit sha>` on success, or `... | verification failed: <which command> | <details>` on failure.

## Do not

- Do not skip verification "because the change is small."
- Do not force-push, amend, or skip git hooks to make a failing check pass.
- Do not commit if any configured test/lint/type-check command fails — surface the failure
  instead.
