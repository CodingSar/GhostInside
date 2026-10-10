# Testing practice (generic)

Fallback used when no domain-specific testing rule exists. Domain files
replace these rules for the same topic.

## Tests are the acceptance criteria

- One test per acceptance criterion of the Backlog task. The criterion number
  is in the test name: `AC<n>`.
- Given / when / then values are literals in the test. Expected values are
  never derived from the code under test.
- Criteria are the only source of expected behaviour. A test that pins a rule
  no criterion states is a defect.

## Level

- Behaviour tests are end-to-end style: call the slice's `index` entry point,
  use the real datastore, assert the returned value or the state read back
  through the same interface.
- Pure rules, with no I/O, may be unit tests.
- A criterion that spans two slices is tested through the entry point of the
  slice the user acts on.

## Doubles

- Mock only external boundaries: clock, randomness, network.
- Never mock the database (see `meta/core/defaults/persistence.md`).
- Never mock the unit under test.
- Do not assert internal call counts or call order.

## Determinism

- No sleeps. No real network. No wall-clock time without an injected clock.
- Seed any randomness.
- Each test is independent: no shared mutable state, no order dependency.
  Reset the datastore state each test in the way the runner defines.

## Failure quality

- Arrange, act, assert. One act per test.
- A failing test names its criterion. Its message gives expected and actual
  values.
- A test that passes for the wrong reason is a defect.
