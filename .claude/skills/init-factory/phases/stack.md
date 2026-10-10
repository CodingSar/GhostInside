# Phase: stack and architecture

Goal: every value in `meta/product/stack.md` set, the datastore and
architecture defaults kept or superseded on purpose, the project scaffolded
so its tools run, and the stack facets known.

## Items to propose

One item per row of `meta/product/stack.md`, plus architecture:

| Item | Default |
|---|---|
| language and version | none; from the brief's language preference and deploy target |
| framework | none unless the deploy target or core jobs call for one |
| package manager | the language's mainstream one |
| install command | from the package manager |
| source root and file extensions | `src/` and the language's |
| datastore | PostgreSQL (`HD-2`) |
| connection variable | `DATABASE_URL` |
| migration command | a mainstream migration tool for the stack; `none` without a datastore |
| test runner, full and targeted test commands | the language's mainstream runner |
| lint command | the language's mainstream linter and formatter check |
| dependencies approved | the smallest set the skeleton needs |
| architecture | vertical slices (`HD-1`) |

## Rules

1. Defaults hold unless the brief gives a reason. Examples of a reason: no
   stored data (CLI tool) means no PostgreSQL; an embedded target means no
   server datastore; a single-screen tool may not fit slices. A reason is a
   brief field, quoted in Why.
2. Replacing a default is a superseding decision (`HD-6`). Then update
   the file that holds the default: `meta/core/defaults/persistence.md` or
   `meta/core/defaults/architecture.md`. Rewrite it for the new choice and
   keep its existing sections. The core test guide assumes a real
   PostgreSQL; when the datastore is superseded, the `test.md` overlay
   (provision phase) names the replacement and how tests reach it.
3. Versions move fast. Check current stable versions with WebSearch and the
   official release pages (WebFetch) for the language, framework, runner,
   linter, and migration tool. Never take a version from memory.
4. When two options are close, launch one research subagent
   (`general-purpose`) to compare them for this brief, with sources. Put the
   loser in Rejected alternatives.
5. Honor the brief's language preference unless it conflicts with a hard
   requirement. Then ask.

## Gate

One row per item. Proposal = the value with its version. Why = the brief
field or default. Rejected alternatives = the options you weighed. Rows that
keep a default say so.

## Output

1. `meta/product/stack.md`: every row set. Replace the Status line with
   `Status: set by init-factory, <init task id>.` No TBD may remain.
2. Superseded default files rewritten as rule 2 says.
3. Decisions and `init-decisions` rows as `SKILL.md` says (every stack row).
4. Scaffold, so the tools of later phases run: the package manifest with the
   approved dependencies, the lockfile from the install command, the linter
   config, the test runner config, and the source root folder. No product
   code. Run the install command once; it must exit 0.
5. Task note: `stack facets: lang/<x>, framework/<y>, datastore/<z>` (omit
   kinds that do not apply).

Evidence for the criterion: `! grep -q TBD meta/product/stack.md` exits 0,
the install command exits 0, and the decision ids.

## Amend

Revisit only items the changed brief fields touch. A changed item is a new
superseding decision; never edit an old decision. Update the scaffold to
match.
