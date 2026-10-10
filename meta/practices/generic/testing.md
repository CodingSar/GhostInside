# Testing practice (generic)

Fallback used when no domain-specific testing practice exists. Domain files
override these rules where they conflict.

## What to test

- Business rules and their outcomes. Not wiring, not framework code.
- Test through the unit's public interface. Assert returned values, visible
  state, or the error raised.
- One test per rule or case. Name it after the behaviour it pins.

## How to write a test

- Arrange, act, assert. One act per test.
- Each test is independent. No shared mutable state, no order dependency.
- Use the case's given values as literals. Do not derive expected values
  from the code under test.
- Keep assertions to what the rule says. No snapshot of unspecified output.

## Doubles

- Replace only external boundaries: clock, randomness, network, storage.
- Never replace the unit or rule under test.
- Do not assert internal call counts or order.

## Determinism

- No sleeps, real network, or wall-clock time.
- Seed any randomness. Inject time.

## Failure quality

- A failing test names the case it pins. Its message states expected and
  actual values.
- A test that passes for the wrong reason is a defect.
