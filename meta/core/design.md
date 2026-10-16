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
| Orchestrator | main thread on Sonnet (`HD-17`), `meta/core/guides/orchestrate.md` | Dispatcher: carries out the one line `loop.py` prints (LAUNCH, ASK, DONE, STOP) and reports each agent's `RETURN` line back (`HD-16`). |
| Loop | `meta/core/tools/loop.py`, state in `.scratch/<run>/` | The task state machine. Runs every deterministic step, commits, pushes; keeps agent calls and questions as a frame stack on disk. |
| Workers | `.claude/agents/`, Haiku | `intake`, `planner`, `test-writer`, `implementer`, `reviewer`; `researcher` on a bigger model. Each reads one guide and one frame, and ends with one `RETURN` line. Workers skip `CLAUDE.md` (`omitClaudeMd`) and pin `effort: medium`, HD-18. |
| Guides | `meta/core/guides/`, overlays in `meta/product/overlays/` | Procedures, plus stack specifics per guide. |
| Defaults | `meta/core/defaults/` | Modules of slices; PostgreSQL only. Overridden only by a product file and a ratified decision (`HD-6`, `HD-9`). |
| Stack | `meta/product/stack.md` | Every command the factory runs. TBD in the template. |
| Practices | `meta/product/practices/` | Facet packs from the central repo, vendored and locked (`HD-8`). |
| Tools | `meta/core/tools/` | `loop.py` (dispatcher loop and hooks), `packet.py` (research packet), `structure.py` (product layout and size), `practices.py` (packs), `guard.py` (Bash and file-write hook; subagents get read-only git and no harness writes), `check-harness.sh`. |
| init-factory | `.claude/skills/init-factory/` | Configures a clone: brief, screens (GUI only), facets, stack, packs, provision, seed, walking skeleton. Six gates, five without a GUI (`HD-15`). |
| Screens | `meta/product/screens/`, Backlog doc `product-screens` | Static HTML mockups of a GUI product's screens. Requirements, not code. |

## Flow of one task

Every stage below is run by `loop.py`; the main thread only dispatches.

1. Intake: the intake agent creates or checks the Backlog task. Each criterion traces to
   the user's words or a source tag, or is marked `ASSUMED:` until
   confirmed. A task that adds or changes a screen first updates its mockup
   and gets the user's confirmation.
2. Research: `meta/core/tools/packet.py` prints the rules (once per run) and the module and slice files, with file and line.
3. Plan: the task's `plan` field. Steps name the slice, files, criteria,
   test command, and the tests the change retires.
4. Test first: `test-writer` writes one test per criterion (`TASK-n#k`) and
   the stubs. All new tests fail for the right reason; all others pass.
5. Implement: one `implementer` per plan step, inside a file allowlist.
6. Review: a fresh-context `reviewer` reads only the diff, the criteria,
   and the tests, and lists gaps with file and line. Gaps get one
   implementer fix run inside the plan's files; a fix that breaks the
   suite is discarded and retried once (HD-24).
7. Tidy: the fix and check commands (lint, boundaries, structure,
   duplication, dead code) run; findings in the plan's files get one tidy
   run, findings elsewhere stop the task.
8. Verify: full suite and check command once; changed files since the start
   match the plan. Then one push, so the remote `main` stays green.
9. Close out: criteria checked only with run evidence.

## Product code

`meta/core/defaults/architecture.md`: modules own their tables and expose an
`index`; each use case is a flat slice inside its module; `app/` wires
transports to module indexes; `shared/` is a kernel without business rules.
`_about.md` catalogs name every module and slice. Size caps and forbidden
catch-all folders keep code small; `structure.py` and the stack's boundary
checker enforce them on every task.

## Where probability is used, and where it is not

- Deterministic: the task state machine in `loop.py`, the packet, file
  allowlists (the guard hook rejects a write outside the pending frame's
  list at write time, HD-19), status values, the red gate from the JUnit report, the
  `RETURN` lines, the frame stack, the check command, the harness checks, the guard
  hook, the stop rules.
- Probabilistic: the code inside a stub, helper names, how a test is
  phrased, the retries that give the model another sample.
- Retries are cheap and bounded. Gaps, deviations, and ambiguity stop the
  run.

## Evaluation

Behaviour tests through each slice's handler, against the real datastore,
are the acceptance evidence for each task. Factory-level
evaluation is separate: run the same small tasks through the factory and
record how often the first pass is green, how many files fall outside the
plan, how many retries and tidy runs a task needs, and how large the
frames get. `loop.py report` prints these for a run, `--all` for every run,
from the timestamped `log.md` (HD-22). Fixtures are Backlog tasks with known
outcomes, so runs are comparable.
