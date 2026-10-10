# Phase: seed

Goal: a starting backlog the user can promote from. Drafts, not tasks: the
orchestrator owns real tasks (`meta/guides/orchestrate.md`).

Read `backlog instructions task-creation` first.

## Source tags

Every criterion ends with exactly one source tag:

| Tag | Use |
|---|---|
| `[brief: <field>]` | The criterion follows from that `product-brief` field. |
| `[pack: <pack id> <rule ID>]` | The criterion enforces a `test` rule of a vendored pack. |
| prefix `ASSUMED:` instead of a tag | Neither source supports it. The orchestrator must confirm it with the user before planning (`meta/guides/orchestrate.md`, step 1). |

## Steps

1. Milestones: 2 to 5, from the brief's core jobs, in delivery order.
2. Candidate slices: one per core job, or fewer when two jobs share one
   entry point. Name each slice in kebab-case.
3. For each slice, draft:
   - title `Slice <name>: <core job>`;
   - description: why, quoting `product-brief`;
   - criteria in `GIVEN <state> WHEN <action> THEN <outcome>` form, each
     with its source tag;
   - label `slice:<name>`, its milestone.
4. One draft `Practice tests` with one criterion per `test` rule in
   `meta/practices/enforced.md`, tagged `[pack: ...]`, if there are any.
5. Gate: milestones, then one row per draft. Proposal = title, criteria
   count, `ASSUMED:` count. Why = the core job or pack. Rejected
   alternatives = slices merged or split, or `-`.
6. Create: `backlog milestone add "<name>"` for each milestone, then
   `backlog task create --draft "<title>" -d "<why>" --ac "<criterion>" ...
   -l slice:<name> -m "<milestone>" --plain` for each draft.

## Output

Milestones and drafts in Backlog.

Evidence for the criterion: `backlog milestone list --plain` and
`backlog draft list --plain`.

## Amend

Add drafts for new core jobs only. Never edit or delete existing tasks or
drafts; list the ones the change may affect in the task notes for the user.
