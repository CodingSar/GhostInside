---
id: TASK-2
title: 'init-factory skill: configure a cloned harness for one product'
status: To Do
assignee: []
created_date: '2026-10-10 08:20'
labels: []
dependencies: []
references:
  - PLAN.md
  - meta/registry/runner.md
priority: high
type: feature
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The harness ships with the stack, runner, practices and environment left TBD (decision-3), so the orchestrator stops at preflight until something fills them. init-factory is that something: run by the Opus main thread inside a user-made clone of the template (decision-4), it turns a concept into a ratified product brief, a stack, vendored best-practice packs, a provisioned environment and a green walking skeleton, so Haiku workers start task 1 with a working loop.

Design was settled in a grilling session on 2026-10-10. Decisions: decision-4 (template/clone), decision-5 (propose + ratify at grouped gates: brief, facets, stack+architecture, packs, provision+seed), decision-6 (defaults are supersedable priors), decision-7 (core guides template-owned, stack overlays only), decision-8 (central practices repo).

Pack rule format: ID, MUST/SHOULD, one line, source URL, enforce: lint|check-cmd|test|review. Facets: lang/, framework/, datastore/, domain/, concern/. Research is tiered: deep-research skill for domain/ and concern/ facets, a single research subagent plus official docs for the rest.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Skill exists at `.claude/skills/init-factory/SKILL.md` and runs in the main thread; Haiku workers are not used for init
- [ ] #2 First run creates a Backlog task whose acceptance criteria are the init phases; re-invocation resumes at the first unchecked criterion; each phase ends in its own commit
- [ ] #3 Init adds the template as a `harness` git remote and never creates repositories itself
- [ ] #4 Brief phase reads `CONCEPT.md`, interviews the user on gaps against a fixed checklist (users, core jobs, scale, data sensitivity and compliance, deploy target, integrations, non-goals, language preference) and stores a Backlog doc `product-brief`, ratified at the brief gate
- [ ] #5 Facet phase derives facets under lang/, framework/, datastore/, domain/, concern/ from the brief, ratified at the facets gate
- [ ] #6 Stack phase fills `meta/registry/runner.md` with no TBD left; each choice is a Backlog decision listing rationale and rejected alternatives; decision-1 and decision-2 are replaced only by a ratified superseding decision (a CLI concept with no stored data gets no PostgreSQL)
- [ ] #7 Practices phase pulls matching packs from the central repo, runs a delta check on packs older than 7 days, researches missing facets per the tiered rule, writes packs in the rule format, vendors them into `meta/practices/` with `practices.lock` (pack ids and commit SHA), and compiles lint and check-cmd rules into tool config
- [ ] #8 Newly researched packs are used locally after user approval and opened as a PR on the central repo; an unreachable central repo does not stop init, it is reported
- [ ] #9 Provision phase writes datastore compose file, toolchain pin, CI workflow running the registry lint and test commands, devcontainer, stack permissions in `.claude/settings.json`, and overlays in `meta/guides/stack/`; core guides are unchanged
- [ ] #10 Seed phase creates milestones and one Backlog draft per candidate slice, each criterion traced to the brief or marked ASSUMED:
- [ ] #11 Exit gate: a trivial health slice runs through the real test runner and real datastore, tests green, `meta/tools/check-harness.sh` passes
- [ ] #12 Re-running on an initialized clone enters amend mode: it asks only about deltas between the new concept and `product-brief` and proposes superseding decisions
<!-- AC:END -->
