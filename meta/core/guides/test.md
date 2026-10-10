# Test-writer how-to

Goal: one failing test per acceptance criterion, plus the signature-only stubs
those tests call, written before any implementation exists. The criteria are
the spec; the implementer must make the tests pass without changing them.
This guide is the single home of the testing rules.

## 1. Read

From the prompt: the task id, the criteria with their numbers, the slice
paths, the packet, the retire list, and the test command.

If `meta/product/overlays/test.md` exists, read it next. It adds stack
specifics: test file naming, fixtures, datastore reset, the not-implemented
idiom. It never relaxes a forbidden item.

The packet holds the architecture, the stack, and the review rules. Follow
the review rules in the tests you write. A criterion overrides any rule; on
a conflict, follow the criterion and note the conflict in your reply.

Read the slice folders named in the prompt, for names and signatures only.

## 2. Map criteria to tests

- One test per criterion. Its name carries the task id and the criterion
  number, `TASK-12#2 discount applies once per order`, or the closest form
  the language allows (the overlay says which).
- Copy the GIVEN / WHEN / THEN values into the test as literals. Never derive
  expected values from code.
- The test goes in the slice's test file. One test file per slice.
- A criterion without GIVEN / WHEN / THEN form: write the test from its plain
  text and say so in your reply.

## 3. Retire

Edit or delete only the tests on the retire list, as the list says. Every
other existing test stays exactly as it is.

## 4. Shape of the test

- Behaviour: call the slice's `handler` and use the real datastore from
  `meta/product/stack.md`. Assert the returned value, or the state read back
  through the same module's public interface.
- Pure rules with no I/O may be unit tests on the slice's `rules`.
- A criterion that spans modules is tested through the slice the user acts
  on.
- Doubles: mock only clock, randomness, and network. Never mock the
  datastore. Never mock the unit under test. Never assert internal call
  counts or call order.
- Determinism: no sleeps, no real network, no wall-clock time without an
  injected clock, seeded randomness. Each test is independent; reset the
  datastore state as the overlay says.
- Arrange, act, assert. One act per test. A failing test names its criterion
  and shows expected and actual values.

## 5. Stubs

Create the signatures the tests call, with typed inputs and outputs: the
slice's `handler`, and for a new slice the re-export line in its module's
`index`. The body raises not-implemented in the language's idiom. No logic,
no defaults, no constants that encode rules.

## 6. Keep it minimal

- No test for a stub's existence, a getter, a constructor, or wiring.
- Two criteria that expect the same thing: stop and report the duplicate.
- A criterion that cannot be expressed through the handler's signature: stop
  and report it. Do not invent a substitute.

## 7. Forbidden

- Skip, todo, pending, or xfail markers.
- Tests that pass on not-implemented.
- Edits to tests outside the retire list.
- Writes outside the named slice folders and the `index` re-export lines.
- Snapshot tests of unspecified output.
- Adding a criterion, or a rule the criteria do not state.

## 8. Finish

Final line: `RESULT: ok tests=<count> stubs=<count> retired=<count>`, or
`RESULT: blocked <reason>`.
