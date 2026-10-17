---
id: TASK-19
title: Workers launch without plugins and MCP servers
status: To Do
assignee: []
created_date: '2026-10-17 11:10'
updated_date: '2026-10-17 11:13'
labels: []
dependencies:
  - TASK-17
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every worker launch may carry the parent session plugin skills list and MCP tool schemas in its system prompt, a fixed cost on every Haiku launch for tools the guides never use. User decision 2026-10-17: workers lose plugins and MCP by default. Mechanism depends on what Claude Code offers per agent or per launch; TASK-17 Phase 0 measurement confirms the saving. The guard hook and the deny list stay as they are.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A worker transcript shows no MCP tool schemas and no plugin skills in its context
- [ ] #2 Each agent file or the settings carry the exclusion, and check-harness.sh fails when a worker lacks it
- [ ] #3 decisions.md has an HD row with the measured per-launch saving
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Docs 2026-10-17: tools is an allowlist resolved against the parent pool, so the six built-ins already exclude MCP tools; Skill is already absent. Work left: a check-harness.sh rule (no mcp__ or Skill in a worker tools list, no skills: preload), and the first-turn cache-creation measurement to confirm the prefix size. Verify whether omitClaudeMd also drops AGENTS.md: docs do not say.
<!-- SECTION:NOTES:END -->
