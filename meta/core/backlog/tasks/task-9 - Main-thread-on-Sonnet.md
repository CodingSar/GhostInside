---
id: TASK-9
title: Main thread on Sonnet
status: Done
assignee:
  - '@claude'
created_date: '2026-10-10 16:21'
updated_date: '2026-10-10 16:22'
labels:
  - orchestrator
dependencies: []
modified_files:
  - .claude/settings.json
  - meta/core/decisions.md
  - AGENTS.md
  - meta/core/design.md
  - meta/core/guides/orchestrate.md
  - meta/core/tools/loop.py
priority: high
type: enhancement
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User decision 2026-10-10: the orchestrator (main thread) runs on Sonnet, not Haiku. Reason given by the user: Haiku pricing rises above 100k context, and a main thread cannot stay under 100k tokens through a task without clearing mid-task. Workers stay on Haiku; the dispatcher loop (HD-16) stays, since it still keeps the main thread small and resumable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Project settings set the main thread model to Sonnet, so every product clone starts on it
- [x] #2 HD-17 records the change and amends HD-16; AGENTS.md, design.md, orchestrate.md say the main thread runs on Sonnet and workers on Haiku
- [x] #3 `check-harness.sh` passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. .claude/settings.json: "model": "claude-sonnet-5-5".
2. HD-17 (decision CLI + decisions.md row; HD-16 status amended).
3. AGENTS.md, design.md, orchestrate.md, loop.py docstring wording.
4. check-harness, commit, push; note on TASK-8.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evidence: settings.json "model": "claude-sonnet-5-5"; HD-17 = decision-17, HD-16 marked amended; check-harness ok; test_loop.py OK.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Main thread set to Sonnet via project settings (HD-17, amends HD-16); workers stay on Haiku, researcher on Sonnet, dispatcher loop kept. Docs updated; check-harness and loop tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
