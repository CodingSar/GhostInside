---
id: TASK-18
title: 'Reference fixture product: Python and PostgreSQL clone with five fixture tasks'
status: To Do
assignee: []
created_date: '2026-10-17 11:10'
labels: []
dependencies: []
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Factory evaluation (design.md Evaluation, HD-22) needs tasks with known outcomes run through the full loop, but the template has no stack so nothing runs end to end. User decision 2026-10-17 (handoff decision 3): create a tiny reference product clone, Python plus PostgreSQL, hosting a fixture set of five Backlog tasks with known outcomes. The clone is a separate repository made with init-factory in its own session; this task tracks it from the template side. Fixture runs are the measurement bed for TASK-17.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A reference clone exists with the template as its harness remote, stack ratified as Python plus PostgreSQL, walking skeleton green
- [ ] #2 Five fixture tasks exist in its product backlog, each with criteria and a recorded expected outcome (green first pass, expected STOP, expected gaps)
- [ ] #3 loop.py report --all over one full fixture run prints comparable metrics for each task
- [ ] #4 The template design.md Evaluation section names the clone and how to run the fixture set
<!-- AC:END -->
