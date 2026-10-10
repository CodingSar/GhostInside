---
id: TASK-5
title: >-
  Harness v2: core/product layers, modular slice architecture, deterministic
  packet
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-10 09:01'
updated_date: '2026-10-10 09:02'
labels: []
dependencies: []
modified_files:
  - backlog/config.yml
  - meta/core/backlog
  - AGENTS.md
priority: high
type: enhancement
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review on 2026-10-10 found that template-owned defaults and init-written product values share files (merge conflicts on harness upgrades), the template backlog ships into product clones (ID collisions), the product architecture is a flat slice list with no nesting, composition root, catalog or size limits, nothing mechanically keeps product code small, behaviour changes deadlock because no worker may touch old tests, the searcher copies static files probabilistically, rules are duplicated across files and core guides hardcode supersedable defaults. The user asked for maximum structure, small maintainable product code, slice-based architecture with clear nesting, in both the harness and what it generates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Template-owned files live under meta/core/, init-factory-written files under meta/product/; a product file overrides the core default of the same name; check-harness fails in a clone when meta/core/ differs from the merge base with harness/main
- [ ] #2 Harness development backlog lives in meta/core/backlog/ (used with BACKLOG_CWD=meta/core); root backlog/ is the product backlog and the template ships it empty
- [ ] #3 Harness decisions have rationale in meta/core/decisions.md as HD-n, one-to-one with harness backlog decision-n
- [ ] #4 Default product architecture is modules containing use-case slices, with app/ composition root, shared/ kernel, _about.md catalogs, import rules, forbidden folder names and size caps
- [ ] #5 meta/core/tools/structure.py checks layout, catalogs, forbidden names and size caps deterministically, with tests; init-factory wires it, a boundary checker, duplication and dead-code checks into one check command
- [ ] #6 Searcher worker is replaced by deterministic meta/core/tools/packet.sh
- [ ] #7 Guides support changing behaviour (plan lists tests to retire, test-writer edits only those), a tidy step after green, and test names carrying TASK-n#k
- [ ] #8 Each rule has one home: generic testing practice merged into the test guide, dead domain-row mechanism removed, agent files only point to their guide, core guides cite the stack datastore instead of PostgreSQL
- [ ] #9 init-factory matches the 5 grouped gates of HD-5 and records one stack decision instead of one per row
- [ ] #10 README is a human entry, PLAN.md becomes DESIGN.md without status lists, governance merged into AGENTS.md, template settings carry no stack or personal entries, and a PreToolUse guard blocks force-push and recursive force-remove variants
- [ ] #11 meta/core/tools/check-harness.sh passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Move harness backlog to meta/core/backlog; ship empty product backlog/ at root.
2. Split meta/ into meta/core (template-owned: guides, defaults, tools, decisions.md) and meta/product (stack.md, overlays/, practices/); update every path.
3. Rewrite default architecture: modules > slices, app/, shared/, catalogs, caps; add structure.py + tests.
4. Replace searcher with packet.sh; rewrite guides (single home per rule, retire tests, tidy step, TASK-n#k names); thin agent files.
5. init-factory: new paths, 5 gates, one stack decision, check command with structure/boundary/dup/dead-code, skeleton in module layout.
6. Settings cleanup + guard.py PreToolUse hook with tests.
7. README, DESIGN.md, AGENTS governance merge, check-harness core-unchanged check, prune legacy checks.
Commit and push after each step; check-harness before each commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
step 1: harness backlog moved to meta/core/backlog, empty product backlog/ at root (backlog init, integration none). Verified: root task list empty, BACKLOG_CWD=meta/core lists TASK-1..5.
<!-- SECTION:NOTES:END -->
