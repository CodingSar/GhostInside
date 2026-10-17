---
type: C4 Component
title: Tool guard
status: stable
groma:
  id: guard
  parent: ghostinside-guard
  code:
    - scanner: python
      file: meta/core/tools/guard.py
  technology: Python
description: Blocks commands and writes the harness forbids
---

PreToolUse hook configured in .claude/settings.json. Blocks force-push, recursive force remove and sudo for everyone; for subagents also blocks git writes, harness-file edits and writes outside the pending frame allowlist read from the loop state.
