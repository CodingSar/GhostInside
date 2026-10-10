# GhostInside: software factory harness

Status: v1 in progress, tracked as Backlog `TASK-1`.

## Goal

A software factory that minimal models can run: Haiku first, then
open-weight quantized models. The harness is the structure around the model.
Small models follow closed procedures well and wander when context is large,
so the harness keeps each worker's context small and its steps explicit.
Stack and domain are not decided here. `init-factory` decides them with the
user, later.

## Parts

| Part | Where | Role |
|---|---|---|
| Backlog tasks | `backlog/` | Plan of record. Acceptance criteria are the cases. |
| Orchestrator | main thread, `meta/guides/orchestrate.md` | Owns one task from intake to Done. Launches workers. Runs tests. Commits and pushes. |
| Workers | `.claude/agents/`, Haiku | `searcher` (read-only), `test-writer`, `implementer`. Each reads one guide first. |
| Guides | `meta/guides/` | Procedures. Written by a human, not by a model. |
| Defaults | `meta/architecture/`, `meta/registry/` | Vertical slices. PostgreSQL only. Runner TBD. |
| Practices | `meta/practices/` | Testing rules. |
| Checks | `meta/tools/check-harness.sh` | Deterministic checks on the harness itself. |

## Flow

1. Intake: orchestrator creates a Backlog task. Each criterion traces to the
   user's words, or is marked `ASSUMED:` until confirmed.
2. Research: `searcher` returns a packet of verbatim rules. Gaps stop the run.
3. Plan: orchestrator writes the plan into the task's `plan` field.
4. Test first: `test-writer` writes one test per criterion and the stubs they
   call. The orchestrator runs them. All must fail for the right reason.
5. Implement: one `implementer` per plan step, inside a file allowlist. Targeted
   tests run per step.
6. Verify: full suite once. Changed files compared with the plan.
7. Close out: criteria checked only with run evidence. Final summary. Status
   Done. Commit and push.

## Where probability is used, and where it is not

- Deterministic: file allowlists, status values, the red check, the
  `RESULT:` lines, the harness check script, the stop rules.
- Probabilistic: the implementation inside a stub, helper names, how a test
  is phrased, the retries that give the model another sample.
- Retries are cheap and bounded. Gaps, deviations, and ambiguity stop the run.

## Evaluation

End-to-end tests are the acceptance evidence for each task. Factory-level
evaluation is separate: run the same small tasks through the factory and
record how often the first pass is green, how many files fall outside the
plan, how many retries a task needs, and how large the orchestrator's context
gets. Fixtures are Backlog tasks with known outcomes, so runs are comparable.

## Next

1. `init-factory` skill: asks the user about the product, the language, the
   runner, and the rest of `meta/registry/runner.md`. It records each answer
   as a Backlog decision and fills the registry.
2. First end-to-end run on a toy slice to check the flow.
3. Build the factory-level eval fixtures.

## Settled

- Vertical slices by default (`decision-1`).
- PostgreSQL only (`decision-2`).
- Stack and runner decided by the user, through `init-factory` (`decision-3`).
- Haiku only for workers until the flow works.
- No headless launch. Workers are subagents launched from the main thread.
- Harness changes live on `main`; commit and push often.
