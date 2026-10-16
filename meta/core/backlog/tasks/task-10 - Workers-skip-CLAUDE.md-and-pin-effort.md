---
id: TASK-10
title: Workers skip CLAUDE.md and pin effort
status: Done
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:33'
labels: []
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every worker subagent receives AGENTS.md (Backlog "run overview first", Groma) although the guides are self-contained: wasted tokens and instructions a Haiku worker may follow. Anthropic reports that effort low->medium halved early stopping on Haiku 5.5. Research 2026-10-16: code.claude.com/docs/en/sub-agents, prompting-claude-haiku-5-5.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every agent in .claude/agents sets omitClaudeMd: true and an explicit effort
- [x] #2 check-harness.sh fails when a loop agent lacks omitClaudeMd or effort
- [x] #3 The guard hook still blocks harness writes and git state changes for subagents (test_guard.py green)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add omitClaudeMd: true and effort: medium to every agent in .claude/agents. 2. Extend check-harness.sh to require both keys on loop agents. 3. Run check-harness.sh and test_guard.py.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
check-harness.sh green with the new rule; test_guard.py OK. Commit on main.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added omitClaudeMd: true and effort: medium to all five agents, check-harness.sh rule 3 requires both, HD-18 records why. Verified with check-harness.sh (ok) and test_guard.py (OK).
<!-- SECTION:FINAL_SUMMARY:END -->
