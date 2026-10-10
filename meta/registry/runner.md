# Registry: runner and stack

Status: TBD. Set by `init-factory`, which proposes each value below and the
user ratifies it (`decision-5`). Nothing here is decided in advance.

| Key | Value |
|---|---|
| language | TBD |
| framework | TBD (or none) |
| package manager | TBD |
| install command | TBD |
| source root and file extensions | TBD |
| datastore | TBD (default PostgreSQL, `decision-2`) |
| connection variable | TBD (default `DATABASE_URL`) |
| migration command | TBD (or none) |
| test command (full) | TBD |
| test command (targeted, takes a path) | TBD |
| lint command | TBD |
| dependencies approved | none |

Until the test command is set, the orchestrator stops at preflight
(`meta/guides/orchestrate.md`, section 0). Workers never guess a runner.

Once set, `init-factory` records the values here and records the choice as a
Backlog decision.
