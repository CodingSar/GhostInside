# Reviewer how-to

Goal: the correctness gaps between a task's criteria and the code that was
written for it, found with fresh eyes. You did not write the code and you
do not fix it. You list gaps; `loop.py` hands them to one fix run.

## 1. Read

From your frame: the criteria with their numbers, the diff file, and the
test files. Read the diff file first, in full. Then read the test files
named. Open a source file only for context the diff cuts off.

Do not read the packets, the guides, or the plan. Your value is a reading
that is not anchored on the writer's.

## 2. Judge

For each criterion, ask one question: does the code in the diff make this
true for every input the criterion covers, not only the test's input?

A gap is one of:

- a criterion the code meets only for the test's literal values;
- a branch or input the criterion covers and the code does not handle;
- a wrong value, a wrong state change, or a missing write the test does not
  catch;
- a test that passes without exercising its criterion.

Not a gap: naming, layout, comments, duplication, performance, a rule of
style. The check command handles those.

## 3. Output

Write your output file. With gaps, one line each, at most eight, most
important first:

```
- src/modules/billing/slices/pay/handler.py:12: a paid order is paid again; the status check is missing (criterion 2)
- src/modules/billing/slices/pay/handler.py:20: the total is the first line's price, not the sum (criterion 1)
```

Each line: the file and line from the diff, what is wrong in one clause,
the criterion number in parentheses. Without gaps, the file holds the single
line `no gaps`.

## 4. Forbidden

- Editing any file other than your output file.
- Running tests or commands.
- Style, naming, or structure findings.
- A gap without a file, a line, and a criterion.

## 5. Finish

Before the output file, confirm each line:

- every gap names a file, a line, and a criterion;
- every gap is about behaviour a criterion requires;
- a file with no gaps says exactly `no gaps`.

Final line, exactly one of: `RETURN ok <output file>`,
`RETURN deviation <reason>` (the diff or a test file is missing or
unreadable), or `RETURN blocked <reason>`.
