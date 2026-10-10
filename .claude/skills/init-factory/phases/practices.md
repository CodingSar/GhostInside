# Phase: practices

Goal: one current, approved pack per facet, vendored and locked, with every
enforceable rule compiled into a tool, and new packs offered upstream.

Pack format and index: the central repo's README
(`.cache/practices/README.md` after fetch). Tool: `meta/tools/practices.py`.

## Steps

1. Facets = the ratified domain and concern facets plus the stack facets
   from the task notes. `python3 -I meta/tools/practices.py fetch`, then
   `status <all ids>`.
2. hit: use the central pack.
3. stale (researched more than 7 days ago): delta check. One research
   subagent: "What changed for <facet> since <researched date> that would
   change these rules? Material changes only, with sources." Attach the pack.
   - Material change: full research as for a miss.
   - None: copy the pack to `.cache/init/packs/<id>.md` and set `researched`
     to today. It goes upstream as a refresh.
4. miss: research, tiered.
   - `domain/` and `concern/`: run the deep-research skill for the facet,
     then distill its report into a pack, tier `deep`.
   - `lang/`, `framework/`, `datastore/`: one `general-purpose` subagent with
     the prompt below, tier `standard`.
   Write each draft to `.cache/init/packs/<id>.md`.
5. `python3 -I meta/tools/practices.py check .cache/init/packs/<id>.md` for
   every draft (the path must end in `<id>.md`). Fix format errors once. Still
   failing: stop.
6. Read all packs together. Remove duplicates across packs. Rules that
   contradict each other go to the gate as a question.
7. Gate: one row per pack. Proposal = origin (central, refreshed, new), rule
   count, MUST/SHOULD split, Enforce split, and the three rules most likely to
   surprise the user. The user may drop packs or rules.
8. Vendor the exact ratified set:
   `python3 -I meta/tools/practices.py vendor <central ids> <.cache/init/packs/... files>`,
   then `verify`.
9. Compile `meta/practices/enforced.md`:
   - `lint:` rules: enable the named rule in the linter's config file.
   - `check-cmd:` rules: add the command to `scripts/practice-checks.sh`
     (exits non-zero on any failure), and make the registry lint command run
     it after the linter.
   - `test` rules: listed for the seed phase, which turns them into criteria.
   A rule the stack's tools cannot enforce goes back to the gate as a
   `review` rule.
10. Upstream: for each refreshed or new pack,
   `python3 -I meta/tools/practices.py propose .cache/init/packs/<id>.md`.
   Record each PR URL in the task notes. If `gh` is not logged in, record
   `PR not opened: <id>` and continue.

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

`meta/practices/packs/`, `practices.lock`, `review.md`, `enforced.md`, the
linter config, `scripts/practice-checks.sh` if any check-cmd rules, PR URLs
in notes.

Evidence for the criterion: `verify` output and the PR URLs (or the
not-opened notes).

## Amend

Run steps 1 to 10 for added facets and for packs now stale. Vendor the full
new set: `vendor` drops any pack not named, so removed facets disappear.
