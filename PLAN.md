# PLAN: Meta harness for small-model coding

Status: design in progress. Nothing here is committed work yet. The harness is
a stack-agnostic meta layer. Stack and domain content come later, as overlays
inside the same structure.

## Premise

Small models (Haiku-class) reason and copy well. They search badly, wander
when context is long, and invent rules when none are given. The harness
therefore:

- never asks a small model to search. A searcher agent does lookup and
  returns a packet
- gives each agent a short, pre-cut context, not the whole repo
- puts best practice in templates and guides the agents read first
- uses closed menus at every choice point

The inner ReAct loop is unchanged. The harness is the outer structure.

## Agents

Personas live in `.claude/agents/`. All run on Haiku for now. Each persona's
first act is to read its guide in `meta/guides/`. The guide holds the
procedure. The persona file holds only role limits.

| Persona | Role | Reads | Writes |
|---|---|---|---|
| orchestrator | plans, launches workers, checks results, closes out. Never writes app code | `guides/orchestrate.md`, plan, result lines | `meta/plans/` |
| searcher | lookup only. Matches exact keys, returns a packet | `meta/` catalog, needed index files | one packet file |
| scaffolder | structure, stubs, injection points, steps | `guides/scaffold.md`, plan, scaffold packet | plan, stubs, dirs |
| tester | minimal failing tests, one per plan case, before execution. Writes only; never runs tests | `guides/test.md`, plan `cases`, test packet, stub signatures | test files, plan file list |
| executor | fills stubs for one step | `guides/execute.md`, plan, execute packet | step's files only |

## Launching: separate processes, not subagents

Subagents share the caller's context, and the orchestrator must not fill up.
So the orchestrator launches each worker as a separate headless agent process.
Each worker has its own context, writes its output to a file, and prints a
final `RESULT:` line. The orchestrator reads that line and nothing else unless
it needs to decide something.

## Meta layout: progressive disclosure

Modelled on skills and MCP tool listings. Agents read a short description
first, then only the files the scope needs.

```
meta/
  _about.md                 root catalog: each directory, its description, the scope key it answers to
  guides/
    _about.md
    orchestrate.md          orchestrator how-to
    scaffold.md             scaffolder how-to
    execute.md              executor how-to
    search.md               searcher how-to (key matching, packet format)
  project/
    _about.md               domain tags and what they mean
    identity.md
    invariants.md           each invariant tagged with a domain
    glossary.md
  architecture/
    _about.md
    units.md                unit_kind -> pattern file, one row each
    layers.md               allowed dependency directions, anchor marker syntax
  patterns/
    _about.md               one row per unit kind
    <unit_kind>.md          one template per unit kind
  registry/
    _about.md
    concerns.yaml           concern -> approved dependency@version
    middleware.yaml         order of application
  decisions/
    _about.md               task type -> approach menu, rejected alternatives
  plans/
    <slug>/
      plan.md
      packets/              scaffold.md, execute-<step>.md
```

Each `_about.md` has the same shape:

```
---
description: <what this directory holds, one line>
keys: <scope key this answers to>
---
| key value | file | description |
|---|---|---|
| repository | repository.md | Persistence boundary: entity CRUD, session, error mapping |
```

Descriptions stay short. Each row must match its file (checked in the dry run).

## Scope and packets

Scope keys (no stack key; the stack is an overlay, added later):
`unit_kinds`, `concerns`, `domain`, `touches`, `mode`, `step`.

Packet format is defined in `.claude/agents/searcher.md`. Anchors come only
from explicit markers defined in `meta/architecture/layers.md`. Same scope on
the same index gives the same packet. Packets are files, so runs are
reproducible and auditable.

Scope key `practices` names best-practice topics (e.g. `testing`), looked up
in `meta/practices/`. Every lookup with a domain variant (patterns, practices,
registry) is tiered: the domain row first, the `generic` row as fallback. Each
packet entry records its `tier`. Agents that use search (searcher-fed workers,
i.e. scaffolder, tester, executor) read tiered packets only and never choose a
tier themselves.

## Gaps stop the run

Any entry in `gaps` stops the run. The orchestrator reports the gaps to the
user. It does not add entries itself and the searcher never fills gaps. We
can relax this later, once we see which gaps are safe to auto-resolve.

## Lifecycle

Status values: `draft` → `planned` → `executing` → `done`. Any failure goes
back to `draft` and stops the run. This is the procedure the orchestrator
guide (`meta/guides/orchestrate.md`) must carry.

