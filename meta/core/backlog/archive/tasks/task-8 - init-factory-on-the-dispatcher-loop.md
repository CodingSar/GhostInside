---
id: TASK-8
title: init-factory on the dispatcher loop
status: To Do
assignee: []
created_date: '2026-10-10 16:18'
updated_date: '2026-10-10 16:22'
labels:
  - init-factory
  - orchestrator
dependencies:
  - TASK-7
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-7 moved the orchestrator onto loop.py so a Haiku main thread only dispatches. init-factory still runs every phase in the main thread and assumes a model that can research, interview, and design in one context, which breaks the rule that everything but research runs on Haiku. It should run as a second state machine on the same loop: phase agents draft gate tables and return ask, research goes to the researcher, deterministic phase steps run in code.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each init-factory phase runs as a loop state with a Haiku phase agent; gates are ASK instructions carried out by the main thread
- [ ] #2 Research (stack versions, missing practice packs) goes through RETURN call researcher
- [ ] #3 Deterministic phase steps (preflight, practices.py, provision checks, skeleton commands, commits) run in loop.py
- [ ] #4 An interrupted init resumes from .scratch state and the init task
- [ ] #5 `check-harness.sh` passes and the loop tests cover the init states
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HD-17 (2026-10-10): main thread is Sonnet, not Haiku. The Haiku-only motivation in the description no longer applies; moving init-factory onto the loop still pays for bounded context and resume after /clear. Re-scope before starting.
<!-- SECTION:NOTES:END -->
