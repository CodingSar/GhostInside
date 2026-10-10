---
id: TASK-4
title: Eval fixtures for init-factory
status: To Do
assignee: []
created_date: '2026-10-10 08:20'
labels: []
dependencies:
  - TASK-2
priority: medium
type: task
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
init-factory makes many judgment calls (facets, overrides of defaults, packs). Without fixed inputs there is no regression signal when the skill or the model changes. Canned concepts with scripted interview answers make runs comparable, like the factory-level fixtures in PLAN.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Four fixture concepts with scripted interview answers: CRUD SaaS, CLI tool with no stored data, realtime app, regulated domain
- [ ] #2 Each fixture states expected facets and expected decisions
- [ ] #3 A run checks: registry has no TBD, expected facets selected, decisions recorded, overrides fire (CLI fixture gets no PostgreSQL), skeleton tests green
- [ ] #4 Results of a run are recorded so later runs compare against them
<!-- AC:END -->
