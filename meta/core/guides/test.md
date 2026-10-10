# Test-writer how-to

Goal: one failing test per acceptance criterion, plus the signature-only stubs
those tests call. Written before any implementation exists. The criteria are
the spec; the implementer must make the tests pass without changing them.

## 1. Read

From the prompt: the task id, the criteria with numbers, the slice path, the
testing packet, the review rules, and the test command.

If the file `test.md` exists in `meta/product/overlays/`, read it next. It adds
stack specifics (commands, paths, file extensions, test idioms) to this guide.
It never relaxes a forbidden item.

Apply the testing packet first. Domain rules replace generic rules for the
same topic. A criterion overrides any practice; if a practice conflicts with a
criterion, follow the criterion and note the conflict in your reply.

Read the slice folder if it exists, for names and existing signatures only.

## 2. Map criteria to tests

- One test per criterion. The criterion number is in the test name, for
  example `AC2 discounts apply once per order`.
- Copy the GIVEN / WHEN / THEN values into the test as literals. Do not
  derive expected values from code.
- Put tests in the slice's `tests/` folder. One file per slice entry point.
- Criterion without GIVEN / WHEN / THEN form: write the test from its plain
  text and say so in your reply.

## 3. Shape of the test

- Prefer end-to-end style for behaviour: call the slice's entry file, use a
  real PostgreSQL database through the connection in
  `meta/core/defaults/persistence.md`, and assert the returned value or the state
  you can read back.
- Pure rules may use direct unit calls.
- Never mock the database. Mock only the clock, randomness, and network.
- No sleeps. No wall-clock time without an injected clock.
- Call only the entry file's public signature. No private helpers.

## 4. Stubs

Create the signatures the tests call, with typed inputs and outputs. The body
raises not-implemented in the language's idiom. Nothing else: no logic, no
defaults, no constants that encode rules.

## 5. Keep it minimal

- No test for a stub's existence, a getter, a constructor, or wiring.
- Two criteria that expect the same thing: stop and report the duplicate.
- A criterion that cannot be expressed through the public signature: stop and
  report it. Do not invent a substitute.

## 6. Forbidden

- Skip, todo, pending, or xfail markers.
- Tests that pass on not-implemented.
- Edits to logic, or to files outside the slice's `tests/` folder and its stub
  entry file.
- Snapshot tests of unspecified output.
- Asserting internal call counts or order.
- Adding a criterion, or a rule the criteria do not state.

## 7. Finish

Final line: `RESULT: ok tests=<count> stubs=<count>`, or
`RESULT: blocked <reason>`.
