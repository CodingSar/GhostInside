---
id: TASK-3
title: Bootstrap central practices repo ghostinside-practices
status: To Do
assignee: []
created_date: '2026-10-10 08:20'
labels: []
dependencies: []
priority: high
type: chore
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
init-factory (TASK-2) reads facet packs from a central repo and PRs new ones back (decision-8). The repo does not exist yet. The user creates it by hand so init never makes repositories; this task defines what the repo must contain so init can rely on it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Repo exists on GitHub under the user account and is reachable with gh
- [ ] #2 Top-level facet directories lang/, framework/, datastore/, domain/, concern/
- [ ] #3 `index.json` lists every pack with facet id, path and researched date
- [ ] #4 README documents the pack rule format (ID, MUST/SHOULD, one line, source URL, enforce) and the PR-and-human-merge rule
<!-- AC:END -->
