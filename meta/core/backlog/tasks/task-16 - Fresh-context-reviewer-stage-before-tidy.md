---
id: TASK-16
title: Fresh-context reviewer stage before tidy
status: To Do
assignee: []
created_date: '2026-10-16 20:30'
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
- [ ] #1 A reviewer agent on Haiku reads a guide meta/core/guides/review.md, the diff file, the criteria, and the tests, and writes gaps as file:line lines with the criterion each misses, correctness only
- [ ] #2 loop.py runs the review phase after the last step: it writes the diff since the task start to the run folder, capped, and launches the reviewer
- [ ] #3 On gaps, loop.py launches one implementer fix run with the union of the plan files as allowlist and the full test command, then continues to tidy without a second review
- [ ] #4 On no gaps or after the fix run, the task continues to tidy; a reviewer deviation or blocked stops the run
- [ ] #5 check-harness.sh, GUIDES, the SubagentStop matcher, design.md, and _about.md name the reviewer
- [ ] #6 test_loop.py covers gaps, no gaps, and the fix run
<!-- AC:END -->