1. **Intake.** Orchestrator writes `plans/<slug>/plan.md`, status `draft`,
   including the scope: `unit_kinds`, `concerns`, `domain`, `touches`. The
   orchestrator sets scope because it chose the approach. The scaffolder
   doesn't need to search to find out what it needs.
2. **Scope check.** Every scope value must be a key in the catalog. Unknown
   key is a gap: the searcher records it, the run stops, the orchestrator
   reports.
3. **Search.** Searcher in `scaffold` mode → packet. Gaps stop the run.
4. **Scaffold.** Scaffolder writes dirs, stubs, injection points, shared
   structures, and ordered steps. Must end `RESULT: ok`.
5. **Test first.** Searcher in `test` mode, scope including `practices:
   [testing]` and the plan's `domain` → `packets/test.md`. The packet carries
   testing best practice, domain tier first, generic fallback. Gaps stop the
   run. Tester reads the packet's practices before writing. Tester writes one test per plan case against the stubs, and appends
   the test files to the plan. Orchestrator runs the new tests: all must fail
   with `NotImplementedError` or an assertion. Import errors, collection
   errors, or passing tests stop the run.
6. **Review gate.** Orchestrator sets `planned`. Plans that add a dependency
   or touch `.claude/`, `meta/`, or `groma/` need user approval first.
7. **Execute.** Per step: searcher in `execute` mode on that step's markers,
   check gaps, then executor on that step. The step's check runs only that
   step's tests.
8. **Verify.** Run the test files covering the changed files. Diff changed
   files against the plan's file list.
9. **Close out.** Run the full suite only here, before merging to `main`.
   Status `done`. Decisions and registry changes recorded. Plan kept.

Test policy: tests run only by the orchestrator, and only at the red check,
per step, at verify, and at close-out. The full suite runs only at close-out.

## Repository files vs. business-layer files

Different kinds of unit need different amounts of structure.

- **Repository, adapter, boundary:** mostly mechanical. The pattern is a full
  template. The entity spec fills the variables. Near-deterministic.
- **Business and domain logic:** the template gives the shape only. Rules come
  from the plan as explicit cases (given / when / then). The executor writes
  code that passes those cases and invents no rules.
- **Pure domain functions:** specified by examples. The examples become tests,
  written before the code.

Each unit kind's pattern file says which of these applies.

## Pattern file format

Same sections in every pattern file, so a model learns the format once:

1. When to use
2. Inputs and outputs
3. Injection points
4. Skeleton with placeholders
5. One worked example
6. Forbidden moves

Patterns are derived from real code once there is some, then frozen. Do not
write them speculatively.

## Open work, in order

1. Write `meta/_about.md`, the four `guides/*.md`, and the `_about.md` for
   each directory.
2. Write the pattern format and the first pattern files (derived from real
   code, not guessed).
3. Verify headless launch: the exact `claude -p --agent` flags, the permission
   mode for unattended tool use, that `--agent` loads the persona file, and
   result line capture. Nothing else is built on top before this.
4. Dry-run one task end to end on a toy example. Check that gaps stop the run,
   the orchestrator's context stays small, and packets are reproducible.
5. Evaluation (below).

## Evaluation

A claim like "this helps small models" needs a measure. Run the same small
tasks with and without the harness, then compare:

- plan-to-diff drift: files changed outside the plan's list
- gap rate and where gaps occur
- deviations per step
- done-when checks passing on first try
- orchestrator context size at close-out
- human rating of coherence with the existing codebase

Start with 5 to 10 tasks. Change one thing at a time.

## Risks

- **Guides become the new prompt sprawl.** Keep each guide short and
  procedural. Test each one by running a task with it.
- **Descriptions drift from the files.** Checked in the dry run.
- **Gap stop is too strict.** Some gaps are harmless. We will learn which only
  from runs.
- **Headless launch is unverified.** The plan depends on it. See Open work, step 3.
- **Haiku is the weakest link for planning.** The guides and closed menus carry
  that load. If plans come out thin, the first fix is the guide, not a bigger
  model.

## Relation to existing work

- Claude Code config layer (`.claude/settings.json`) sits below this plan.
- `meta/docs/harness-review.md` governs changes to harness files. This plan
  follows that rule.
- `groma/` stays the architecture model. `meta/` is harness-owned.

## Deferred

- Hooks and enforcement (edit allowlists, plan-status guard, registry import
  check). Added last, once the flow works without them.
- Stack and domain overlays.
- Auto-resolving gaps.
- Scheduled cloud job to refresh `meta/practices/` (curated, reviewed before
  merge). Added at a later stage, not before the flow runs.
