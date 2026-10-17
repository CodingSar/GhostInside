---
type: C4 Component
title: Structure check
status: stable
groma:
  id: structure
  parent: ghostinside-structure
  code:
    - scanner: python
      file: meta/core/tools/structure.py
  technology: Python
description: Checks module layout, catalogs and size caps
---

Validates the product code layout against meta/core/defaults/architecture.md: module and slice folders, _about.md catalogs, forbidden names and line caps. Import boundaries are left to the stack checker.
