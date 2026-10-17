---
type: C4 Actor
title: Maintainer
status: stable
groma:
  id: maintainer
---

Runs the main-thread session, answers ASK questions and resolves STOPs.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [maintainer](maintainer.md) | [meta/core/tools/loop.py](../../meta/core/tools/loop.py) | Starts and resolves runs | CLI |
