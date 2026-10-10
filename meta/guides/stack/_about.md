---
description: Stack overlays for the core guides. Written by init-factory in a product clone. Empty in the template.
---

Core guides in `meta/guides/` belong to the template and stay the same in
every product, so harness upgrades merge cleanly (`decision-7`). What changes
per stack lives here, one overlay per core guide, same file name:

| Overlay | Adds to | Typical content |
|---|---|---|
| `orchestrate.md` | the orchestrator guide | stack commands to run, CI notes |
| `test.md` | the test-writer guide | test file naming, fixtures, datastore reset idiom, not-implemented idiom |
| `implement.md` | the implementer guide | language idioms, migration command, lint fix command |

Rules for overlays:

- Add specifics only: commands, paths, file extensions, idioms.
- Never remove or relax a stop rule or a forbidden item of the core guide.
- Short. A worker reads its core guide and its overlay, nothing else.
- Written by `init-factory` at its provision gate, after user approval.
