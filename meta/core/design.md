# GhostInside: design

A software factory that minimal models can run: Haiku first, then open-weight
quantized models. The harness is the structure around the model. Small models
follow closed procedures well and wander when context is large, so the
harness keeps each worker's context small, its steps explicit, and every
check that can be deterministic deterministic.

Status and next work live in the harness backlog
(`BACKLOG_CWD=meta/core backlog task list --plain`). Decisions and their
rationale live in `meta/core/decisions.md`.

## Template and product

GhostInside is a template. Each product is a `git clone` of it with the
template as the `harness` remote (`HD-4`). In the clone, `init-factory`
proposes the stack and practices and the user ratifies them (`HD-5`).

| Layer | Where | Owner |
|---|---|---|
| Core | `meta/core/`, `AGENTS.md`, `CLAUDE.md`, core agents, the init-factory skill | Template. Never edited in a clone; upgrades merge from `harness`. |
| Product harness | `meta/product/` | init-factory, in the clone. |
| Product | `src/`, `scripts/`, `backlog/`, root config files | The factory's workers and the user. |

## Parts

| Part | Where | Role |
|---|---|---|
| Backlog | root `backlog/` | Product plan of record. Acceptance criteria are the cases. |
| Orchestrator | main thread, `meta/core/guides/orchestrate.md` | Owns one task from intake to Done. Launches workers, runs tests and checks, commits and pushes. |
| Workers | `.claude/agents/`, Haiku | `test-writer`, `implementer`. Each reads one guide first. |
| Guides | `meta/core/guides/`, overlays in `meta/product/overlays/` | Procedures, plus stack specifics per guide. |
| Defaults | `meta/core/defaults/` | Modules of slices; PostgreSQL only. Overridden only by a product file and a ratified decision (`HD-6`, `HD-9`). |
| Stack | `meta/product/stack.md` | Every command the factory runs. TBD in the template. |
| Practices | `meta/product/practices/` | Facet packs from the central repo, vendored and locked (`HD-8`). |
| Tools | `meta/core/tools/` | `packet.py` (research packet), `structure.py` (product layout and size), `practices.py` (packs), `guard.py` (Bash hook), `check-harness.sh`. |
| init-factory | `.claude/skills/init-factory/` | Configures a clone: brief, facets, stack, packs, provision, seed, walking skeleton. Five gates. |

## Flow of one task

1. Intake: the orchestrator creates a Backlog task. Each criterion traces to
   the user's words, or is marked `ASSUMED:` until confirmed.
2. Research: `meta/core/tools/packet.py` prints the rules and slice files, with file and line.
3. Plan: the task's `plan` field. Steps name the slice, files, criteria,
   test command, and the tests the change retires.
4. Test first: `test-writer` writes one test per criterion (`TASK-n#k`) and
   the stubs. All new tests fail for the right reason; all others pass.
5. Implement: one `implementer` per plan step, inside a file allowlist.
6. Tidy: the check command (lint, boundaries, structure, duplication, dead
   code) runs; findings in the plan's files get one tidy step.
7. Verify: full suite and check command once; changed files match the plan.
8. Close out: criteria checked only with run evidence. Commit and push.

## Product code

`meta/core/defaults/architecture.md`: modules own their tables and expose an
`index`; each use case is a flat slice inside its module; `app/` wires
transports to module indexes; `shared/` is a kernel without business rules.
`_about.md` catalogs name every module and slice. Size caps and forbidden
catch-all folders keep code small; `structure.py` and the stack's boundary
checker enforce them on every task.

## Where probability is used, and where it is not

- Deterministic: the packet, file allowlists, status values, the red check,
  the `RESULT:` lines, the check command, the harness checks, the guard
  hook, the stop rules.
- Probabilistic: the code inside a stub, helper names, how a test is
  phrased, the retries that give the model another sample.
- Retries are cheap and bounded. Gaps, deviations, and ambiguity stop the
  run.

## Evaluation

End-to-end tests are the acceptance evidence for each task. Factory-level
evaluation is separate: run the same small tasks through the factory and
record how often the first pass is green, how many files fall outside the
plan, how many retries and tidy runs a task needs, and how large the
orchestrator's context gets. Fixtures are Backlog tasks with known outcomes,
so runs are comparable.
