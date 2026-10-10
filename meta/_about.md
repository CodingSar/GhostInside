---
description: Catalog of the harness. Read this first, then only the files the current job names.
---

Two layers (`HD-9`). `core/` belongs to the template and is never edited in a
product clone. `product/` is written by init-factory in the clone. For
`architecture.md` and `persistence.md`, a file in `product/` overrides the
default of the same name in `core/defaults/`.

| Path | What it holds |
|---|---|
| `core/guides/` | Procedures. The orchestrator reads `orchestrate.md`; each worker reads the guide its agent file names. |
| `core/defaults/` | Defaults a product may override: `architecture.md` (modules of slices), `persistence.md` (PostgreSQL only). |
| `core/tools/` | Deterministic tools: `check-harness.sh` (run before harness commits), `practices.py` (practice packs). |
| `core/decisions.md` | Harness decisions `HD-n` with rationale. |
| `core/backlog/` | Harness backlog (`BACKLOG_CWD=meta/core`). History in a clone. |
| `product/` | Product layer: stack, overlays, practices, overrides. See `product/_about.md`. |

Product decisions live in the root Backlog: `backlog decision list --plain`,
rationale in the Backlog doc `init-decisions`.
