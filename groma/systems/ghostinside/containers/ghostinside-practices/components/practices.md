---
type: C4 Component
title: Practice packs
status: stable
groma:
  id: practices
  parent: ghostinside-practices
  code:
    - scanner: python
      file: meta/core/tools/practices.py
  technology: Python
description: Fetches, checks, vendors and verifies practice packs
---

Mechanical half of practice packs: compares facets with the central repo cache, validates pack format, vendors packs with a lock, verifies the lock and proposes new packs as a PR.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [meta/core/tools/practices.py](../../../../../../meta/core/tools/practices.py) | [central-practices-repo](../../../../../externals/central-practices-repo.md) | Fetches and proposes packs | git |
