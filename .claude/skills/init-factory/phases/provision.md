# Phase: provision

Goal: a fresh machine or CI runner gets from clone to running tests with the
ratified stack, and the workers know the stack specifics.

## Items to propose

| Item | File | Content |
|---|---|---|
| datastore | `compose.yaml` | The datastore service and a test database, health check, named volume. Only if the datastore runs as a server. |
| environment | `.env.example` | The connection variable from the registry and any other required variable, with local values. `.env` goes in `.gitignore`. |
| toolchain pin | language-native file (`.python-version`, `.nvmrc`, `rust-toolchain.toml`, ...) or `mise.toml` | Exact versions from the stack phase. |
| CI | `.github/workflows/ci.yml` | Datastore as a service container, toolchain setup, install, then the registry lint command and full test command, verbatim. |
| devcontainer | `.devcontainer/devcontainer.json` | Same toolchain, attached to the compose datastore. |
| permissions | `.claude/settings.json` | Allow entries for the package manager, test runner, linter, and `docker compose`. Add only. Never remove an entry. Never touch `deny`. |
| overlays | `orchestrate.md`, `test.md`, `implement.md` in `meta/guides/stack/` | As `meta/guides/stack/_about.md` says: commands, paths, extensions, idioms. Short. |
| ignore | `.gitignore` | Build output, virtual environments, `.env`. Keep existing lines. |

## Overlay content

- `test.md`: test file naming and location in a slice, how to reach the test
  database, how state is reset between tests, the not-implemented idiom for
  stubs.
- `implement.md`: how to add a migration, how to run the linter's fix mode,
  language idioms the review rules assume.
- `orchestrate.md`: the commands to bring the datastore up and install
  dependencies before tests.

## Steps

1. Draft every file. Gate: one row per file with a one-line summary.
2. Write the files.
3. Install dependencies and start the datastore (`docker compose up -d`).
4. Validate: `docker compose config -q`; the install exits 0; the CI file
   parses (`actionlint` if installed, otherwise say it was not linted).

## Output

The files above.

Evidence for the criterion: the validation output from step 4.

## Amend

Change only the files a superseding decision or a new pack affects. Show the
diff at the gate.
