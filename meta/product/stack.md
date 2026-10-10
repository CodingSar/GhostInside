# Stack

Status: TBD. Set by `init-factory`, which proposes each value and the user
ratifies it (`HD-5`). Nothing here is decided in advance.

| Key | Value |
|---|---|
| language and version | TBD |
| framework | TBD (or none) |
| package manager | TBD |
| install command | TBD |
| source root | TBD (default `src`) |
| source extensions | TBD |
| test file pattern | TBD (regex on the file name) |
| name case | TBD (one of kebab, snake, camel, pascal; default kebab, snake where the language imports folders by name) |
| entry file stems | TBD (default `index, handler`; the language's case, such as `Index, Handler`) |
| datastore | TBD (default PostgreSQL, `HD-2`) |
| connection variable | TBD (default `DATABASE_URL`) |
| migration command | TBD (or none) |
| test command (full) | TBD |
| test command (targeted, takes a path) | TBD |
| check command | TBD (default `scripts/check.sh`) |
| fix command | TBD (formatter and linter in fix mode) |
| dependencies approved | none |

The check command runs every static check and exits non-zero on any failure:
linter and formatter check, the import boundary checker, `structure.py`,
duplication (source files only, not tests), dead code, and practice
`check-cmd` rules. The fix command rewrites files in place with the
formatter and the linter's fix mode.

Cell values are bare: a path, a command, or a list. Notes go in this text,
not in the cells, because `packet.py` and `check.sh` read the cells.

Until the test command is set, the orchestrator stops at preflight
(`meta/core/guides/orchestrate.md`, section 0). Workers never guess a command.
