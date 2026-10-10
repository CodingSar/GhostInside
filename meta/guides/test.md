# Tester how-to

Goal: the fewest tests that pin the plan's business rules, written before the
implementation exists. Tests are the spec. The executor must make them pass
without changing them.

## 1. Read

- The plan: its `cases` block and file list.
- The test packet, in this order:
  1. `practices` for `testing`: the rules, with their tier. Apply them first.
  2. `registry` for `testing`: the runner and version. Tests use only this.
  3. `invariants` and `patterns` for each unit kind.
- The stubs for the units under test: names, signatures, types. Nothing else.

Tier rules:

- `tier: domain` practice replaces the generic rule for the same topic. Where
  the domain practice is silent, the generic rule applies.
- A plan case overrides any practice. If a practice conflicts with a case,
  follow the case and note the conflict in your report.
- Do not add practices the packet does not list.

## 2. Map cases to tests

- One test per case. The case id is in the test name, e.g.
  `test_case_price_discount_03_...`.
- Cases are the only source of expected behaviour. Copy the given / when /
  then values into the test. Do not add rules.
- Parametrize only when cases differ by input alone and share one assertion.
  Each row keeps its own case id.

## 3. Test business logic

- Assert outcomes: returned values, state changes visible through the public
  interface, or the domain error raised.
- Call the unit through its stub signature only. Do not reach into private
  helpers.
- Mock only external boundaries (clock, randomness, network, storage). Never
  mock the rule under test.
- No sleeps, no real network, no wall-clock time, no random without a seed.

## 4. Keep it minimal

- No test for a stub's existence, a getter, a constructor, or framework code.
- No test for repository or adapter plumbing unless the plan lists a case for
  it.
- No duplicate tests across cases. If two cases expect the same thing, the
  plan is wrong: stop and report.
- Boundary tests only when the plan lists them as cases.

## 5. Red check expectation

Each test must fail for the stub's reason: `NotImplementedError` or a failing
assertion on the case's expected value. A test that cannot even import, or
that passes, is a defect. Write it so the failure is the expected one. The
orchestrator checks this after you finish.

## 6. Finish

Append test file paths to the plan's file list. Print the `RESULT` line.

## Forbidden

- Skip, xfail, pending, or todo markers.
- Tests that assert on `NotImplementedError` as a pass.
- Editing stubs or source to make imports work.
- Snapshot tests of unspecified output.
- Asserting internal call counts or call order.
