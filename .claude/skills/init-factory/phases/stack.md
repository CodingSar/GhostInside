# Phase: stack and architecture

Goal: every value in `meta/product/stack.md` set, the datastore and
architecture defaults kept or superseded on purpose, the project scaffolded
so its tools run, the check command wired, and the stack facets known.

## Items to propose

One item per row of `meta/product/stack.md`, plus the static checks and the
architecture:

| Item | Default |
|---|---|
| language and version | none; from the brief's language preference and deploy target |
| framework | none unless the deploy target or core jobs call for one |
| package manager | the language's mainstream one |
| install command | from the package manager |
| source root, source extensions, test file pattern | `src`, the language's extensions, the runner's test file naming as a regex |
| name case | `kebab`; `snake` where the language imports folders by name (Python, Rust); `pascal` or `camel` where its conventions require |
| entry file stems | `index, handler`; the language's case where the file name must match a type (`Index, Handler` in Java, Kotlin, C#) |
| datastore | PostgreSQL (`HD-2`) |
| connection variable | `DATABASE_URL` |
| migration command | a mainstream migration tool for the stack; `none` without a datastore |
| test runner, full and targeted test commands | the language's mainstream runner |
| linter and formatter | the language's mainstream ones |
| import boundary checker | a tool that enforces the architecture's import rules 1 to 4 (for example import-linter, dependency-cruiser, depguard, eslint boundaries) |
| duplication checker | jscpd, or a stack-native one; configured to ignore test files |
| dead code checker | a stack-native one (for example vulture, knip, deadcode) |
| check command | `scripts/check.sh` |
| fix command | the formatter and the linter in fix mode, one command |
| dependencies approved | the smallest set the skeleton needs |
| architecture | modules of slices (`HD-11`) |

## Rules

1. Defaults hold unless the brief gives a reason. Examples of a reason: no
   stored data (CLI tool) means no PostgreSQL; an embedded target means no
   server datastore. A reason is a brief field, quoted in Why.
2. Replacing a default is a superseding decision (`HD-6`). Write the
   override in `meta/product/` under the default's file name
   (`architecture.md` or `persistence.md`), with the same sections as the
   default. Never edit `meta/core/defaults/`. Guides read the datastore from
   `meta/product/stack.md`, so a persistence override needs no other change.
   An architecture override may change rules, names, and caps, but must keep
   the skeleton `packet.py`, `structure.py`, and the guides rely on:
   `<source root>/modules/<module>/slices/<slice>/`, the entry file stems,
   and the `_about.md` catalogs. A different skeleton is a harness change:
   stop and tell the user it belongs in the template.
3. Versions move fast. Check current stable versions with WebSearch and the
   official release pages (WebFetch) for the language, framework, runner,
   linter, checkers, and migration tool. Never take a version from memory.
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
2. Overrides written as rule 2 says.
3. Decisions and `init-decisions` rows as `SKILL.md` says: one stack
   decision, one per superseded default.
4. Scaffold, so the tools of later phases run: the package manifest with the
   approved dependencies, the lockfile from the install command, the linter,
   formatter, boundary, duplication, and dead code configs, the test runner
   config, and the source root with `_about.md` (an empty module table),
   `shared/`, `modules/`, and the `app/` entry file that starts and exits,
   so every checker has input. No other product code. The test runner config
   must collect identically named test files in different slices (for
   pytest, `--import-mode=importlib`).
5. `scripts/check.sh`: runs, in order and stopping at the first failure, the
   linter, the formatter check, the boundary checker,
   `python3 -I meta/core/tools/structure.py --root <source root> --ext <extensions> --test '<test file pattern>' --case <name case> --index <index stem> --handler <handler stem>`
   (caps from the architecture, passed as `--max-*` flags if an override changed them),
   the duplication checker, and the dead code checker. Exits non-zero on any
   failure. The practices phase appends practice checks.
6. Run the install command and the check command once; both must exit 0.
7. Task note: `stack facets: lang/<x>, framework/<y>, datastore/<z>` (omit
   kinds that do not apply).

Evidence for the criterion: `! grep -q TBD meta/product/stack.md` exits 0,
the install and check commands exit 0, and the decision ids.

## Amend

Revisit only items the changed brief fields touch. A changed item is a new
superseding decision; never edit an old decision. Update the scaffold and
`scripts/check.sh` to match.
