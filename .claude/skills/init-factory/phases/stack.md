# Phase: stack and architecture

Goal: every value in `meta/registry/runner.md` set, the datastore and
architecture defaults kept or superseded on purpose, and the stack facets
known.

## Items to propose

| Item | Default |
|---|---|
| language and version | none; from the brief's language preference and deploy target |
| package manager | the language's mainstream one |
| framework | none unless the deploy target or core jobs call for one |
| datastore | PostgreSQL (`decision-2`) |
| architecture | vertical slices (`decision-1`) |
| source root and file extensions | `src/` and the language's |
| test runner | the language's mainstream one |
| test command (full) | from the runner |
| test command (targeted, takes a path) | from the runner |
| lint command | the language's mainstream linter and formatter check |
| connection variable | `DATABASE_URL` |
| dependencies approved | the smallest set the skeleton needs |

## Rules

1. Defaults hold unless the brief gives a reason. Examples of a reason: no
   stored data (CLI tool) means no PostgreSQL; an embedded target means no
   server datastore; a single-screen tool may not fit slices. A reason is a
   brief field, quoted in Why.
2. Replacing a default is a superseding decision (`decision-6`). Then update
   the file that holds the default: `meta/registry/persistence.md` or
   `meta/architecture/vertical-slice.md` (rewrite it for the new style, keep
   its sections: Unit, Layout, Rules, Why).
   The core test guide assumes a real PostgreSQL; when the datastore is
   superseded, the `test.md` overlay (provision phase) names the replacement
   and how tests reach it.
3. Versions move fast. Check current stable versions on the web for the
   language, framework, runner, and linter. Never take a version from memory.
4. When two options are close, launch one research subagent
   (`general-purpose`) to compare them for this brief, with sources. Put the
   loser in Rejected alternatives.
5. Honor the brief's language preference unless it conflicts with a hard
   requirement. Then ask.

## Gate

One row per item. Rows that keep a default say so.

## Output

1. `meta/registry/runner.md`: every value set. Replace the Status line with
   `Status: set by init-factory, <init task id>.` No TBD may remain.
2. Superseded default files rewritten as rule 2 says.
3. Decisions and `init-decisions` rows as `SKILL.md` describes: one per
   non-default choice and one for the stack as a whole.
4. Task note: `stack facets: lang/<x>, framework/<y>, datastore/<z>` (omit
   kinds that do not apply).

Evidence for the criterion: `grep -c TBD meta/registry/runner.md` prints 0,
and the decision ids.

## Amend

Revisit only items the changed brief fields touch. A changed item is a new
superseding decision; never edit an old decision.
