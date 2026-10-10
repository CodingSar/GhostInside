---
id: TASK-2
title: 'init-factory skill: configure a cloned harness for one product'
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-10 08:20'
updated_date: '2026-10-10 08:48'
labels: []
dependencies: []
references:
  - PLAN.md
  - meta/registry/runner.md
modified_files:
  - meta/tools/practices.py
  - meta/tools/test_practices.py
  - .gitignore
  - meta/guides/orchestrate.md
  - meta/guides/search.md
  - meta/guides/test.md
  - meta/guides/implement.md
  - .claude/agents/searcher.md
  - .claude/agents/test-writer.md
  - .claude/agents/implementer.md
  - meta/guides/stack/_about.md
  - meta/practices/_about.md
  - meta/practices/practices.lock
  - meta/practices/review.md
  - meta/practices/enforced.md
  - .claude/skills/init-factory/SKILL.md
  - .claude/skills/init-factory/phases/brief.md
  - .claude/skills/init-factory/phases/facets.md
  - .claude/skills/init-factory/phases/stack.md
  - .claude/skills/init-factory/phases/practices.md
  - .claude/skills/init-factory/phases/provision.md
  - .claude/skills/init-factory/phases/seed.md
  - .claude/skills/init-factory/phases/skeleton.md
  - meta/tools/check-harness.sh
  - meta/_about.md
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
- [ ] #5 Facet phase derives domain/ and concern/ facets from the brief, ratified at the facets gate; stack phase adds lang/, framework/, datastore/ facets from the ratified stack, ratified at the stack gate
- [ ] #6 Stack phase fills `meta/registry/runner.md` with no TBD left; each choice is a Backlog decision listing rationale and rejected alternatives; decision-1 and decision-2 are replaced only by a ratified superseding decision (a CLI concept with no stored data gets no PostgreSQL)
- [ ] #7 Practices phase pulls matching packs from the central repo, runs a delta check on packs older than 7 days, researches missing facets per the tiered rule, writes packs in the rule format, vendors them into `meta/practices/` with `practices.lock` (pack ids and commit SHA), and compiles lint and check-cmd rules into tool config
- [ ] #8 Newly researched packs are used locally after user approval and opened as a PR on the central repo; an unreachable central repo does not stop init, it is reported
- [ ] #9 Provision phase writes datastore compose file, toolchain pin, CI workflow running the registry lint and test commands, devcontainer, stack permissions in `.claude/settings.json`, and overlays in `meta/guides/stack/`; core guides are unchanged
- [ ] #10 Seed phase creates milestones and one Backlog draft per candidate slice, each criterion traced to the brief or marked ASSUMED:
- [ ] #11 Exit gate: a trivial health slice runs through the real test runner and real datastore, tests green, `meta/tools/check-harness.sh` passes
- [ ] #12 Re-running on an initialized clone enters amend mode: it asks only about deltas between the new concept and `product-brief` and proposes superseding decisions
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Skill entry: `.claude/skills/init-factory/SKILL.md` (Opus main thread only). Preflight: refuse when origin is the template (git@github.com:CodingSar/GhostInside.git) and offer to rename origin to `harness` and add the product remote; require shared history with `harness/main` (plain git clone, not the GitHub template button). Resume: find the init task by label `init-factory`; create it with one AC per phase when absent; continue at the first unchecked AC. Amend: init task Done and `product-brief` exists -> new init task in amend mode. AC 1-3, 12.
2. Phase references in `.claude/skills/init-factory/phases/`: `brief.md` (checklist: users, core jobs, scale, data sensitivity and compliance, deploy target, integrations, non-goals, language preference; output Backlog doc `product-brief`), `facets.md` (facet kinds and derivation), `stack.md`, `practices.md`, `provision.md`, `seed.md`, `skeleton.md`. Each phase ends at its gate table (proposal, rationale, rejected alternatives), then commit. AC 4-5, 10.
3. Rationale store: decision CLI has no body, so each init decision gets a row in Backlog doc `init-decisions` (decision id, choice, rationale, rejected alternatives); decision title names the choice. AC 6.
4. Deterministic helper `meta/tools/practices.py` (python3 stdlib, harness-only, not the product stack): `status <facet ids>` -> hit/stale(>7d)/miss against central index.json; `check <pack file>` -> front matter and rule table format; `vendor <ids>` -> copy packs to `meta/practices/packs/`, write `meta/practices/practices.lock` (repo, sha, ids), regenerate `meta/practices/review.md` from review-level rules; `verify` -> lock matches vendored files; `propose <pack file>` -> branch in a scratch clone of the central repo, add pack + index entry, `gh pr create`. AC 7-8.
5. Searcher wiring: add topic `practices:review` -> `meta/practices/review.md` in `meta/guides/search.md` and `.claude/agents/searcher.md`; orchestrator step 3 passes it. Update `meta/practices/_about.md`. AC 7.
6. Stack overlays: create `meta/guides/stack/_about.md`; core guides orchestrate/test/implement get one line each: read the overlay for this guide in `meta/guides/stack/` when it exists. AC 9.
7. Provision phase spec: compose file for the datastore, toolchain pin, CI workflow mirroring registry lint/test commands, devcontainer, allow-only additions to `.claude/settings.json` (denies untouched per meta/docs/harness-review.md rule 5), overlays. AC 9.
8. Seed and skeleton specs: milestones via `backlog milestone add`, drafts via `backlog task create --draft` with criteria traced to `product-brief` or `ASSUMED:`; health slice in vertical-slice layout through the real runner and datastore; exit gate = full tests green, lint green, `check-harness.sh` passes, registry no TBD. AC 10-11.
9. check-harness: scan `.claude/skills` for path refs; when `meta/practices/practices.lock` exists, run `practices.py verify`; when the init task is Done, fail on TBD in `meta/registry/runner.md`.
10. Docs: `meta/_about.md`, `PLAN.md` Parts row for init-factory. Verify: `practices.py` self-test on fixture packs in scratchpad, `check-harness.sh` green, dry read of SKILL.md against each AC. AC 1-12 coverage reviewed; full behavioural proof is TASK-4.

