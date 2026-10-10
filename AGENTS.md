# AGENTS.md

## Git

- Default branch `main`, remote `origin`.
- Harness changes commit directly to `main`, in small commits, one per coherent change. Commits are the rollback path to earlier, better harness versions.
- Harness changes: push after each commit. Product tasks: commit per step, push once the task's full suite and check pass (`meta/core/guides/orchestrate.md`). `loop.py`, run by the main thread, commits and pushes product tasks; the main thread pushes harness changes. Subagents never commit or push.
- Never force-push. Never rewrite published history.

## Harness

- Read `meta/core/design.md` for the design and `meta/_about.md` for the catalog.
- The main thread runs the orchestrator procedure in `meta/core/guides/orchestrate.md`: it dispatches what `meta/core/tools/loop.py` prints. The main thread runs on Sonnet (`model` in `.claude/settings.json`, `HD-17`); every agent runs on Haiku except the `researcher`. Workers are subagents in `.claude/agents/`, launched from the main thread. No headless launch.
- Backlog tasks are the plan of record. Acceptance criteria are the cases. Plans live in the task `plan` field, not in files.
- Two Backlog projects. Root `backlog/` is the product backlog; the template ships it empty. `meta/core/backlog/` is the harness backlog: prefix every `backlog` command for harness work with `BACKLOG_CWD=meta/core`. In a product clone the harness backlog is read-only history.
- Run `meta/core/tools/check-harness.sh` before committing harness changes. A failing check holds the commit.

## Governance

- Harness files (`.claude/`, `meta/`, `AGENTS.md`, `CLAUDE.md`) change live on `main`, without a review gate. Restore an earlier version of a file from its commit to roll back.
- `meta/core/` belongs to the template. In a product clone it is never edited; harness changes are made in the template and merged from the `harness` remote.
- A change to a worker's limits (its tools, model, or allowlist rules) states why in the commit message: the Backlog task that motivated it, or the user request when there is none.
- Hard denies in `.claude/settings.json` and the guard hook stay in place whatever the allowlists say. Changing either needs the user's explicit confirmation.

<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.53.0 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**At the beginning of each conversation in this project, run `backlog instructions overview` before answering or taking action. Re-read it only if you have not read it yet in the current conversation.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->

<!-- groma:start -->
## Groma

This project uses Groma. Before you scan, inspect, or curate architecture, or change files for a Backlog task, run `groma agent-instructions` and read the guide it names for that job. When it reports a first scan, ask the user whether they want you to curate the architecture. Do not edit Groma-owned architecture files directly.
<!-- groma:end -->
