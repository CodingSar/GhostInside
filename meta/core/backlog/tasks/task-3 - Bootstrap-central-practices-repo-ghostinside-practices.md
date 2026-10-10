---
id: TASK-3
title: Bootstrap central practices repo ghostinside-practices
status: Done
assignee:
  - '@claude'
created_date: '2026-10-10 08:20'
updated_date: '2026-10-10 08:27'
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
- [x] #1 Repo exists on GitHub under the user account and is reachable with gh
- [x] #2 Top-level facet directories lang/, framework/, datastore/, domain/, concern/
- [x] #3 `index.json` lists every pack with facet id, path and researched date
- [x] #4 README documents the pack rule format (ID, MUST/SHOULD, one line, source URL, enforce) and the PR-and-human-merge rule
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Clone empty repo to scratchpad.
2. Add facet dirs lang/ framework/ datastore/ domain/ concern/ with .gitkeep.
3. Add index.json (version 1, empty packs list) and README documenting pack file format, rule table, index schema, staleness, PR-and-human-merge rule.
4. Commit and push to main.
5. Point PLAN.md at the real repo URL.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Repo: git@github.com:CodingSar/GhostInsidePractices.git (decision-8 title says ghostinside-practices; this is the real name). Bootstrap commit 6acaf49 pushed to main: facet dirs with .gitkeep, index.json {version 1, packs []}, README with pack front matter, rule table columns, index schema, 7-day staleness, PR-and-human-merge rule. Verified: git ls-remote shows refs/heads/main at 6acaf49; index.json parses. AC1 open: gh CLI not installed on this machine; repo reachable over git only. gh is also needed by TASK-2 for PR write-back.

gh installed and authed as CodingSar; gh repo view returns PUBLIC repo, default branch main.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Bootstrapped CodingSar/GhostInsidePractices (commit 6acaf49): facet dirs, empty index.json, README defining pack format, index schema, 7-day delta check and PR-and-human-merge rule. Verified with git ls-remote, json parse of index.json, and gh repo view.
<!-- SECTION:FINAL_SUMMARY:END -->
