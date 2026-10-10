---
id: TASK-5
title: >-
  Harness v2: core/product layers, modular slice architecture, deterministic
  packet
status: Done
assignee:
  - '@claude'
created_date: '2026-10-10 09:01'
updated_date: '2026-10-10 09:29'
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
  - README.md
  - >-
    meta/core/backlog/tasks/task-2 -
    init-factory-skill-configure-a-cloned-harness-for-one-product.md
  - meta/core/backlog/tasks/task-4 - Eval-fixtures-for-init-factory.md
  - backlog/completed/.gitkeep
  - backlog/decisions/.gitkeep
  - backlog/docs/.gitkeep
  - backlog/drafts/.gitkeep
  - backlog/milestones/.gitkeep
  - backlog/tasks/.gitkeep
  - meta/core/backlog/archive/.gitkeep
  - meta/core/backlog/completed/.gitkeep
  - meta/core/backlog/docs/.gitkeep
  - meta/core/backlog/drafts/.gitkeep
  - meta/core/backlog/milestones/.gitkeep
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
- [x] #1 Template-owned files live under meta/core/, init-factory-written files under meta/product/; a product file overrides the core default of the same name; check-harness fails in a clone when meta/core/ differs from the merge base with harness/main
- [x] #2 Harness development backlog lives in meta/core/backlog/ (used with BACKLOG_CWD=meta/core); root backlog/ is the product backlog and the template ships it empty
- [x] #3 Harness decisions have rationale in meta/core/decisions.md as HD-n, one-to-one with harness backlog decision-n
- [x] #4 Default product architecture is modules containing use-case slices, with app/ composition root, shared/ kernel, _about.md catalogs, import rules, forbidden folder names and size caps
- [x] #5 meta/core/tools/structure.py checks layout, catalogs, forbidden names and size caps deterministically, with tests; init-factory wires it, a boundary checker, duplication and dead-code checks into one check command
- [x] #6 Searcher worker is replaced by deterministic meta/core/tools/packet.py, with tests
- [x] #7 Guides support changing behaviour (plan lists tests to retire, test-writer edits only those), a tidy step after green, and test names carrying TASK-n#k
- [x] #8 Each rule has one home: generic testing practice merged into the test guide, dead domain-row mechanism removed, agent files only point to their guide, core guides cite the stack datastore instead of PostgreSQL
- [x] #9 init-factory matches the 5 grouped gates of HD-5 and records one stack decision instead of one per row
- [x] #10 README is a human entry, PLAN.md becomes meta/core/design.md without status lists, governance merged into AGENTS.md, template settings carry no stack or personal entries, and a PreToolUse guard blocks force-push and recursive force-remove variants
- [x] #11 meta/core/tools/check-harness.sh passes
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

step 7: README rewritten as human entry (start a product, layout, harness work); meta/core/design.md rewritten without status/next (layers table, parts, flow with tidy, product code, evaluation); meta/_about.md lists all tools. TASK-5 ACs reworded to what was built (packet.py, design.md). Notes added to TASK-2 and TASK-4 mapping old paths.

review fixes A (findings 1,2,18): .gitkeep in every backlog folder (root and meta/core) - verified decision and draft creation in a fresh clone; preflight runs git push -u origin main after the remote rename and every push names origin main; first-run clean tree allows an untracked CONCEPT.md.

review fixes B (findings 3,17): guard.py checks newline-separated commands, shell keywords and braces, wrappers with value options (timeout, nice, env -u, xargs -n), bash flag groups containing c, backticks and $(...), find -exec/-execdir, unique long-option abbreviations for push and rm; unbalanced quotes fall back to word split. 22 new blocked and 6 new allowed cases; tests green. Heredocs whose lines look like blocked commands are blocked (conservative).

review fixes D (findings 9-14,20,25): stack.md rows name case, entry file stems, fix command; cells must be bare values. structure.py: --case, extension list tolerant of spaces, catalog requires backticked names (12 tests). packet.py: tolerant table parsing, distinct errors for missing file, missing row, TBD, non-path value; entry stems from stack (9 tests). Stack phase: case/stems passed to structure.py, duplication ignores tests, scaffold includes app/ entry so checkers have input, test runner must collect same-named test files; architecture overrides must keep the module/slice skeleton. Seed and skeleton use the stack's name case and stems.

review fixes C+E (findings 4-8,15,16,19,21-24): orchestrator records start sha, checks git status against each step's allowlist, diffs start..HEAD at verify, commits per step and pushes once after verify; intake accepts existing/promoted tasks and init source tags; plan adds app/ wiring step, Retire (delete | rewrite as TASK-n#k) and Change lines; fix command after test-writer and before check; test-file findings go to test-writer tidy mode; outside-plan findings stop the task. test guide: change lines, new-module tables, size cap stop, tidy run. Overlay reset tolerates missing tables. design.md: handler-level behaviour tests are the acceptance evidence. AGENTS: product tasks push after green. check-harness: product guides accepted for added workers; in clones deny entries and hooks compared with merge base (verified FAIL on removed deny, ok on added allow).

Validation: test_guard, test_packet, test_practices, test_structure all OK; check-harness ok; scratch clones: core-path edit FAILs, removed deny FAILs, added allow ok; fresh clone creates decisions and drafts; root backlog empty; 14 harness decisions = 14 HD rows; guard hook blocked rm -fr live in this session. Independent review (25 findings) all addressed in commits e9bf097..96ef3cc.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Harness v2. Layers: meta/core (template-owned, enforced in clones by check-harness against the merge base, including settings deny/hooks) and meta/product (stack.md, overlays, practices, optional overrides). Harness backlog moved to meta/core/backlog; root backlog ships empty with tracked folders. Decisions get rationale in meta/core/decisions.md (HD-1..HD-14). Product architecture: modules owning tables with flat use-case slices, app/ composition root, shared/ kernel, backticked _about.md catalogs, import rules, forbidden catch-all names, size caps; structure.py enforces layout, catalogs, names, case and caps; init wires it with boundary, duplication and dead-code checkers into scripts/check.sh plus a fix command. Searcher replaced by deterministic packet.py. Orchestrator: start sha, per-step allowlist check, Retire/Change lines, app/ wiring step, tidy step (implementer or test-writer), push once green, accepts promoted drafts. One home per rule; agents point to guides; init-factory has five gates and one stack decision. README and design doc rewritten; governance in AGENTS.md; guard.py PreToolUse hook blocks force-push, recursive force-remove and sudo in all tested spellings. Verified with four tool test suites, check-harness, scratch-clone negative tests, a live hook block, and an independent review whose 25 findings were fixed.
<!-- SECTION:FINAL_SUMMARY:END -->
