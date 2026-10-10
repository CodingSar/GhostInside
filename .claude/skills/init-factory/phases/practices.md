# Phase: practices

Goal: one current, approved pack per facet, vendored and locked, with every
enforceable rule compiled into a tool, and new packs offered upstream.

Pack format and index: the central repo's README
(`.cache/practices/README.md` after fetch). Tool: `meta/core/tools/practices.py`.

## Steps

1. Facets = the ratified domain and concern facets plus the stack facets
   from the task notes. `python3 -I meta/core/tools/practices.py fetch`, then
   `status <all ids>`. If `fetch` fails, the central repo is unreachable:
   note `central unreachable: <error>`, treat every facet as a miss, skip
   step 11, and continue.
2. hit: use the central pack.
3. stale (researched more than 7 days ago): delta check. One research
   subagent: "What changed for <facet> since <researched date> that would
   change these rules? Material changes only, with sources." Attach the pack.
   - Material change: full research as for a miss.
   - None: copy the pack to `.cache/init/packs/<id>.md` and set `researched`
     to today. It goes upstream as a refresh.
4. miss: research, tiered. Create `.cache/init/packs/<kind>/` first.
   - `domain/` and `concern/`: run the `anthropic-skills:deep-research` skill
     for the facet, then distill its report into a pack, tier `deep`. If that
     skill is not available, use one `general-purpose` subagent with the
     prompt below, ask it for at least ten independent sources, and keep tier
     `deep`.
   - `lang/`, `framework/`, `datastore/`: one `general-purpose` subagent with
     the prompt below, tier `standard`.
   Write each draft to `.cache/init/packs/<id>.md`.
5. `python3 -I meta/core/tools/practices.py check .cache/init/packs/<id>.md` for
   every draft (the path must end in `<id>.md`). Fix format errors once. Still
   failing: stop.
6. Read all packs together. Remove duplicates across new and refreshed packs.
   Rules that contradict each other go to the gate as a question.
7. Plan enforcement for every non-`review` rule:
   - `lint:` the linter rule to enable. A rule named for a tool the stack
     does not use: map it to the stack linter's equivalent rule; with no
     equivalent, it is enforced by review through the `implement.md` overlay
     (provision phase).
   - `check-cmd:` the command, run by `scripts/practice-checks.sh`. The
     registry lint command becomes `<linter command> && scripts/practice-checks.sh`.
   - `test`: becomes a criterion in the seed phase.
8. Gate: one row per pack, plus one row for the new lint command if step 7
   changes it. Pack row: Proposal = origin (central, refreshed, new), rule
   count, MUST/SHOULD split, Enforce split, rules mapped to review, and the
   three rules most likely to surprise the user. Why = the facet. Rejected
   alternatives = dropped rules or `-`. The user may drop packs or rules;
   dropping a rule of a central pack makes the pack a local copy in
   `.cache/init/packs/`. Propose that copy upstream only if the user says
   the rule is wrong in general, not just for this product.
9. Vendor the exact ratified set:
   `python3 -I meta/core/tools/practices.py vendor <central ids> <.cache/init/packs/... files>`,
   then `verify`. The lock records `central` or `local`; refreshed and new
   packs are both `local` until their PR merges.
10. Compile the plan from step 7. `vendor` regenerates
    `meta/product/practices/enforced.md` and `review.md`; never edit them. Edit the
    linter config, write `scripts/practice-checks.sh` (exits non-zero on any
    failure) if there are check-cmd rules, update the lint command in
    `meta/product/stack.md`, and run it once: it must exit 0 on the
    scaffold. Note `review via overlay: <rule ids>` for the provision phase.
11. Upstream: for each refreshed or new pack (and each local copy the user
    chose to propose),
    `python3 -I meta/core/tools/practices.py propose .cache/init/packs/<id>.md`.
    Exit 0: record the PR URL. Exit 3: record its `PR not opened` line, which
    names the pushed branch for a manual PR later. Rerunning `propose` with
    the same file is safe.

## Research prompt (standard tier)

```
Write a best-practice pack for <id> for this product: <one-liner, deploy
target, scale from product-brief>. Stack: <ratified stack>.
Return only the pack file, in exactly this format: <paste the README's pack
file section>.
- 10 to 30 rules. Each one line, imperative, testable or reviewable.
- Every rule has a source URL. Prefer official docs, then standards, then
  well-known maintainers. Check that each URL is current.
- Enforce: name a lint rule (tool and rule id) when the stack's linter has
  one; a check command when a command can prove it; test when only a test
  can; review otherwise.
- No rule that only restates the language. No style rule the formatter
  already enforces.
```

## Output

`meta/product/practices/packs/`, `practices.lock`, `review.md`, `enforced.md`, the
linter config, `scripts/practice-checks.sh` if any check-cmd rules, the lint
command in the registry, PR URLs in notes.

Evidence for the criterion: `verify` output, the lint command exit 0, and
the PR URLs (or the `PR not opened` and `central unreachable` notes).

## Amend

Run steps 1 to 11 for added facets and for packs now stale. Then vendor the
full new set: every kept pack (central ids and local files) plus the new
ones. `vendor` drops any pack not named, so removed facets disappear and a
forgotten kept pack disappears too. Compare with `practices.lock` before
running it.
