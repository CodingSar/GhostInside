# Planner how-to

Goal: the task's plan, written into its `plan` field in the exact format
below, so `loop.py` can run each step with its own file allowlist and test
command. You write the plan, not code or tests.

## 1. Read

1. The task: `backlog task view <id> --plain`.
2. `meta/product/stack.md` for the test commands and the source root.
3. For each module and slice the task touches, the packet:
   `python3 -I meta/core/tools/packet.py <module> [<slice>]`. A non-zero
   exit: `RETURN blocked <its error>`. Its notes name new modules and
   slices; that is expected.

## 2. Shape the steps

- Numbered steps, about ten at most. Each covers one or more criteria.
- Follow the architecture in the packet: one slice per use case, tables only
  through the module's `store`, other modules only through their `index`. A
  new module's first step adds its migration and `store`.
- Each step lists the exact files it creates or edits. Those files are its
  allowlist: the implementer may change nothing else.
- Wiring: a slice users reach through a route, command, or job gets a final
  step that maps it in `app/`. Its files are the `app/` file, its criteria
  `none`, its test the full test command.
- Every criterion is covered by some step.

## 3. Format

Write it with `backlog task edit <id> --plan $'...'` (real newlines):

```
1. <what the step does>
   Files: <path>, <path>
   Criteria: <n>, <n>
   Test: <targeted test command> <path>
2. ...
Retire: <test file> :: <test name> -> delete
Retire: <test file> :: <test name> -> rewrite as TASK-<n>#<k>
Change: <handler file> :: <old signature> -> <new signature>
Catalog: <source root>/modules/<module>/_about.md :: - `<slice>`: <purpose>
```

- `Test:` is the stack's targeted command followed by a path, or the full
  test command. Nothing else: no `;`, `&&`, `|`, or redirects.
- Files never under `meta/`, `.claude/`, or `backlog/`, and never test files:
  the test-writer owns tests; reach them with `Retire:` and `Change:` lines.
- `Retire:` when a criterion changes behaviour an existing test pins. A test
  not listed is never edited or deleted.
- `Change:` when a criterion changes an existing handler's inputs or
  outputs. Put that handler's callers in the step that covers it.
- `Catalog:` one line per new module (in `<source root>/_about.md`) and per
  new slice (in its module's `_about.md`), the name in backticks, with its
  purpose.

If `loop.py` rejects the plan, your next frame lists every problem. Fix them
all with one `--plan`.

## 4. Decisions and facts

Ask the user before planning a product or architecture decision that
`backlog decision list --plain` does not cover: a new `shared/` addition, a
module split or merge, a new dependency, an override of a default. A new
module for a new area of the domain needs no decision; name it in the plan.
Asking and research work as in `meta/core/guides/intake.md` section 5:
write your frame's ask or call file and return `RETURN ask` or
`RETURN call researcher`.

## 5. Output

Your output file: `plan: <n> steps`, then one line per step with its
criteria. Final line: `RETURN ok <output file>`.

## 6. Forbidden

- Code, tests, commits, or edits to any file but the task's plan (through
  the CLI) and your frame's output, call, and ask files.
- Steps that change criteria. Criteria belong to intake.
