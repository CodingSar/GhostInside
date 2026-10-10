# Phase: seed

Goal: a starting backlog the user can promote from. Drafts, not tasks: the
orchestrator owns real tasks (`meta/core/guides/orchestrate.md`).

Read `backlog instructions task-creation` first.

Gate: shared with the provision phase (`SKILL.md`). The drafts below are
proposed in that gate; after it, this phase only creates them.

## Source tags

Every criterion ends with exactly one source tag:

| Tag | Use |
|---|---|
| `[brief: <field>]` | The criterion follows from that `product-brief` field. |
| `[pack: <pack id> <rule ID>]` | The criterion enforces a `test` rule of a vendored pack. |
| `[screen: <screen id>]` | The criterion follows from that screen's row in `product-screens` (an action, a data view, or a state). |
| prefix `ASSUMED:` instead of a tag | Neither source supports it. The orchestrator must confirm it with the user before planning (`meta/core/guides/orchestrate.md`, step 1). |

## Steps

1. Milestones: 2 to 5, from the brief's core jobs, in delivery order.
2. Modules: one per area of the domain the core jobs work in, as the
   architecture defines (`HD-11`). Name each in the stack's name case.
3. Slices: one per use case (one command or one query) of a core job. Name
   each in the stack's name case. One draft per slice:
   - title `<module>/<slice>: <use case>`;
   - description: why, quoting `product-brief`;
   - criteria in `GIVEN <state> WHEN <action> THEN <outcome>` form, each
     with its source tag;
   - label `module:<module>`, its milestone.
   With a `product-screens` doc, every action and data view it lists maps
   to at least one draft; a slice a screen reaches cites it with
   `[screen: <id>]`.
4. One draft `Practice tests` with one criterion per `test` rule in
   `meta/product/practices/enforced.md`, tagged `[pack: ...]`, if there are any.
5. Gate rows (shared gate): milestones, modules, then one row per draft.
   Proposal = title, criteria count, `ASSUMED:` count. Why = the core job,
   screen, or pack. A screen action no draft covers is its own row, marked
   `unmapped`, until a draft covers it. Rejected alternatives = modules or slices merged or split, or `-`.
6. Create: `backlog milestone add "<name>"` for each milestone, then
   `backlog task create --draft "<title>" -d "<why>" --ac "<criterion>" ...
   -l module:<module> -m "<milestone>" --plain` for each draft.

## Output

Milestones and drafts in Backlog.

Evidence for the criterion: `backlog milestone list --plain` and
`backlog draft list --plain`.

## Amend

Add drafts for new core jobs and for screens the screens phase changed only. Never edit or delete existing tasks or
drafts; list the ones the change may affect in the task notes for the user.
