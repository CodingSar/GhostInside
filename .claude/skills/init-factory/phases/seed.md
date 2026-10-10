# Phase: seed

Goal: a starting backlog the user can promote from. Drafts, not tasks: the
orchestrator owns real tasks (`meta/guides/orchestrate.md`).

## Steps

1. Milestones: 2 to 5, from the brief's core jobs, in delivery order.
2. Candidate slices: one per core job, or fewer when two jobs share one
   entry point. Name each slice in kebab-case.
3. For each slice, draft:
   - title `Slice <name>: <core job>`;
   - description: why, quoting `product-brief`;
   - criteria in `GIVEN <state> WHEN <action> THEN <outcome>` form, each
     traced to a brief field or prefixed `ASSUMED:`;
   - label `slice:<name>`, its milestone.
4. One draft `Practice tests` with one criterion per `test` rule in
   `meta/practices/enforced.md`, if there are any.
5. Gate: milestones, then one row per draft with its criteria count and
   `ASSUMED:` count.
6. Create: `backlog milestone add "<name>"` for each milestone, then
   `backlog task create --draft "<title>" -d "<why>" --ac "<criterion>" ...
   -l slice:<name> -m "<milestone>"` for each draft.

## Output

Milestones and drafts in Backlog.

Evidence for the criterion: `backlog draft list --plain`.

## Amend

Add drafts for new core jobs only. Never edit or delete existing tasks or
drafts; list the ones the change may affect in the task notes for the user.
