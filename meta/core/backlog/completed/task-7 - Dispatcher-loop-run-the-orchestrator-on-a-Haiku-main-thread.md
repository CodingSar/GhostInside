---
id: TASK-7
title: 'Dispatcher loop: run the orchestrator on a Haiku main thread'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-10 16:08'
updated_date: '2026-10-10 16:19'
labels:
  - orchestrator
  - tools
  - hooks
dependencies: []
modified_files:
  - meta/core/tools/loop.py
  - meta/core/tools/test_loop.py
  - .gitignore
  - meta/core/guides/intake.md
  - meta/core/guides/plan.md
  - meta/core/guides/research.md
  - meta/core/guides/test.md
  - meta/core/guides/implement.md
  - meta/core/guides/orchestrate.md
  - .claude/agents/intake.md
  - .claude/agents/planner.md
  - .claude/agents/researcher.md
  - .claude/agents/test-writer.md
  - .claude/agents/implementer.md
  - .claude/settings.json
  - meta/core/tools/check-harness.sh
  - meta/product/stack.md
  - .claude/skills/init-factory/phases/stack.md
  - .claude/skills/init-factory/phases/skeleton.md
  - meta/core/decisions.md
  - meta/core/design.md
  - AGENTS.md
  - README.md
  - meta/_about.md
priority: high
type: feature
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Everything in the factory runs on Haiku, the main thread included; only research may use a bigger model. The orchestrator ran in the main thread and held the whole procedure, every worker result, and raw test and check output in context, which a Haiku main thread cannot carry through a task. Subagents cannot launch subagents and headless launch is banned, so orchestration cannot move into a subagent. Instead the main thread becomes a trampoline: a deterministic script holds the state machine and runs every deterministic step, judgment goes to fresh Haiku subagents, and a subagent that needs another agent or the user returns a typed request that the main thread carries out, with the call stack kept as frames on disk in `.scratch/`. User confirmed both hooks and orchestrator-first scope on 2026-10-10; init-factory moves onto the same loop in a follow-up.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `meta/core/tools/loop.py` runs one task from intake to Done through `start`, `next`, `done`, and `status`; `next` prints exactly one of LAUNCH, ASK, DONE, STOP and runs every deterministic step itself (preflight, activate, red gate, targeted and full tests, allowlist and plan-diff checks, tidy routing, close-out, commits, push)
- [x] #2 Every agent ends with one typed line: RETURN ok, call, ask, deviation, or blocked; `loop.py done` rejects a malformed line with one relaunch, then STOP
- [x] #3 A RETURN call pushes a frame in `.scratch/<run>/`; when the callee returns ok, the caller is relaunched with a resume frame holding its earlier output and the callee result; only listed edges are allowed and depth is capped at 3
- [x] #4 RETURN ask produces ASK with a question file and an answer file; the main thread asks the user, writes the answer, and the asking agent resumes with it
- [x] #5 All run state is on disk: after /clear, `loop.py next` repeats the pending instruction or continues
- [x] #6 A SubagentStop hook blocks a loop agent from finishing without a valid RETURN line; a Stop hook blocks the main thread from ending while a run is pending, except at ASK, DONE, or STOP
- [x] #7 The red gate and criterion evidence come from the JUnit XML report named in `meta/product/stack.md`; a criterion is checked only when its `TASK-n#k` test passed
- [x] #8 Judgment roles are agents with guides and the RETURN grammar: intake, planner, test-writer, implementer (Haiku) and researcher (the only non-Haiku agent); `orchestrate.md` becomes the short dispatcher procedure
- [x] #9 `meta/core/tools/test_loop.py` covers return parsing, call and resume, ask, resume after restart, plan parsing, the red gate, the allowlist check, and both hooks; `check-harness.sh` passes
- [x] #10 HD-16 records the design; design.md, AGENTS.md, decisions.md, catalogs, and the stack template match
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. meta/core/tools/loop.py: state machine (intake, activate, plan, red, step, tidy, verify, close, push), frames and stack in .scratch/<run>/, RETURN grammar, start/next/done/status/retry/abandon, hook-stop and hook-subagent-stop. Plan format parsed from the Backlog plan field (steps with Files, Criteria, Test; Retire, Change, Catalog lines). JUnit report for red gate and close evidence. AC1-7.
2. meta/core/tools/test_loop.py with fake backlog CLI on PATH, temp git repo, fake test commands writing JUnit. AC9.
3. Agents: intake, planner (Haiku), researcher (Sonnet); guides intake.md, plan.md, research.md; test.md and implement.md end with RETURN lines and read from frames. orchestrate.md becomes dispatcher procedure. AC8.
4. Hooks in .claude/settings.json (user confirmed 2026-10-10): Stop -> loop.py hook-stop; SubagentStop matcher on loop agents -> loop.py hook-subagent-stop. .gitignore .scratch/. AC6.
5. stack.md template row `test report (JUnit XML)`, init-factory stack phase item. HD-16, design.md, AGENTS.md, decisions.md, _about catalogs, check-harness (researcher model exception, guides carry RETURN grammar). AC10.
6. check-harness, commit + push per coherent step.
Note: docs (2026-10) say subagents can nest 3 deep; trampoline kept for bounded context, AskUserQuestion on main thread only, and resume after /clear.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evidence: test_loop.py 15 tests OK (happy path to Done with push, call/resume, disallowed call -> relaunch -> STOP, ask round trip, restart repeats instruction, ASSUMED stop, red gate pass/error/missing, allowlist STOP, plan parsing, return grammar, both hooks, tidy routing, unset stack). check-harness.sh ok (new check 3b: loop agents match guides with RETURN lines). HD-16 = decision-16. Hooks smoke-tested idle (exit 0).
Not yet proven: a live run with Haiku agents in a product clone (TASK-4 fixtures). Products initialized before this change need the stack row `test report (JUnit XML)`; loop.py stops with a message naming it.
Fix on the way: skeleton test name #8 -> #9 after TASK-6 renumbering.
Follow-up: TASK-8 (init-factory on the loop).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Orchestrator rebuilt as a dispatcher for a Haiku main thread (HD-16). meta/core/tools/loop.py holds the task state machine and runs all deterministic steps; intake, planner, test-writer, implementer (Haiku) and researcher (Sonnet) end with typed RETURN lines; call/ask push frames on a stack in .scratch/<run>/ and resume the caller. Stop and SubagentStop hooks keep the loop on rails. Red gate and criterion evidence come from a JUnit report named in the stack. Verified with test_loop.py (15 tests) and check-harness.sh; live Haiku run pending TASK-4.
<!-- SECTION:FINAL_SUMMARY:END -->
