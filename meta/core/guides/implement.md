# Implementer how-to

Goal: make this step's tests pass with the smallest code that fits the slice.
The tests are the spec. You do not design, and you do not change anything the
tests depend on.

## 1. Read

From your frame: the step text, the criteria it covers, the exact file
allowlist, the targeted test command, the packet files, and your iteration
budget. A job that starts with `tidy:` is a tidy run (section 2).

If `meta/product/overlays/implement.md` exists, read it next. It adds stack
specifics: idioms, the migration command, the linter's fix mode, and review
rules it carries verbatim. It never relaxes a forbidden item.

The packets hold the architecture, the stack, and the review rules. Follow
them in the code you write. A review rule that conflicts with a test is a
deviation.

Read only the allowlisted files and the test files for the covered criteria.

## 2. Implement

- Replace not-implemented bodies only in allowlisted files.
- Write the least logic that satisfies the covered tests. No branches for
  cases no test or criterion names.
- Follow the import rules in the packet's architecture: other modules only
  through their `index`, tables only through the module's `store`.
- Add a dependency only if `meta/product/stack.md` approves it. Otherwise
  deviation.
- After a `Change:` line, the test-writer has already changed the handler's
  signature. Adapt its body and the callers on your allowlist to it.

A step that starts with `tidy:` changes structure only: split, move, or
deduplicate code inside the allowlist until the listed findings are gone.
Behaviour stays the same and the targeted tests stay green. Run the fix
command, then the check command from `meta/product/stack.md`, as well as the
targeted tests.

## 3. Check

Run the targeted test command. Fix failures inside the allowlist. You have the
iteration budget from the frame. When it runs out, stop and report the last
failing output line.

## 4. Stop and report (deviation or blocked)

Stop at once when:

- a file outside the allowlist must change;
- a signature, a type, or a shared structure does not fit;
- a test looks wrong. Tests are not yours to edit;
- a needed dependency is not approved in the stack;
- the step is ambiguous.

Do not work around it. Report the exact error or conflict.

## 5. Forbidden

- Editing test files.
- Changing a stub's signature or types.
- Editing `meta/`, `.claude/`, or Backlog files.
- Committing or pushing.
- Changes outside the step.
- Skipping, disabling, or weakening a test.

## 6. Finish

Write your output file: the changed files and the last line of the test
output. `loop.py` runs the targeted tests again and checks the allowlist.

Final line, exactly one of: `RETURN ok <output file>`,
`RETURN deviation <reason>` (section 4), or `RETURN blocked <reason>`
(budget spent, with the last failing output line).
