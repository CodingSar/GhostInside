# Orchestrator how-to

You run in the main thread. You own one Backlog task from intake to Done.
You never write application code. Workers are Haiku subagents that you launch
with the Agent tool. Subagents cannot launch subagents, so every step below is
yours to run.

Backlog is the plan of record. The task holds the description, the
acceptance criteria (the cases), the plan, the notes, the final summary, and
the dependencies. Do not create plan files.

Use the Backlog CLI for every task change. Read `backlog instructions
task-creation`, `task-execution`, and `task-finalization` at the step that
names them. Do not edit Backlog markdown files.

## 0. Preflight

1. Run `backlog instructions overview` once per conversation.
2. Read `meta/registry/runner.md`. If the test command says TBD, stop and tell
   the user the stack is not set and init-factory must run first. Do not
   invent a runner.
3. Read `meta/_about.md` to know what the catalog holds.

## 1. Intake: create the task

Follow `backlog instructions task-creation`.

- One task per independently shippable change. Use subtasks (`-p`) for parts
  of one feature.
- Description: why the work exists, in the user's words. Do not restate the
  criteria.
- Acceptance criteria are the cases. One criterion per line. Testable. When
  it describes behaviour, write it as `GIVEN <state> WHEN <action> THEN <outcome>`.
  Criteria are numbered by position: #1, #2, and so on.
- Source rule: every criterion must trace to the user's request. If you cannot
  point to the user's words for it, prefix it with `ASSUMED:` and ask the user
  to confirm before step 3. Do not invent rules.
- Labels: `slice:<name>` for each slice touched. Use `--dep` for ordering.
- References: add `--ref meta/architecture/vertical-slice.md` and any registry
  file that applies.

## 2. Activate

`backlog task edit TASK-n -s "In Progress" -a @claude`

## 3. Research and plan

1. Launch `searcher` (Agent tool). Prompt it with: the topics
   `architecture`, `registry`, `practices:testing`, `slice:<name>`, and the
   slice path. Read only its final `RESULT` line and the packet's gap list.
   Any gap stops the run: report it to the user.
2. Write the plan: `backlog task edit TASK-n --plan "..."`. Numbered steps.
   Each step names: the slice folder, the exact files it creates or edits,
   the criterion numbers it covers, and the targeted test command. Keep it
   under about ten steps.
3. If the plan makes a product or architecture decision that is not already
   in `backlog decision list --plain`, ask the user before continuing.

## 4. Test first

1. Launch `test-writer` with: the task id, the criteria verbatim with their
   numbers, the slice path, the testing packet text, and the test command.
2. Run the test command yourself. Gate: every new test fails with an
   assertion or a not-implemented error. An import error, a collection error,
   or any passing new test is a failure.
3. On failure: relaunch `test-writer` once with the exact error text. If it
   fails again, stop and report.

## 5. Implement, one plan step at a time

For each step, in order:

1. Launch `implementer` with: the step text, the criteria it covers, the
   exact file allowlist, the targeted test command, and the budget (two
   iterations inside the worker).
2. Read its `RESULT` line. `ok`: run the targeted command yourself to confirm.
   `deviation` or `blocked`: stop and report. Do not retry deviations.
3. Record progress: `backlog task edit TASK-n --append-notes "step <n>: <result>"`.
4. Commit and push the step (see section 7).

Retries are for probabilistic misses only. A failing targeted test may get one
relaunch with the error text. Gaps, deviations, ambiguity, and out-of-allowlist
changes get no retry.

Optional, for a single step that keeps failing after one relaunch: run up to
three implementers in separate git worktrees, keep the first whose targeted
tests pass, and discard the rest. Only use this if the user has asked for it.

## 6. Verify

1. Run the full test command once. Everything must pass.
2. Compare `git diff --name-only` with the files listed in the plan. Any file
   outside the plan is a deviation: stop and ask the user.
3. If `meta/` or `.claude/` changed, run `meta/tools/check-harness.sh`.
4. Record modified files for groma: `backlog task edit TASK-n --modified-file <path>`
   for each changed path. Follow `groma agent-instructions backlog`.

## 7. Commit and push

- Commit after each passing step and after harness changes. Small commits,
  one coherent change each. Message in the imperative, with the task id.
- Then `git push origin main`. Never force-push.
- If the push fails, report the error. Do not work around it.

## 8. Close out

Follow `backlog instructions task-finalization`.

1. Check a criterion only with evidence from this run: `--check-ac <n>`.
   Evidence is test output, not code presence.
2. `--final-summary "..."` with what changed and how it was verified.
3. Set the terminal status: `-s Done`.
4. Report to the user: task id, each criterion with its evidence, any
   `ASSUMED:` criteria still open, and any deviations.

## Stop rules

Stop and report instead of looping on:

- The test command is TBD.
- A criterion marked `ASSUMED:` is still unconfirmed.
- The searcher reports gaps.
- A worker returns `deviation` or `blocked`.
- A retry budget is spent.
- A change falls outside the plan's files.
- A product or architecture decision is needed.
