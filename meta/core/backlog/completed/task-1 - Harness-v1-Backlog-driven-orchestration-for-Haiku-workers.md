---
id: TASK-1
title: 'Harness v1: Backlog-driven orchestration for Haiku workers'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-10 07:50'
updated_date: '2026-10-10 07:53'
labels:
  - harness
dependencies: []
modified_files:
  - AGENTS.md
  - PLAN.md
  - .claude/agents/searcher.md
  - .claude/agents/test-writer.md
  - .claude/agents/implementer.md
  - .claude/agents/orchestrator.md
  - .claude/agents/scaffolder.md
  - .claude/agents/tester.md
  - .claude/agents/executor.md
  - meta/_about.md
  - meta/guides/orchestrate.md
  - meta/guides/search.md
  - meta/guides/test.md
  - meta/guides/implement.md
  - meta/architecture/vertical-slice.md
  - meta/registry/_about.md
  - meta/registry/persistence.md
  - meta/registry/runner.md
  - meta/practices/_about.md
  - meta/practices/generic/testing.md
  - meta/docs/harness-review.md
  - meta/tools/check-harness.sh
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Harness is the first deliverable. Goal: a software factory that minimal models (Haiku, later open-weight quantized) can run. Backlog.md is the plan of record and holds the acceptance criteria that act as cases. Previous meta/plans/ design is superseded. Workers are Haiku subagents launched from the main thread; no headless launch. Architecture defaults: vertical slices, PostgreSQL only. Stack and test runner stay undecided until init-factory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Orchestrator procedure lives in meta/guides/orchestrate.md and uses only Backlog task fields: acceptance criteria as cases, plan, notes, final summary, dependencies
- [x] #2 No headless launch remains: grep for 'claude -p' under .claude/ and meta/ returns no matches
- [x] #3 Subagent definitions exist in .claude/agents/ for searcher, test-writer and implementer, each with model claude-haiku-5-5; orchestrator.md, scaffolder.md, tester.md and executor.md are removed
- [x] #4 Vertical slice and PostgreSQL-only persistence are defined in meta/architecture/ and meta/registry/ and recorded as Backlog decisions
- [x] #5 meta/registry/runner.md marks stack and test runner as TBD, to be set by init-factory
- [x] #6 AGENTS.md git section matches the user rules: commit frequently to main, orchestrator may push, no force push
- [x] #7 meta/tools/check-harness.sh exits 0: every path referenced by .claude/agents/ and meta/guides/ exists
- [x] #8 PLAN.md describes the v1 design and no longer mentions meta/plans/ or scaffold packets
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rewrite AGENTS.md git and harness sections (main, commit often, orchestrator pushes).
2. Remove old persona files (orchestrator, scaffolder, tester, executor); add searcher, test-writer, implementer subagents on claude-haiku-5-5.
3. Write meta/_about.md index, guides: orchestrate, search, test, implement.
4. Write meta/architecture (vertical slice) and meta/registry (persistence=postgres, runner=TBD).
5. Record vertical slice and postgres decisions with backlog decision create; link from architecture files.
6. Update meta/practices testing rules to AC-driven and e2e-at-slice-entry.
7. Add meta/tools/check-harness.sh; run it.
8. Rewrite PLAN.md and meta/docs/harness-review.md.
9. Commit per step to main; push.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Checks: check-harness.sh exit 0; grep 'claude -p' under .claude and meta returns nothing; .claude/agents holds searcher, test-writer, implementer, all claude-haiku-5-5; decisions 1-3 created; AGENTS.md git section rewritten.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Harness v1: Backlog is the plan of record, acceptance criteria are the cases. Subagents searcher, test-writer, implementer on Haiku, launched from main thread; orchestrator procedure in meta/guides/orchestrate.md. Defaults: vertical slices (decision-1), PostgreSQL only (decision-2); runner TBD until init-factory (decision-3). Verified by meta/tools/check-harness.sh (exit 0) and grep checks. Full test suite not run: no runner exists yet.
<!-- SECTION:FINAL_SUMMARY:END -->
