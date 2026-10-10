---
id: TASK-5
title: >-
  Harness v2: core/product layers, modular slice architecture, deterministic
  packet
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-10 09:01'
updated_date: '2026-10-10 09:14'
labels: []
dependencies: []
modified_files:
  - backlog/config.yml
  - meta/core/backlog
  - AGENTS.md
  - .claude/agents/implementer.md
  - .claude/agents/searcher.md
  - .claude/agents/test-writer.md
  - .claude/skills/init-factory/SKILL.md
  - .claude/skills/init-factory/phases/facets.md
  - .claude/skills/init-factory/phases/practices.md
  - .claude/skills/init-factory/phases/provision.md
  - .claude/skills/init-factory/phases/seed.md
  - .claude/skills/init-factory/phases/skeleton.md
  - .claude/skills/init-factory/phases/stack.md
  - meta/_about.md
  - meta/core/decisions.md
  - meta/core/defaults/architecture.md
  - meta/core/defaults/persistence.md
  - meta/core/defaults/testing.md
  - meta/core/design.md
  - meta/core/guides/implement.md
  - meta/core/guides/orchestrate.md
  - meta/core/guides/search.md
  - meta/core/guides/test.md
  - meta/core/tools/check-harness.sh
  - meta/core/tools/practices.py
  - meta/core/tools/test_practices.py
  - meta/docs/harness-review.md
  - meta/guides/stack/_about.md
  - meta/practices/_about.md
  - meta/product/_about.md
  - meta/product/practices/enforced.md
  - meta/product/practices/practices.lock
  - meta/product/practices/review.md
  - meta/product/stack.md
  - meta/registry/_about.md
  - meta/tools/check-harness.sh
  - >-
    meta/core/backlog/decisions/decision-11 -
    Default-product-architecture-modules-of-use-case-slices-app-composition-root-shared-kernel-catalogs-size-caps-enforced-by-structure.py-amends-decision-1.md
  - meta/core/tools/structure.py
  - meta/core/tools/test_structure.py
  - .gitignore
  - >-
    meta/core/backlog/decisions/decision-12 -
    Searcher-worker-replaced-by-deterministic-packet.py.md
  - >-
    meta/core/backlog/decisions/decision-13 -
    Behaviour-changes-retire-named-tests-tidy-step-after-green-test-names-carry-TASK-nk.md
  - >-
    meta/core/backlog/tasks/task-5 -
    Harness-v2-core-product-layers-modular-slice-architecture-deterministic-packet.md
  - meta/core/tools/packet.py
  - meta/core/tools/test_packet.py
  - >-
    meta/core/backlog/decisions/decision-14 -
    init-factory-five-gates-per-HD-5-provision-and-seed-share-one-skeleton-has-none-one-stack-decision-instead-of-one-per-row.md
  - .claude/settings.json
  - meta/core/tools/guard.py
  - meta/core/tools/test_guard.py
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
- [ ] #6 Searcher worker is replaced by deterministic meta/core/tools/packet.py, with tests
- [ ] #7 Guides support changing behaviour (plan lists tests to retire, test-writer edits only those), a tidy step after green, and test names carrying TASK-n#k
- [ ] #8 Each rule has one home: generic testing practice merged into the test guide, dead domain-row mechanism removed, agent files only point to their guide, core guides cite the stack datastore instead of PostgreSQL
- [ ] #9 init-factory matches the 5 grouped gates of HD-5 and records one stack decision instead of one per row
- [ ] #10 README is a human entry, PLAN.md becomes meta/core/design.md without status lists, governance merged into AGENTS.md, template settings carry no stack or personal entries, and a PreToolUse guard blocks force-push and recursive force-remove variants
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

step 2: meta split into core/ (guides, defaults, tools, decisions.md, design.md, backlog) and product/ (stack.md, practices/, overlays/ later). decisions.md HD-1..HD-10 with rationale; decision-9/10 created in harness backlog; citations renamed decision-n -> HD-n. harness-review.md merged into AGENTS.md Governance. check-harness: optional product refs, tests glob, clone check (template-owned paths vs merge-base with harness/main) - verified FAIL on edited core guide in scratch clone, ok when clean.

step 3: architecture.md rewritten (modules > slices, app/, shared/, catalogs, import rules, forbidden names, caps); persistence.md per-module tables; structure.py + test_structure.py (9 tests green); HD-11 / decision-11.

step 4: packet.py + test_packet.py (6 tests) replace searcher (HD-12); orchestrate/test/implement guides rewritten: packet, retire list, catalogs after test-first, tidy step, TASK-n#k names, real datastore from stack.md (HD-13); generic testing practice merged into test.md and deleted; search.md, searcher agent removed; agents reduced to pointer to guide; stack.md gains source root, extensions, test file pattern, check command rows; __pycache__ untracked and ignored.

step 5: init-factory: product layer paths, never-change list = meta/core + core agents/skill/AGENTS/CLAUDE; five gates (provision+seed shared, skeleton none), one stack decision (HD-14); stack phase proposes boundary, duplication, dead-code checkers and writes scripts/check.sh with structure.py; practices append check-cmd rules to check.sh; provision writes README and overlays with TASK-n#k idiom; seed proposes modules and module/slice drafts labelled module:<m>; skeleton is a health module with app/ wiring.

step 6: guard.py PreToolUse hook (force push in all spellings incl. +refspec, --force-with-lease, -uf, git -C; rm with recursive+force flags in any order; sudo; nested bash -c/eval/env/xargs) + test_guard.py (3 tests, 37 cases); verified live: hook blocked rm -fr in this session. settings.json: stack-specific allows (npm, npx, node, make) removed (init adds them); CAVEMAN env moved to gitignored .claude/settings.local.json; deny list unchanged.
<!-- SECTION:NOTES:END -->
