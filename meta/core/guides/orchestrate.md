# Orchestrator how-to

You run in the main thread. You own one Backlog task from intake to Done.
You never write application code. Workers are Haiku subagents that you launch
with the Agent tool: `test-writer` and `implementer`. Subagents cannot launch
subagents, so every step below is yours to run.

Backlog is the plan of record. The task holds the description, the
acceptance criteria (the cases), the plan, the notes, the final summary, and
the dependencies. Do not create plan files. Use the Backlog CLI for every
task change.

Commands come from `meta/product/stack.md`: install, migration, test (full
and targeted), check, and fix.

## 0. Preflight

1. Run `backlog instructions overview` once per conversation.
2. Read `meta/product/stack.md`. If the test command says TBD, stop and tell
   the user the stack is not set and init-factory must run first.
3. If `meta/product/overlays/orchestrate.md` exists, read it. It adds stack
   specifics to this guide. It never removes a stop rule.

## 1. Intake

If the user names an existing task (for example a promoted draft), read it
with `backlog task view <id> --plain` and keep its criteria; go to step 2.
Otherwise create the task, following `backlog instructions task-creation`:

- One task per independently shippable change. Use subtasks (`-p`) for parts
  of one feature.
- Description: why the work exists, in the user's words. Do not restate the
  criteria.
- Acceptance criteria are the cases. One per line, testable, numbered by
  position. Behaviour is written `GIVEN <state> WHEN <action> THEN <outcome>`.
- Labels: `module:<name>` for each module touched. Use `--dep` for ordering.

Source rule, for new and existing tasks: every criterion traces to the
user's words or carries a source tag from init-factory (`[brief: <field>]`,
`[pack: <id> <rule>]`, `[screen: <id>]`). A criterion with neither is
prefixed `ASSUMED:` and the user confirms it before step 3.

Screens, only when the Backlog doc `product-screens` exists and the task
adds a screen or changes what one shows or does:

1. Edit or add its mockup in `meta/product/screens/`, by the mockup rules in
   `.claude/skills/init-factory/phases/screens.md`. Never copy a mockup into
   the source root.
2. Show it as that phase's step 3 says. Ask about what it exposes, at most
   four questions, recommended option first.
3. After the user confirms it, update the screen's row in `product-screens`
   and `meta/product/screens/_about.md`. Criteria that follow from the
   screen carry `[screen: <id>]`. Until the user confirms, those criteria
   are `ASSUMED:`.
4. Commit the mockup and catalog with the task id. They count as plan files
   in step 7.

## 2. Activate

1. Read `backlog instructions task-execution`.
2. `backlog task edit TASK-n -s "In Progress" -a @claude`
3. Record the start: `backlog task edit TASK-n --append-notes "start: <git rev-parse HEAD>"`.

## 3. Research and plan

1. For each module and slice the task touches, run
   `python3 -I meta/core/tools/packet.py <module> [<slice>]`. A non-zero exit
   stops the run. Its notes name new modules and slices; that is expected.
2. Write the plan: `backlog task edit TASK-n --plan "..."`. Numbered steps,
   about ten at most. Each step names the slice folder, the exact files it
   creates or edits, the criterion numbers it covers, and the targeted test
   command. Follow the architecture in the packet: one slice per use case,
   tables only through the module's `store`, other modules only through
   their `index`. A new module's first step adds its migration and `store`.
3. Wiring: a slice users reach through a route, command, or job gets a
   final step that maps it in `app/`. Its allowlist is the `app/` file;
   its check is the full test command.
4. Special lines, after the steps, one per item:
   - `Retire: <test file> :: <test name> -> delete` or
     `-> rewrite as TASK-n#k`, when a criterion changes behaviour an
     existing test pins. A test not on the list is never edited or deleted.
   - `Change: <handler file> :: <old signature> -> <new signature>`, when a
     criterion changes an existing handler's inputs or outputs. Callers of
     that handler go into the allowlist of the step that covers it.
5. Ask the user before continuing when the plan makes a product or
   architecture decision that `backlog decision list --plain` does not
   cover: a new `shared/` addition, a module split or merge, a new
   dependency, an override of a default. A new module for a new area of the
   domain needs no decision; name it in the plan.

## 4. Test first

1. Launch `test-writer` with: the task id, the criteria verbatim with their
   numbers, the slice paths, the packet output, the `Retire:` and `Change:`
   lines, and the full test command.
2. Run the fix command on the files it wrote, so formatting never reaches
   the tidy step.
3. Catalogs: add each new module to `<source root>/_about.md` and each new
   slice to its module's `_about.md`, one line each, the name in backticks,
   with its purpose.
4. Run the full test command yourself. Gate: every new or rewritten test
   fails with an assertion or a not-implemented error; every other test
   passes. An import error, a collection error, a setup error, or a passing
   new test fails the gate.
5. On failure: relaunch `test-writer` once with the exact error text. If it
   fails again, stop and report.
6. Commit the tests, stubs, and catalogs locally (section 8).

## 5. Implement, one plan step at a time

For each step, in order:

1. Launch `implementer` with: the step text, the criteria it covers, the
   exact file allowlist, the targeted test command, the packet output, and
   the budget (two iterations inside the worker).
2. Read its `RESULT` line. `deviation` or `blocked`: stop and report. Do not
   retry deviations. `ok`: run the targeted command yourself to confirm.
3. Allowlist check: every path in `git status --porcelain` is on the step's
   allowlist. Any other path is a deviation: stop and report.
4. `backlog task edit TASK-n --append-notes "step <n>: <result>"`.
5. Commit the step locally (section 8).

A failing targeted test may get one relaunch with the error text. Gaps,
deviations, ambiguity, and out-of-allowlist changes get no retry.

Optional, only if the user asked for it: for a step that keeps failing after
one relaunch, run up to three implementers in separate git worktrees, keep
the first whose targeted tests pass, and discard the rest.

## 6. Tidy

Run the fix command, then the check command. The check covers lint, import
boundaries, structure and size caps, duplication, and dead code.

- Findings in source files of this plan: launch `implementer` once with the
  step `tidy: <the finding lines>`, the allowlist of those files (plus the
  module's `model` when duplication moves there), and the targeted test
  command.
- Findings in test files of this plan: launch `test-writer` once with
  `tidy: <the finding lines>` and those test files.
- Findings in files outside this plan: stop. Show them to the user, who
  either adds a tidy step for those files to this plan or ends the run with
  a follow-up task. The task cannot close while the check fails.
- Still failing after one tidy run: stop and report.

Behaviour does not change in a tidy run; the targeted tests stay green.
Commit the tidy run locally.

## 7. Verify

1. Run the full test command once. Everything passes.
2. Run the check command once. It exits 0.
3. Compare `git diff --name-only <start>..HEAD` with the plan's files, the
   catalogs, the screen files from intake, and the test files. Any other file is a deviation: stop and ask
   the user.
4. If `meta/` or `.claude/` changed, run `meta/core/tools/check-harness.sh`.

## 8. Commit and push

- Commit after the test-first step, after each passing step, and after the
  tidy run. Small commits, one coherent change each, imperative message with
  the task id.
- Push once, after step 7 passes: `git push origin main`. `main` on the
  remote stays green. Never force-push. If the push fails, report the
  error; do not work around it.

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
- A change falls outside the step's allowlist or the plan's files.
- A check finding falls outside the plan's files.
- A product or architecture decision is needed.
