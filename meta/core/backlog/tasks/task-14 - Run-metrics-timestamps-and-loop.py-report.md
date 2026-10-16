---
id: TASK-14
title: 'Run metrics: timestamps and loop.py report'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:42'
labels: []
dependencies: []
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
design.md promises factory-level evaluation (first-pass green, files outside the plan, retries, tidy runs, context size) but nothing records it; log.md has no timestamps. Fixture evals need comparable numbers per run (Anthropic demystifying-evals, Hamel). The report is the prerequisite for any eval.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every log.md line starts with an ISO timestamp
- [x] #2 loop.py report prints for the current run: task, outcome, elapsed, launches per agent, relaunches, stops, steps green on first try, tidy runs, frame bytes written
- [x] #3 loop.py report --all prints one line per run under .scratch with the same numbers
- [x] #4 test_loop.py covers the report
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. log() prefixes ISO timestamps; launches log frame bytes. 2. report(st) computes task, outcome, elapsed, launches per agent, relaunches, stops, first-try steps, tidy runs, frame bytes. 3. loop.py report and report --all. 4. Tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
test_loop.py 19 tests green incl. report assertions on the happy path, a relaunch, and a stop; check-harness.sh ok.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
log() writes UTC ISO timestamps; launches log frame bytes, relaunches their key, tidy runs their agent; loop.py report and report --all compute metrics from log.md and state.json; orchestrate.md prints the report at DONE. Verified by test_loop.py and check-harness.sh. HD-22.
<!-- SECTION:FINAL_SUMMARY:END -->
