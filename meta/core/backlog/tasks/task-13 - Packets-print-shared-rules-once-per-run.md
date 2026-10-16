---
id: TASK-13
title: Packets print shared rules once per run
status: To Do
assignee: []
created_date: '2026-10-16 20:30'
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
- [ ] #1 packet.py --rules prints only the effective architecture, persistence, stack, and review rules
- [ ] #2 packet.py <module> [<slice>] --no-rules prints only the catalog, module, and slice sections and the notes
- [ ] #3 loop.py writes packets/rules.md once per run and one module packet per module without the rules, and frames list rules.md first
- [ ] #4 test_packet.py and test_loop.py cover both modes
<!-- AC:END -->
