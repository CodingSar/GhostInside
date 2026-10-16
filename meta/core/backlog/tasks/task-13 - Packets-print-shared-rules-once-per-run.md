---
id: TASK-13
title: Packets print shared rules once per run
status: Done
assignee:
  - '@claude'
created_date: '2026-10-16 20:30'
updated_date: '2026-10-16 20:40'
labels: []
dependencies: []
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
packet.py prints architecture, persistence, stack, and review rules in every module packet, so a plan over N modules makes the worker read N copies of the same 250 lines. Repeated coherent text is the strongest distractor for small models (Chroma context rot). Rules once, module content per packet.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 packet.py --rules prints only the effective architecture, persistence, stack, and review rules
- [x] #2 packet.py <module> [<slice>] --no-rules prints only the catalog, module, and slice sections and the notes
- [x] #3 loop.py writes packets/rules.md once per run and one module packet per module without the rules, and frames list rules.md first
- [x] #4 test_packet.py and test_loop.py cover both modes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. packet.py: --rules prints only rules sections; --no-rules skips them. 2. loop.py packets(): rules.md once per run, module packets without rules, rules first in the list. 3. Tests in test_packet.py and test_loop.py.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
test_packet.py 10 tests and test_loop.py 19 tests green; check-harness.sh ok.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
packet.py gained --rules and --no-rules; loop.py packets() writes rules.md once per run and one module packet per module, rules listed first; plan, test, implement guides and design.md updated. Verified by test_packet.py test_rules_once_and_module_without_rules, test_loop.py happy path, check-harness.sh. HD-21.
<!-- SECTION:FINAL_SUMMARY:END -->
