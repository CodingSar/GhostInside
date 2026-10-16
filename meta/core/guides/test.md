# Test-writer how-to

Goal: one failing test per acceptance criterion, plus the signature-only stubs
those tests call, written before any implementation exists. The criteria are
the spec; the implementer must make the tests pass without changing them.
This guide is the single home of the testing rules.

## 1. Read

From your frame: the task id, the criteria with their numbers, the slice
paths, the packet files, the `Retire:` and `Change:` lines, and the test
command. A job that starts with `tidy:` is a tidy run: go to section 8.

If `meta/product/overlays/test.md` exists, read it next. It adds stack
specifics: test file naming, fixtures, datastore reset, the not-implemented
idiom. It never relaxes a forbidden item.

The first packet, `rules.md`, holds the architecture, the stack, and the review rules; the others hold one module each. Follow
the review rules in the tests you write. A criterion overrides any rule; on
a conflict, follow the criterion and note the conflict in your output file.

Read the slice folders named in the frame, for names and signatures only.

## 2. Map criteria to tests

- One test per criterion. Its name carries the task id and the criterion
  number, `TASK-12#2 discount applies once per order`, or the closest form
  the language allows (the overlay says which).
- Copy the GIVEN / WHEN / THEN values into the test as literals. Never derive
  expected values from code.
- The test goes in the slice's test file. One test file per slice.
- A criterion without GIVEN / WHEN / THEN form: write the test from its plain
  text and say so in your output file.

## 3. Retire and change

- `Retire: <file> :: <test> -> delete`: delete that test.
- `Retire: <file> :: <test> -> rewrite as TASK-n#k`: replace it with the test
  for that criterion, under the new name.
- `Change: <handler> :: <old> -> <new>`: change the handler's signature and
  its `index` re-export to the new one. Leave the body as it is; the
  implementer adapts it. If the body no longer compiles against the new
  signature, replace it with not-implemented and say so in your output file.

Every other existing test stays exactly as it is.

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
- A new module's tables do not exist yet: setup must not create, query, or
  require them. The handler stub fails first; the implementer adds the
  migration.
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
- Keep each test short; shared arrange code goes in fixtures in the same
  file. If the slice's test file would pass the test file cap in the
  architecture, stop and report: the slice holds more than one use case.

## 7. Forbidden

- Skip, todo, pending, or xfail markers.
- Tests that pass on not-implemented.
- Edits to tests outside the `Retire:` lines, and signature edits outside
  the `Change:` lines.
- Writes outside the named slice folders and the `index` re-export lines.
- Snapshot tests of unspecified output.
- Adding a criterion, or a rule the criteria do not state.

## 8. Tidy run

The job lists check findings in test files; the frame's "Edit only" list is those files. Fix only those: split long
tests, move repeated arrange code into fixtures in the same file, apply the
lint rule named. Test names, literal values, and assertions stay exactly as
they are. A finding you cannot fix that way: report it as blocked.

## 9. Finish

Before the output file, confirm each line:

- one test per criterion, named `<task>#<n>`, with the criterion's literals;
- every test calls a stub that raises not-implemented, so it fails now;
- every stub has typed inputs and outputs and no logic;
- every `Retire:` and `Change:` line is applied, nothing else touched.

Write your output file: `tests=<count> stubs=<count> retired=<count>`, the
files you wrote, and any notes the sections above ask for. Never run the
tests; `loop.py` runs the red gate.

Final line, exactly one of: `RETURN ok <output file>`,
`RETURN deviation <reason>` (a stop rule above fired), or
`RETURN blocked <reason>`.
