---
description: Catalog of the harness. Read this first, then only the directories the current job names.
---

| Directory | What it holds |
|---|---|
| `guides/` | Procedures. The orchestrator reads `orchestrate.md`. Each worker reads the guide named in its agent file. |
| `architecture/` | Structure defaults. Default style: vertical slices. |
| `registry/` | Fixed choices: datastore, test runner, approved dependencies. Runner is TBD until init-factory. |
| `practices/` | Best-practice rules by topic. Currently: testing. |
| `tools/` | Harness checks, run before harness commits. |
| `docs/` | Governance: how harness changes are made and rolled back. |

Decisions are not in these files. They live in Backlog: `backlog decision list --plain`.
