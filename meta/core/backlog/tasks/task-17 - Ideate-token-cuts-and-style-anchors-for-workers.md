---
id: TASK-17
title: Ideate token cuts and style anchors for workers
status: To Do
assignee: []
created_date: '2026-10-17 10:57'
updated_date: '2026-10-17 11:13'
labels: []
dependencies:
  - TASK-18
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per-task cost is unmeasured beyond frame bytes, and the biggest suspected costs (inherited plugin and MCP schemas on every launch, guides read instead of cached, whole-file packets) are unverified. Separately, a few canonical software-engineering terms or a named exemplar codebase may steer Haiku toward better code at near-zero token cost, but only an experiment can say. Plan of the ideation, candidates ranked, and the decisions it needs: `.scratch/ideation-plan.md` (2026-10-17). Blocked on a fixture product (handoff decision 3).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Per-launch token accounting (input, output, cache read, cache write, bucketed by source) appears in loop.py report
- [ ] #2 Each Phase 1 candidate has a measured saving or a recorded rejection with numbers
- [ ] #3 The style-anchor experiment (none, word list, named exemplar, few-shot) has run on the fixture tasks with first-pass green rate, gaps, and tokens per arm
- [ ] #4 Every winner is a harness task plus an HD row; every loser is a rejected alternative with its numbers
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Phase 0 findings 2026-10-17: subagent transcripts at ~/.claude/projects/<proj>/<session>/subagents/agent-<id>.jsonl carry per-assistant-message usage (input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens); undocumented, format may change, parse defensively. SubagentStop hook stdin has agent_id, agent_type, agent_transcript_path: the hook can sum usage per launch into log.md. General-purpose launches here: 24k-31k tokens of cache creation on turn one (system prompt prefix). No harness worker transcript exists yet; the template has no stack. Subagent cache is separate from the parent, 5m TTL default; subagentPromptCacheTtl setting or frontmatter experimental.cacheTtl raises to 1h. Decisions ratified: HD-25 fixture clone (TASK-18), HD-26 no plugins or MCP for workers (TASK-19), HD-27 guide in agent body (TASK-20).
<!-- SECTION:NOTES:END -->
