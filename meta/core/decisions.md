---
description: Harness decisions with their rationale. HD-n is decision-n of the harness backlog (meta/core/backlog). Product decisions live in the root backlog as decision-n.
---

# Harness decisions

The Backlog decision CLI stores a title only, so the rationale lives here.
`HD-n` is `decision-n` in the harness backlog (`BACKLOG_CWD=meta/core backlog
decision list --plain`). Cite harness decisions as `HD-n`. A bare
`decision-n` always means the product backlog.

| ID | Decision | Why | Rejected | Status |
|---|---|---|---|---|
| HD-1 | Default architecture: vertical slices. | A small model holds one folder in context; a step's allowlist is one folder, so a wrong-file edit is easy to detect. | Layered (controllers/services/repos): every feature touches every layer, so allowlists grow. | amended by HD-11 |
| HD-2 | Default datastore: PostgreSQL only. | One datastore, tested for real, removes a class of mocking and choice errors. | SQLite (diverges from production), document stores (no schema), in-memory fakes. | accepted |
| HD-3 | Stack and test runner undecided until init-factory. | The template serves any product; a premature stack is wrong for most. | A default stack. | amended by HD-5 |
| HD-4 | GhostInside is a template; each product is a user-made `git clone` with the template as the `harness` remote. | Shared history lets harness upgrades merge into products. | GitHub template button (no shared history), a package or submodule (harness files must sit in the repo for Claude Code). | accepted |
| HD-5 | init-factory proposes stack and architecture; the user ratifies at five grouped gates: brief, facets, stack and architecture, packs, provision and seed. | The model researches; the user owns product choices. Grouping keeps the user's effort bounded. | Ask per item (too many prompts); decide silently (no ownership). | accepted |
| HD-6 | Defaults HD-1 and HD-2 are priors; a product supersedes them only by a ratified decision. | Defaults fit most products, not all (a CLI with no stored data needs no PostgreSQL). | Hard defaults. | accepted |
| HD-7 | Core guides are template-owned; stack specifics go in overlays. | Core guides stay identical across products, so harness upgrades merge cleanly. | init-factory rewriting core guides. | amended by HD-9 |
| HD-8 | Practices come from the central repo `CodingSar/GhostInsidePractices` as facet packs, vendored with a lock, delta-checked after 7 days; new packs go back by PR and a human merges. | Research is expensive; packs are reused across products and reviewed once. | Research per product; unreviewed writes to the central repo. | accepted |
| HD-9 | Two layers: `meta/core/` is template-owned and never edited in a clone; `meta/product/` is written by init-factory. A product file overrides the core default of the same name (`meta/product/architecture.md` over `meta/core/defaults/architecture.md`). | Defaults and product values in the same files conflict on every harness merge. One rule says who owns a file, and check-harness can enforce it. | Overlays for guides only (HD-7 alone). | accepted |
| HD-10 | The harness backlog lives in `meta/core/backlog/`; the root `backlog/` is the product's and the template ships it empty. | Template tasks in the root backlog shipped into products and collided with product task ids on harness merges. | A task prefix per product (the prefix is read-only after init and template tasks still show up as product work). | accepted |
