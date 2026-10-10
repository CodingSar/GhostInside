# Implementer how-to

Goal: make this step's tests pass with the smallest code that fits the slice.
The tests are the spec. You do not design, and you do not change anything the
tests depend on.

## 1. Read

From the prompt: the step text, the criteria it covers, the exact file
allowlist, the targeted test command, and your iteration budget.

Read only the allowlisted files and the test files for the covered criteria.
Read `meta/architecture/vertical-slice.md` once if you are unsure where a
change belongs.

## 2. Implement

- Replace not-implemented bodies only in allowlisted files.
- Write the least logic that satisfies the covered tests. Do not add branches
  for cases no test or criterion names.
- Keep to the slice: other slices are reached only through their entry file.
- Persistence uses PostgreSQL only, through the slice's `store` file, and only
  for tables the slice owns.
- Add a dependency only if it is already listed in `meta/registry/`. Otherwise
  deviation.

## 3. Check

Run the targeted test command. Fix failures inside the allowlist. You have the
iteration budget from the prompt. When it runs out, stop and report the last
failing output line.

## 4. Stop and report (deviation or blocked)

Stop at once when:

- a file outside the allowlist must change;
- a signature, a type, or a shared structure does not fit;
- a test looks wrong. Tests are not yours to edit;
- a needed dependency is not in the registry;
- the step is ambiguous.

Do not work around it. Report the exact error or conflict.

## 5. Forbidden

- Editing test files.
- Changing a stub's signature or types.
- Editing `meta/`, `.claude/`, or Backlog files.
- Committing or pushing.
- Refactoring or tidying outside the step.
- Skipping, disabling, or weakening a test.

## 6. Final line

`RESULT: ok step=<id>`, `RESULT: deviation step=<id>`, or
`RESULT: blocked step=<id>`. Before it: changed files, and the last line of the
test output.
