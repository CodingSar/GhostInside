---
id: TASK-15
title: Plan step size cap and guide tuning for small models
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:42'
labels: []
dependencies: []
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research 2026-10-16: small models succeed on short tasks (METR 80 percent horizon far below the 50 percent one); few canonical examples beat rule lists; say what to do rather than what not to do; Anthropic published Haiku 5.5 paragraphs ("run a real check before reporting done", anti test gaming) that were measured. Guides stay short.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 parse_plan rejects a step with more than 4 files, saying so
- [ ] #2 plan.md states the 4-file cap and prefers one criterion per step
- [ ] #3 implement.md carries the published real-check paragraph and an end-of-job checklist
- [ ] #4 test.md and intake.md each end with a short checklist and keep their forbidden lists
- [ ] #5 test_loop.py covers the file cap
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. parse_plan: reject a step with more than 4 files. 2. plan.md: state the cap, prefer one criterion per step. 3. implement.md: real-check paragraph and end checklist. 4. test.md and intake.md: end checklists. 5. test_loop.py covers the cap.
<!-- SECTION:PLAN:END -->
