---
type: C4 Component
title: Research packet
status: stable
groma:
  id: packet
  parent: ghostinside-packet
  code:
    - scanner: python
      file: meta/core/tools/packet.py
  technology: Python
description: Prints rules and module files workers need
---

Deterministically prints the shared architecture, persistence, stack and review rules plus existing module and slice files, with file:line citations. The loop calls it as a subprocess once per run for rules and once per module.
