---
id: TASK-6
title: 'Screens: mockup-first requirements for products with a GUI'
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-10 11:14'
updated_date: '2026-10-10 11:15'
labels:
  - init-factory
  - orchestrator
dependencies: []
modified_files:
  - .claude/skills/init-factory/phases/brief.md
  - .claude/skills/init-factory/phases/screens.md
  - .claude/skills/init-factory/SKILL.md
  - .claude/skills/init-factory/phases/facets.md
  - .claude/skills/init-factory/phases/seed.md
  - meta/core/guides/orchestrate.md
  - meta/core/decisions.md
  - meta/core/design.md
  - meta/product/_about.md
  - README.md
  - meta/core/tools/check-harness.sh
priority: high
type: enhancement
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Requirements reach the factory only as text: CONCEPT.md, the product brief, and criteria in the user's words. For a product with a graphical interface, users react to a screen far more precisely than to prose, and a mockup surfaces missing states, navigation, and the data each screen needs before any plan exists. The harness had no step that shows the user a screen. Products without a GUI (CLI, API, library) must not pay for this step. Mockups are throwaway static HTML for eliciting answers, never product code; a working UI stays the walking skeleton's job. A visual verify step (screenshot of the real screen beside the mockup) is deferred until a UI stack exists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The brief checklist has an `interface` field that says whether the product has a GUI
- [ ] #2 init-factory has a screens phase between brief and facets: static HTML mockups of the core jobs' screens, shown to the user, an interview on what they expose, a gate, and a Backlog doc `product-screens`
- [ ] #3 A product whose interface has no GUI skips the screens phase and its gate; the criterion is checked with `n/a` evidence
- [ ] #4 Mockups live in `meta/product/screens/`, are self-contained static HTML marked as mockups, and are never copied into the source root
- [ ] #5 Seed drafts may carry a `[screen: <id>]` source tag, and every action in `product-screens` maps to at least one draft
- [ ] #6 Orchestrator intake for a task that adds or changes a screen updates its mockup and gets the user's confirmation before criteria are final; criteria may carry `[screen: <id>]`
- [x] #7 Harness decision HD-15 records the screens gate and amends HD-5 and HD-14; design.md, decisions.md, catalogs, and README match
- [x] #8 `meta/core/tools/check-harness.sh` passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. brief.md: add `interface` field (web, mobile, desktop GUI, CLI, API, library). AC1.
2. New phase .claude/skills/init-factory/phases/screens.md: skip rule for no GUI; mockup rules (static HTML, self-contained, MOCKUP banner, states, links); show via Artifact tool or file paths; interview; gate; doc product-screens; files in meta/product/screens/; Amend. AC2-4.
3. SKILL.md: new criterion 3, renumber, phase table, six gates, allowed paths. AC2-3.
4. facets.md: interface field raises concern facets. seed.md: [screen: <id>] tag, every screen action maps to a draft. AC5.
5. orchestrate.md intake: screen step for GUI tasks, source tag, verify diff allows mockup files. AC6.
6. HD-15 decision (harness backlog) + decisions.md rows, design.md, meta/product/_about.md, README, check-harness optional path. AC7.
7. Run check-harness.sh. Commit, push. AC8.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented plan steps 1-7. HD-15 = decision-15.
Evidence: check-harness.sh -> "ok: harness checks passed"; brief.md has `interface` row; decisions.md HD-5/HD-14 marked amended by HD-15; design.md, README, meta/product/_about.md updated.
Open: AC 2-6 describe procedure behaviour; they are written but unproven until a dry run of init-factory and orchestrator intake on a GUI and a non-GUI concept (TASK-4 eval fixtures).
<!-- SECTION:NOTES:END -->
