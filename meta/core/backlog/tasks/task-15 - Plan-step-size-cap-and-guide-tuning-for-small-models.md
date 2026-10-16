---
id: TASK-15
title: Plan step size cap and guide tuning for small models
status: Done
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:43'
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
- [x] #1 parse_plan rejects a step with more than 4 files, saying so
- [x] #2 plan.md states the 4-file cap and prefers one criterion per step
- [x] #3 implement.md carries the published real-check paragraph and an end-of-job checklist
- [x] #4 test.md and intake.md each end with a short checklist and keep their forbidden lists
- [x] #5 test_loop.py covers the file cap
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. parse_plan: reject a step with more than 4 files. 2. plan.md: state the cap, prefer one criterion per step. 3. implement.md: real-check paragraph and end checklist. 4. test.md and intake.md: end checklists. 5. test_loop.py covers the cap.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
test_loop.py 19 tests green incl. the 5-file step rejection; check-harness.sh ok.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
parse_plan rejects steps with more than STEP_FILES (4) files; plan.md states the cap and one criterion per step; implement.md has the real-check paragraph and a finish checklist; test.md and intake.md end with checklists, forbidden lists kept. Verified by test_loop.py test_plan_parsing and check-harness.sh. HD-23.
<!-- SECTION:FINAL_SUMMARY:END -->
