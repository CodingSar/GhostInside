---
id: TASK-16
title: Fresh-context reviewer stage before tidy
status: Done
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:49'
labels: []
dependencies: []
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Anthropic Claude Code best practices and Cognition (multi-agents-working, 2026) both report that a clean-context reviewer that sees only the diff and the criteria finds about two real bugs per change, because it is not anchored on the writer. Deterministic gates prove the tests pass, not that the change is right. One bounded fix run keeps it dark.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A reviewer agent on Haiku reads a guide meta/core/guides/review.md, the diff file, the criteria, and the tests, and writes gaps as file:line lines with the criterion each misses, correctness only
- [x] #2 loop.py runs the review phase after the last step: it writes the diff since the task start to the run folder, capped, and launches the reviewer
- [x] #3 On gaps, loop.py launches one implementer fix run with the union of the plan files as allowlist and the full test command, then continues to tidy without a second review
- [x] #4 On no gaps or after the fix run, the task continues to tidy; a reviewer deviation or blocked stops the run
- [x] #5 check-harness.sh, GUIDES, the SubagentStop matcher, design.md, and _about.md name the reviewer
- [x] #6 test_loop.py covers gaps, no gaps, and the fix run
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New agent .claude/agents/reviewer.md on Haiku and guide meta/core/guides/review.md. 2. loop.py: review phase after the last step writes diff.md (capped), launches the reviewer with criteria and test files; gaps -> one implementer fix run (plan files, full test command) -> tidy; no gaps -> tidy. 3. GUIDES, SubagentStop matcher, check-harness core_paths, design.md, _about.md, orchestrate.md. 4. test_loop.py: gaps, no gaps, fix run.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
reviewer agent (.claude/agents/reviewer.md, Haiku, read-only plus Write for its frame output) and guide meta/core/guides/review.md; loop.py review phase between step and tidy: diff capped at DIFF_LINES, gaps parsed by GAP_RE, gaps outside the diff ignored, one implementer fix run inside plan files, failing fix discarded and relaunched once; SubagentStop matcher and check-harness core paths include the reviewer; 3 new loop tests (22 green); HD-24.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fresh-context reviewer stage added between the last plan step and tidy, with one bounded fix run (HD-24).
<!-- SECTION:FINAL_SUMMARY:END -->
