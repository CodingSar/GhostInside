---
description: Best-practice rules per topic and domain. A domain row wins; the generic row is the fallback.
---

| Practice | Domain | File | What it covers |
|---|---|---|---|
| testing | generic | `generic/testing.md` | Acceptance-criteria tests, end-to-end style through slice entry points, real PostgreSQL, boundary-only mocks |

## Facet packs

Vendored by `init-factory` from the central practices repo (`decision-8`)
with `meta/tools/practices.py vendor`. The template ships an empty set.

| Path | What it holds |
|---|---|
| `packs/<kind>/<name>.md` | One pack per facet, copied verbatim from the central repo or approved locally. |
| `practices.lock` | Central repo URL, commit sha, and each pack's id, origin, researched date, and sha256. |
| `review.md` | Generated. Rules with `Enforce: review`. The searcher topic `practices:review` returns these to workers. |
| `enforced.md` | Generated. Rules enforced by lint, check command, or test. init-factory compiles them into tool config. |

Do not edit vendored or generated files. Change a pack upstream or locally,
then run `vendor` again. `meta/tools/check-harness.sh` runs `verify`.