Note: step 4 tests are committed as meta/tools/test_practices.py (temp dirs, local bare repo as central, fake gh) instead of a scratchpad-only self-test, so check-harness can rerun them.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
step 4: practices.py fetch/status/check/vendor/verify/propose; 7 unittest cases green; fetch+status against real central: 6acaf49, both facets miss (empty index).

steps 5-6: searcher topic practices:review (search.md, searcher agent, orchestrator step 3), review rules passed to test-writer and implementer; overlay hook line in orchestrate/test/implement; meta/guides/stack/_about.md; practices/_about.md documents packs, lock, review.md, enforced.md. vendor accepts an empty set; template ships empty vendored state (lock at central 6acaf49), verify ok.

steps 1-3, 7-8: SKILL.md (preflight template guard + shared history, init/resume/amend via label init-factory, 8 phase ACs, gate format, decisions + init-decisions doc, stop rules) and phases/{brief,facets,stack,practices,provision,seed,skeleton}.md. Facets phase covers domain/concern only; stack phase adds lang/framework/datastore facets, since they follow from the stack choice. Seed uses task create --draft (draft create lacks --ac/-m).
step 9: check-harness scans .claude/skills refs, runs practices.py verify when lock exists, runs test_practices.py, fails on TBD once runner.md Status is no longer TBD (marker is the Status line, not the init task state, so the check needs no Backlog parsing). Negative cases verified: TBD with set status, edited review.md, broken skill path each FAIL.
step 10: meta/_about.md, PLAN parts row.

AC5 reworded: lang/framework/datastore facets follow from the stack choice, so they are ratified at the stack gate, not the facets gate. Order of criteria unchanged.

Independent review (reviewer subagent): 2 high, 14 medium, 18 low; all addressed. Highs: unreachable central now a non-stop path in facets/practices; stack phase now scaffolds manifest, lockfile, linter and test config and runs install before practices compiles lint rules. Registry gains rows: framework, install command, source root, datastore, connection variable, migration command. propose is resume-safe (content-hashed branch, reuses pushed branch and open PR) and exits 3 with the branch name when gh is missing or fails; GHOSTINSIDE_GH makes gh injectable for tests; 8 tests green. SKILL: task-creation guide, preflight commit, check-harness before meta/.claude commits, resume rows for several unfinished or Done-without-brief, URL normalization, no repo creation, decision granularity, real newlines. Seed source tags [brief: f] / [pack: id rule]. Skeleton: CI run located by commit sha; without gh criterion 8 stays unchecked.
<!-- SECTION:NOTES:END -->
