---
id: TASK-11
title: Allowlist enforced at write time by the guard hook
status: Done
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:36'
labels: []
dependencies: []
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A worker that edits outside its allowlist is caught only after it returns: its work is discarded and it is relaunched. Negative rules ("never edit tests") scale badly on small models (inverse scaling on negation, arXiv 2209.12711); a mechanical deny at the moment of the write, with the allowed list in the message, is feedback at the point of error. The frame should state the allowlist last, before the RETURN contract (start/end placement, arXiv 2307.03172).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 loop.py writes the allowed paths and prefixes of a launch into the pending frame in state.json
- [x] #2 guard.py denies Edit, Write, and NotebookEdit by a subagent to a path outside the pending frame allowlist and names the allowed paths in the reason
- [x] #3 A frame without an allowlist (intake, planner, researcher) is unrestricted beyond the harness protection
- [x] #4 The frame file ends with an "Edit only" section listing the allowlist, right before the Last line section
- [x] #5 test_guard.py and test_loop.py cover the deny, the allow, and the frame section
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. launch() stores allow list (exact paths and prefixes) in the frame; frame_text ends with an Edit only section before Last line. 2. guard.py reads .scratch/current -> state.json pending frame; denies Edit/Write/NotebookEdit outside the list for subagents, naming the allowed paths; frame out/call/ask always allowed. 3. Tests in test_guard.py and test_loop.py.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
test_guard.py (7 tests) and test_loop.py (17 tests) green; check-harness.sh ok.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
launch() stores an allow list in the pending frame and prints it as the Edit only section before Last line; guard.py check_allow denies subagent Edit/Write/NotebookEdit outside it (own frame files always allowed, frames without a list unrestricted). Verified by test_guard.py test_pending_frame_allowlist, test_loop.py happy path assertions, check-harness.sh. HD-19.
<!-- SECTION:FINAL_SUMMARY:END -->
