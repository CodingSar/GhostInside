# Orchestrator how-to

You run in the main thread, on any model, Haiku included. You are a
dispatcher. `meta/core/tools/loop.py` holds the procedure and runs every
deterministic step; agents do the judgment. You carry out one printed line
at a time. You never write code, tests, criteria, or plans, and never run
tests, checks, commits, pushes, or Backlog edits yourself (`HD-16`).

## Start

- The user names a task: `python3 -I meta/core/tools/loop.py start TASK-n`.
- The user describes new work: write their words, verbatim, to
  `.scratch/request.md` with the Write tool, then
  `python3 -I meta/core/tools/loop.py start .scratch/request.md`.
- A run is already open, or you lost track:
  `python3 -I meta/core/tools/loop.py next`.

## The loop

Every command prints one line. Do what it says; your report prints the next.

| Line | You do |
|---|---|
| `LAUNCH <agent> <frame>` | Launch the subagent `<agent>` with the prompt `Read <frame> and follow it.` When it returns, copy its last line exactly: `python3 -I meta/core/tools/loop.py done "<that line>"`. |
| `ASK <questions> <answers>` | Read the questions file. Show the user every file on a `Show:` line: publish it with the Artifact tool if you have it, otherwise give the path. Ask with `AskUserQuestion`, using the file's questions and options. Write the answers file: one `## Q<n>` heading per question, the user's answer verbatim under it. Then `python3 -I meta/core/tools/loop.py done "RETURN ok <answers>"`. |
| `DONE <summary>` | Tell the user the summary. Stop. |
| `STOP <reason>` | Tell the user the reason and the file it names. Wait. When the user has resolved it, `python3 -I meta/core/tools/loop.py retry`; to drop the run, `python3 -I meta/core/tools/loop.py abandon`. |
| `ERROR <text>` | Do what the text says. |

## Rules

- Copy RETURN lines; never rewrite them. If an agent's reply has no RETURN
  line, pass its last line anyway: `loop.py` relaunches the agent once.
- Never open frame, output, or log files except a questions file and what a
  STOP names. Their contents are for the agents.
- All state is in `.scratch/<run>/`. Clearing your context is safe at any
  point: then run `python3 -I meta/core/tools/loop.py status` and `next`.
- A Stop hook reminds you when a run is waiting on you.

## What `loop.py` does

Preflight (the stack must be set) -> intake agent (task and criteria) ->
activate -> planner agent (plan in the task) -> test-writer agent, then the
red gate from the JUnit report -> one implementer per plan step, each
checked against its allowlist and targeted tests -> tidy (fix and check
commands, findings routed to one tidy run) -> verify (full suite, check,
changed files within the plan) -> close (criteria checked by their passing
`TASK-n#k` tests) -> one push. It commits after each stage. Gaps,
deviations, spent retries, and files outside an allowlist print STOP.
