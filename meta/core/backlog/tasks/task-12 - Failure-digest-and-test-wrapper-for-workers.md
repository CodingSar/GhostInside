---
id: TASK-12
title: Failure digest and test wrapper for workers
status: To Do
assignee: []
created_date: '2026-10-16 20:30'
labels: []
dependencies: []
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A relaunch after a failed step or red gate hands the worker a raw log path; the implementer runs the stack test command itself and reads its whole output. Research: tests are the best repair feedback, output to the model should be a few lines with one greppable line per failure and the full log in a file (Anthropic C compiler post, writing-tools-for-agents); retry prompts should restate the goal and append the exact failure (goal plus delta).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 loop.py has a digest of a test run: pass and fail counts from the JUnit report, one line per failing test with its first message line, else the last 10 output lines, at most 20 lines
- [ ] #2 A relaunch after a failed step or red gate restates the step and includes the digest inline, not only the log path
- [ ] #3 python3 -I meta/core/tools/loop.py test <command> runs the command, writes the full output under the run logs, and prints the digest with exit code 0 on green and 1 otherwise
- [ ] #4 implement.md tells the implementer to run tests only through loop.py test
- [ ] #5 test_loop.py covers the digest and the test command
<!-- AC:END -->
