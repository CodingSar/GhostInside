# Orchestrator how-to

You run in the main thread. You own one Backlog task from intake to Done.
You never write application code. Workers are Haiku subagents that you launch
with the Agent tool: `test-writer` and `implementer`. Subagents cannot launch
subagents, so every step below is yours to run.

Backlog is the plan of record. The task holds the description, the
acceptance criteria (the cases), the plan, the notes, the final summary, and
the dependencies. Do not create plan files. Use the Backlog CLI for every
task change; read `backlog instructions task-creation`, `task-execution`, and
`task-finalization` at the step that names them.

Commands come from `meta/product/stack.md`: install, migration, test (full
and targeted), and check.

## 0. Preflight

1. Run `backlog instructions overview` once per conversation.
2. Read `meta/product/stack.md`. If the test command says TBD, stop and tell
   the user the stack is not set and init-factory must run first.
3. If `meta/product/overlays/orchestrate.md` exists, read it. It adds stack
   specifics to this guide. It never removes a stop rule.

## 1. Intake: create the task

Follow `backlog instructions task-creation`.

- One task per independently shippable change. Use subtasks (`-p`) for parts
  of one feature.
- Description: why the work exists, in the user's words. Do not restate the
  criteria.
- Acceptance criteria are the cases. One per line, testable, numbered by
  position. Behaviour is written `GIVEN <state> WHEN <action> THEN <outcome>`.
- Source rule: every criterion traces to the user's request. If you cannot
  point to the user's words for it, prefix it `ASSUMED:` and ask the user to
  confirm before step 3.
- Labels: `module:<name>` for each module touched. Use `--dep` for ordering.

## 2. Activate

`backlog task edit TASK-n -s "In Progress" -a @claude`

## 3. Research and plan

1. For each module and slice the task touches, run
   `python3 -I meta/core/tools/packet.py <module> [<slice>]`. A non-zero exit
   stops the run. Its notes name new modules and slices; that is expected.
2. Write the plan: `backlog task edit TASK-n --plan "..."`. Numbered steps,
   about ten at most. Each step names the slice folder, the exact files it
   creates or edits, the criterion numbers it covers, and the targeted test
   command. Follow the architecture in the packet: one slice per use case,
   tables only through the module's `store`, other modules only through
   their `index`.
3. Retire list: when a criterion changes behaviour that existing tests pin,
   add a `Retire:` line per test: file, test name, the criterion that
   replaces it. A test not on the list is never edited or deleted.
4. Ask the user before continuing when the plan makes a product or
   architecture decision that `backlog decision list --plain` does not
   cover: a new `shared/` addition, a module split or merge, a new
   dependency, an override of a default. A new module for a new area of the
   domain needs no decision; name it in the plan.

## 4. Test first

1. Launch `test-writer` with: the task id, the criteria verbatim with their
   numbers, the slice paths, the packet output, the retire list, and the full
   test command.
2. Catalogs: add each new module to `<source root>/_about.md` and each new
   slice to its module's `_about.md`, one line each, with its purpose.
3. Run the full test command yourself. Gate: every new or rewritten test
   fails with an assertion or a not-implemented error; every other test
   passes. An import error, a collection error, or a passing new test fails
   the gate.
4. On failure: relaunch `test-writer` once with the exact error text. If it
   fails again, stop and report.

## 5. Implement, one plan step at a time

For each step, in order:

1. Launch `implementer` with: the step text, the criteria it covers, the
   exact file allowlist, the targeted test command, the packet output, and
   the budget (two iterations inside the worker).
2. Read its `RESULT` line. `ok`: run the targeted command yourself to
   confirm. `deviation` or `blocked`: stop and report. Do not retry
   deviations.
3. `backlog task edit TASK-n --append-notes "step <n>: <result>"`.
4. Commit and push the step (section 8).

A failing targeted test may get one relaunch with the error text. Gaps,
deviations, ambiguity, and out-of-allowlist changes get no retry.

Optional, only if the user asked for it: for a step that keeps failing after
one relaunch, run up to three implementers in separate git worktrees, keep
the first whose targeted tests pass, and discard the rest.

## 6. Tidy

Run the check command. It covers lint, import boundaries, structure and size
caps, duplication, and dead code.

- Findings in files of this plan: launch `implementer` once with the step
  `tidy: <the finding lines>`, the allowlist of those files (plus the
  module's `model` when duplication moves there), and the targeted test
  command. Behaviour must not change; the tests stay as they are.
- Findings in files outside this plan: do not fix them here. Report them and
  ask the user whether to create a follow-up task.
- Still failing after one tidy run: stop and report.

## 7. Verify

1. Run the full test command once. Everything passes.
2. Run the check command once. It exits 0.
3. Compare `git diff --name-only` with the plan's files and the catalogs.
   Any other file is a deviation: stop and ask the user.
4. If `meta/` or `.claude/` changed, run `meta/core/tools/check-harness.sh`.

## 8. Commit and push

- Commit after each passing step and after the tidy run. Small commits, one
  coherent change each, imperative message with the task id.
- Then `git push origin main`. Never force-push. If the push fails, report
  the error; do not work around it.

## 9. Close out

Follow `backlog instructions task-finalization`.

1. Check a criterion only with evidence from this run: `--check-ac <n>`.
   Evidence is test output, not code presence.
2. `--final-summary "..."`: what changed, tests retired, how it was verified.
3. Set the terminal status: `-s Done`.
4. Report to the user: task id, each criterion with its evidence, any
   `ASSUMED:` criteria still open, deviations, and follow-ups.

## Stop rules

Stop and report instead of looping on:

- The test command is TBD, or `packet.py` exits non-zero.
- A criterion marked `ASSUMED:` is still unconfirmed.
- A worker returns `deviation` or `blocked`.
- A retry budget is spent.
- A change falls outside the plan's files.
- A product or architecture decision is needed.
