# Harness governance

The harness changes live. It is not behind a review gate.

1. Harness files (`.claude/`, `meta/`, `AGENTS.md`, `CLAUDE.md`, `PLAN.md`) are
   edited directly on `main`.
2. Commit after each coherent change, in small commits. Push after each
   commit. Commits are the rollback path: restore an earlier version of a file
   from its commit. Never rewrite published history.
3. Run `meta/tools/check-harness.sh` before each harness commit. A failing
   check means the commit waits.
4. A change to a worker's limits (its tools, model, or allowlist rules) names
   the Backlog task that motivated it, in the commit message.
5. Hard denies in `.claude/settings.json` stay in place whatever the
   allowlists say. Changing a deny needs the user's explicit confirmation.
