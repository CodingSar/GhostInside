# AGENTS.md

## Git

- Default branch `main`, remote `origin`.
- Harness changes commit directly to `main`, in small commits, one per coherent change. Commits are the rollback path to earlier, better harness versions.
- Push after each commit. The orchestrator (main thread) may push. Subagents never commit or push.
- Never force-push. Never rewrite published history.

## Harness

- Read `PLAN.md` for the design and `meta/_about.md` for the catalog.
- The main thread runs the orchestrator procedure in `meta/guides/orchestrate.md`. Workers are Haiku subagents in `.claude/agents/`, launched from the main thread. No headless launch.
- Backlog tasks are the plan of record. Acceptance criteria are the cases. Plans live in the task `plan` field, not in files.
- Run `meta/tools/check-harness.sh` before committing harness changes.

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
