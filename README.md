# GhostInside

A software factory harness that small models can run. Claude Code's main
thread orchestrates; Haiku subagents write tests and code inside tight file
allowlists; deterministic tools check everything that can be checked.

GhostInside is a template. Each product is a clone of it.

## Start a product

1. Create an empty repository for the product.
2. `git clone git@github.com:CodingSar/GhostInside.git <product>` (a plain
   clone, not the GitHub template button, so harness upgrades can merge).
3. In the clone, write the idea to `CONCEPT.md` and run `/init-factory` in
   Claude Code. It renames `origin` to `harness`, adds your repository as
   `origin`, and walks you through six gates: brief, screens (mockups,
   only for a product with a GUI), facets, stack and architecture, practice
   packs, provision and seed. It ends with a green walking skeleton.
4. Promote a draft (`backlog draft promote <id>`) and ask Claude to run the
   orchestrator on it (`meta/core/guides/orchestrate.md`).

Upgrade the harness later with `git pull harness main`.

## Layout

```
AGENTS.md, CLAUDE.md     agent instructions (template-owned)
.claude/                 workers, init-factory skill, settings, guard hook
backlog/                 product backlog (empty in the template)
meta/
  _about.md              catalog; read first
  core/                  template-owned: guides, defaults, tools, decisions, design, harness backlog
  product/               written by init-factory: stack, overlays, practices
src/                     product code, created by the factory (modules of slices)
```

Design: `meta/core/design.md`. Decisions: `meta/core/decisions.md`.

## Work on the harness itself

Harness work happens in this template repository, on `main`, in small
commits. Its backlog is `meta/core/backlog/`: prefix Backlog commands with
`BACKLOG_CWD=meta/core`. Run `meta/core/tools/check-harness.sh` before each
commit.
