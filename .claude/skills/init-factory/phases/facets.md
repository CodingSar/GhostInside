# Phase: facets

Goal: the list of domain and concern facets whose practice packs the product
needs. Stack facets (`lang/`, `framework/`, `datastore/`) are added in the
stack phase, one per ratified stack item, because they follow from it.

## Facet ids

`<kind>/<name>`, name in kebab-case. Kinds here:

| Kind | Covers | Examples |
|---|---|---|
| `domain/` | Rules of the product's field | `domain/payments`, `domain/healthcare-records`, `domain/realtime-collaboration` |
| `concern/` | Cross-cutting quality concerns | `concern/security-web`, `concern/privacy-gdpr`, `concern/accessibility`, `concern/observability` |

## Steps

1. `python3 -I meta/core/tools/practices.py fetch`. Read `.cache/practices/index.json`
   for the ids that already exist. If `fetch` fails, the central repo is
   unreachable: note `central unreachable: <error>`, treat every facet as a
   miss, skip step 5, and continue.
2. From `product-brief`, derive candidates:
   - one `domain/` facet per distinct field the core jobs work in;
   - one `concern/` facet per brief field that raises a concern: data
     sensitivity and compliance, deploy target, integrations, scale.
3. Reuse an existing central id whenever it means the same thing. Name a new
   id only when nothing in the index fits.
4. At most eight facets. More: propose which to merge or drop.
5. `python3 -I meta/core/tools/practices.py status <ids>` to show hit, stale, or
   miss for each.
6. Gate: one row per facet. Proposal = the id and hit, stale, or miss. Why =
   the brief field it comes from. Rejected alternatives = merged or dropped
   candidates. Each miss costs a deep-research run in the practices phase.

## Output

Task note: `facets: <id> (hit|stale|miss), ...`. Nothing else is written.

Evidence for the criterion: the ratified list in the notes.

## Amend

Derive candidates from the changed brief fields only. Propose added facets
and facets that no longer apply. Removing a facet drops its pack in the
practices phase.
