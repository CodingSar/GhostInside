# GhostInside: software factory harness

Status: v1 done (`TASK-1`). Next: `init-factory` (`TASK-2`).

## Goal

A software factory that minimal models can run: Haiku first, then
open-weight quantized models. The harness is the structure around the model.
Small models follow closed procedures well and wander when context is large,
so the harness keeps each worker's context small and its steps explicit.
Stack and domain are not decided here. GhostInside is a template; each
product is a clone of it. In the clone, `init-factory` proposes the stack and
domain practices and the user ratifies them.

## Parts

| Part | Where | Role |
|---|---|---|
| Backlog tasks | `backlog/` | Plan of record. Acceptance criteria are the cases. |
| Orchestrator | main thread, `meta/guides/orchestrate.md` | Owns one task from intake to Done. Launches workers. Runs tests. Commits and pushes. |
| Workers | `.claude/agents/`, Haiku | `searcher` (read-only), `test-writer`, `implementer`. Each reads one guide first. |
| Guides | `meta/guides/` | Procedures. Core guides are written by a human and owned by the template. `init-factory` writes stack overlays in `meta/guides/stack/` only. |
| Defaults | `meta/architecture/`, `meta/registry/` | Vertical slices. PostgreSQL only. Runner TBD. Defaults are priors that `init-factory` may supersede by a ratified decision. |
| Practices | `meta/practices/` | Testing rules. `init-factory` vendors facet packs from the central repo `CodingSar/GhostInsidePractices` and pins them in `practices.lock`. |
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

1. Central practices repo `git@github.com:CodingSar/GhostInsidePractices.git`, created by the user
   (`TASK-3`).
2. `init-factory` skill (`TASK-2`). Runs in the Opus main thread inside a
   clone. Phases: brief, facets, stack and architecture, practices,
   provision and seed, walking skeleton. Each phase is an acceptance
   criterion of an init task, so a re-run resumes, and a re-run on an
   initialized clone amends.
3. Eval fixtures for `init-factory` (`TASK-4`).
4. First end-to-end run on a toy slice to check the flow.
5. Build the factory-level eval fixtures.

## Settled

- Vertical slices by default (`decision-1`).
- PostgreSQL only by default (`decision-2`).
- Stack and runner decided through `init-factory` (`decision-3`): it
  proposes, the user ratifies at grouped gates (`decision-5`).
- Template and clone: products are clones with a `harness` remote
  (`decision-4`).
- Defaults are priors, superseded only by a ratified decision (`decision-6`).
- Core guides are template-owned; stack specifics go in overlays
  (`decision-7`).
- Practices come from a central repo as facet packs, vendored and pinned,
  delta-checked after 7 days; new packs go back by PR (`decision-8`).
- Haiku only for workers until the flow works.
- No headless launch. Workers are subagents launched from the main thread.
- Harness changes live on `main`; commit and push often.
