# Phase: walking skeleton

Goal: proof that the loop the workers depend on runs: stack commands,
datastore, migrations, the check command, tests, CI. You write this module
yourself; it is harness proof, not product work, so it does not go through
the orchestrator. No gate: every piece of evidence is a command result.

## The health module

Follow the architecture (`meta/product/architecture.md` if it exists, else
`meta/core/defaults/architecture.md`) and the source root, extensions, and
commands in `meta/product/stack.md`. Names below are file stems; use the
stack's entry file stems and name case.

- `<source root>/_about.md`: one row, `health`, with its purpose.
- `modules/health/_about.md`: purpose, public API `check`, table
  `health_ping`, slice `check`.
- `modules/health/index`: re-exports `check`.
- `modules/health/store`: inserts one row into `health_ping` and reads it
  back.
- `modules/health/migrations/`: one migration creating `health_ping`.
- `modules/health/slices/check/handler`: `check()` returns status `ok` when
  the datastore answers.
- `modules/health/slices/check/` test file: `<init task id>#8 health check
  reports ok with a live datastore`, through the handler, against the real
  datastore, as `meta/core/guides/test.md` and the `test.md` overlay say.
- `shared/`: the datastore connection, read from the connection variable.
- `app/`: the entry point that wires `health.check` into the product's
  transport (a route, a CLI command, or a job, per the brief's deploy
  target).

Stack without a datastore (datastore `none`, by a superseding decision):
`check()` returns `ok` with the version string, the test asserts it, and
there is no store or migration. Report that the skeleton proves no
datastore, and why.

## Steps

1. Write the module, `shared/`, and `app/`.
2. Run, in order, and keep the output:
   - the migration command (skip without a datastore);
   - the check command (it includes `structure.py` and the boundary checker);
   - the targeted test command on the slice's path;
   - the full test command;
   - `meta/core/tools/check-harness.sh`.
3. Fix and rerun. Three rounds at most; still red: stop and report.
4. Commit and `git push origin main`. Find the CI run for that commit:
   `gh run list --commit <sha> --limit 1 --json databaseId --jq '.[0].databaseId'`,
   then `gh run watch <id> --exit-status`. The run may take a few seconds to
   appear; retry the list a few times. Red: fix within the same three-round
   budget. Without `gh`: note `CI not checked: gh unavailable`.
5. Report the outputs of step 2 and the CI result to the user.

## Output

The health module, `shared/`, `app/`, a green CI run.

Evidence for the criterion: the last line of each command in step 2 and the
CI run URL. Without a CI result, leave the criterion unchecked and report
it; the init task stays In Progress until CI is checked.

## Amend

Rerun step 2 and the CI check only. Change the module only if a superseding
decision changed the stack or layout.
