---
type: C4 Component
title: Dispatcher loop
status: stable
groma:
  id: loop
  parent: ghostinside-loop
  code:
    - scanner: python
      file: meta/core/tools/loop.py
  technology: Python
description: Runs one Backlog task through the factory
---

Prints one LAUNCH/ASK/DONE/STOP line at a time for the main thread. Runs preflight, baseline suite, red gate, allowlist and plan-diff checks, commits and the final push; agents only supply judgment and end with a RETURN line. State lives in .scratch/<run>/state.json.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [meta/core/tools/loop.py](../../../../../../meta/core/tools/loop.py) | [meta/core/tools/packet.py](../../../../../../meta/core/tools/packet.py) | Prints worker packets | subprocess |
