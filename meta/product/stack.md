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
| datastore | TBD (default PostgreSQL, `HD-2`) |
| connection variable | TBD (default `DATABASE_URL`) |
| migration command | TBD (or none) |
| test command (full) | TBD |
| test command (targeted, takes a path) | TBD |
| check command | TBD (default `scripts/check.sh`) |
| dependencies approved | none |

The check command runs every static check and exits non-zero on any failure:
linter and formatter check, the import boundary checker, `structure.py`,
duplication, dead code, and practice `check-cmd` rules.

Until the test command is set, the orchestrator stops at preflight
(`meta/core/guides/orchestrate.md`, section 0). Workers never guess a command.
