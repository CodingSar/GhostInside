---
description: Product layer of the harness. Written by init-factory in a product clone; the template ships it with TBD values and no packs.
---

| Path | What it holds | In the template |
|---|---|---|
| `stack.md` | Language, tools, and every command the factory runs. | all TBD |
| `architecture.md`, `persistence.md` | Override of the core default of the same name, only by a superseding decision. | absent |
| `overlays/<guide>.md` | Stack specifics for the core guide of the same name: `orchestrate.md`, `test.md`, `implement.md`. | absent |
| `screens/<id>.html`, `screens/_about.md` | Static HTML mockups of a GUI product's screens, and their catalog (`HD-15`). Never copied into the source root. | absent |
| `practices/packs/<kind>/<name>.md` | Facet packs vendored from the central practices repo (`HD-8`). | absent |
| `practices/practices.lock` | Central repo URL and sha; each pack's id, origin, researched date, sha256. | empty set |
| `practices/review.md` | Generated. Pack rules with `Enforce: review`; workers apply them. | empty |
| `practices/enforced.md` | Generated. Pack rules enforced by lint, check command, or test. | empty |

Overlay rules:

- Add specifics only: commands, paths, file extensions, idioms.
- Never remove or relax a stop rule or a forbidden item of the core guide.
- Short. A worker reads its core guide and its overlay, nothing else.

Practices: never edit vendored or generated files. Change a pack upstream or
locally, then run `meta/core/tools/practices.py vendor` again.
`meta/core/tools/check-harness.sh` runs `practices.py verify`.
