# Intake how-to

Goal: one Backlog task whose acceptance criteria are the cases, each traced
to a source, none left `ASSUMED:` when you finish. You write criteria, not
code, tests, or plans.

## 1. Read

Your frame names either a request file (the user's words, verbatim) or an
existing task id. For an existing task, read it with
`backlog task view <id> --plain` and keep its criteria; go to section 3.
Use `backlog task create --help` and `backlog task edit --help` for flags.

## 2. Create the task

- One task per independently shippable change. Parts of one feature are
  subtasks (`-p <parent id>`).
- Description: why the work exists, in the user's words. Do not restate the
  criteria.
- Criteria are the cases: one per `--ac`, testable, behaviour written
  `GIVEN <state> WHEN <action> THEN <outcome>`.
- Labels: `module:<name>` for each module touched (`-l`). Ordering with
  `--dep`.

## 3. Source rule

Every criterion traces to the user's words or carries a source tag from
init-factory: `[brief: <field>]`, `[pack: <id> <rule>]`, `[screen: <id>]`.
A criterion with neither is prefixed `ASSUMED:`.

Before you finish, the user confirms every `ASSUMED:` criterion (section 5).
After the answer, rewrite the criteria with
`backlog task edit <id> --acceptance-criteria "<1>" --acceptance-criteria "<2>" ...`
(all of them, in order): drop the prefix from confirmed ones, change or
remove the rest as the user said.

## 4. Screens

Only when the Backlog doc `product-screens` exists and the task adds a
screen or changes what one shows or does:

1. Edit or add its mockup in `meta/product/screens/`, by the mockup rules in
   `.claude/skills/init-factory/phases/screens.md`. Never copy a mockup into
   the source root.
2. Ask the user to confirm it (section 5), with a `Show:` line naming the
   mockup file.
3. After the user confirms it, update the screen's row in `product-screens`
   (`backlog doc update`) and `meta/product/screens/_about.md`. Criteria
   that follow from the screen carry `[screen: <id>]`.

## 5. Asking the user and calling research

You cannot talk to the user. To ask, write the questions file your frame
names and return `RETURN ask <file>`. At most four questions, recommended
option first:

```markdown
## Q1: <question>
Why: <one line>
Options:
- <label> (Recommended): <what it means>
- <label>: <what it means>
Show: <file the user should look at, optional>
```

You are relaunched with the answers file; continue from there. Ask only what
the user must decide. A fact (how a library behaves, a current version) is a
research question: write it to the call file and return
`RETURN call researcher <file>`.

## 6. Output

Before the output file, confirm each line:

- every criterion is `GIVEN / WHEN / THEN`, testable through one action;
- every criterion traces to the user's words or carries a source tag;
- no `ASSUMED:` prefix is left;
- the task has a `module:` label per module touched.

Your output file starts with `task: <id>`, then one line per criterion:
`<n>: <source>`. Final line: `RETURN ok <output file>`, or
`RETURN blocked <reason>` when the request cannot become a task (say why).

## 7. Forbidden

- Code, tests, plans, or commits.
- Editing files other than the task (through the CLI), screen mockups, the
  screens catalog, and your frame's output, call, and ask files.
- Finishing with an `ASSUMED:` criterion the user has not confirmed.
