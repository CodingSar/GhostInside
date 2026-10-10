# Phase: walking skeleton

Goal: proof that the loop the workers depend on runs: registry commands,
datastore, migrations, lint, tests, CI. You write this slice yourself; it is
harness proof, not product work, so it does not go through the orchestrator.

## The health slice

Follow `meta/architecture/` (the default or its replacement) and the source
root and extensions in `meta/registry/runner.md`.

- entry `index`: `check()` returns status `ok` when the datastore answers.
- `store`: inserts one row into `health_ping` and reads it back.
- `migrations/`: one migration creating `health_ping`, so the migration path
  is exercised.
- `tests/`: `AC1 health check reports ok with a live datastore`, through the
  entry point, against the real datastore, as `meta/practices/generic/testing.md`
  and the `test.md` overlay say.
- `shared/`: the datastore connection, read from the registry's connection
  variable.

When the stack has no datastore, `check()` returns `ok` with the version
string, and the test asserts it.

## Steps

1. Write the slice and `shared/`.
2. Run, in order, and keep the output:
   - the registry lint command;
   - the targeted test command on the slice's `tests/` path;
   - the full test command;
   - `meta/tools/check-harness.sh`.
3. Fix and rerun. Three rounds at most; still red: stop and report.
4. Commit and push. Watch CI: `gh run watch` on the latest run. Red: fix
   within the same three-round budget.
5. Gate: show the four outputs and the CI result. The user confirms the
   skeleton.

## Output

The health slice, `shared/`, a green CI run.

Evidence for the criterion: the last line of each command in step 2 and the
CI run URL.

## Amend

Rerun step 2 and the CI check only. Change the slice only if a superseding
decision changed the stack or layout.
