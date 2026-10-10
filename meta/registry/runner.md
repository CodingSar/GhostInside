# Registry: runner and stack

Status: TBD. Set by `init-factory`, which asks the user for each value below.
Nothing here is decided in advance.

| Key | Value |
|---|---|
| language | TBD |
| package manager | TBD |
| test command (full) | TBD |
| test command (targeted, takes a path) | TBD |
| lint command | TBD |
| dependencies approved | none |

Until the test command is set, the orchestrator stops at preflight
(`meta/guides/orchestrate.md`, section 0). Workers never guess a runner.

Once set, `init-factory` records the values here and records the choice as a
Backlog decision.
