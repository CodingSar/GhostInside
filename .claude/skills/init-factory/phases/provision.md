# Phase: provision

Goal: a fresh machine or CI runner gets from clone to running tests with the
ratified stack, and the workers know the stack specifics.

Gate: shared with the seed phase (`SKILL.md`). Draft this phase's files and
the seed drafts, show both in one table, then write both.

## Items to propose

Commands below are the values in `meta/product/stack.md`, copied verbatim.

| Item | File | Content |
|---|---|---|
| datastore | `compose.yaml` | The datastore service and a test database, health check, named volume. Only if the datastore runs as a server. |
| environment | `.env.example` | The connection variable and any other required variable, with local values. `.env` goes in `.gitignore`. |
| toolchain pin | language-native file (`.python-version`, `.nvmrc`, `rust-toolchain.toml`, ...) or `mise.toml` | Exact versions from the stack phase. |
| CI | `.github/workflows/ci.yml` | Datastore as a service container, toolchain setup, then the install, migration, check, and full test commands. |
| devcontainer | `.devcontainer/devcontainer.json` | Same toolchain, attached to the compose datastore. |
| permissions | `.claude/settings.json` | Allow entries for the package manager, test runner, linter and checkers, migration tool, and `docker compose`. Add only. Never remove an entry. Never touch `deny` or `hooks`. |
| overlays | `meta/product/overlays/` | `orchestrate.md`, `test.md`, `implement.md`, as below and as `meta/product/_about.md` says. |
| ignore | `.gitignore` | Build output, virtual environments, `.env`. Keep existing lines. |
| readme | `README.md` | The product's name and one-liner from `product-brief`, how to install, start the datastore, run tests and checks. Keep a short "Built with the GhostInside harness" section pointing to `meta/_about.md`. |

## Overlay content

- `test.md`: the test file name inside a slice (it must match the stack's
  test file pattern), how test names carry `TASK-n#k` in this language, how
  to reach the test database, how state is reset between tests (the reset
  must tolerate tables that do not exist yet), the
  not-implemented idiom for stubs, and how a module `index` re-exports a
  handler. If the datastore was superseded, the replacement and how tests
  reach it.
- `implement.md`: how to add a migration, how to run the linter's fix mode,
  how the boundary checker reports a violation, language idioms the review
  rules assume, and the rules noted `review via overlay` in the practices
  phase, verbatim with their ids.
- `orchestrate.md`: the commands to bring the datastore up, install
  dependencies, and run migrations before tests.

## Steps

1. Tools: if the datastore runs as a server, `docker compose version` must
   succeed. If Docker or its compose plugin is missing, ask the user to
   install it; if they do not, stop.
2. Draft every file. Gate rows (shared gate): one row per file. Proposal = a
   one-line summary. Why = the stack value or decision it serves. Rejected
   alternatives = other options considered (for example another CI
   provider) or `-`.
3. Write the files.
4. Run the install command and start the datastore
   (`docker compose up -d --wait`). Run the migration command.
5. Validate: `docker compose config -q`; install and migration exit 0; the
   CI file parses (`actionlint` if installed, otherwise note `CI file not
   linted`).

## Output

The files above.

Evidence for the criterion: the output of steps 4 and 5.

## Amend

Change only the files a superseding decision or a new pack affects. Show the
diff at the gate.
