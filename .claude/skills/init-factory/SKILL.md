---
name: init-factory
description: Configure a cloned GhostInside harness for one product. Turns CONCEPT.md into a ratified brief, facets, stack, vendored practice packs, a provisioned environment, a seeded backlog, and a green walking skeleton. Re-run on an initialized clone to amend after the concept changes. Use when the user runs /init-factory or asks to initialize, set up, or amend the factory for a product.
---

# init-factory

You run in the main thread. Do every phase yourself. Do not hand phases to
the Haiku workers in `.claude/agents/`; they need a configured harness, which
is what this skill builds. Research subagents and the deep-research skill are
allowed where a phase file says so.

Design: `HD-4` to `HD-13` in `meta/core/decisions.md`. Your task is the init
task from step 1, in the root `backlog/` (the product backlog). The harness
backlog in `meta/core/backlog/` is template history; never change it.

## Ground rules

- Propose, the user ratifies (`HD-5`). Nothing a gate covers is written
  before the gate passes.
- Backlog CLI for every Backlog change. Read `backlog instructions
  task-creation` before creating the init task and before the seed phase,
  `task-execution` before step 1, `task-finalization` before closing.
- Commit and push after each phase, preflight included. Message:
  `init-factory: <phase> (<init task id>)`. If the commit touches `meta/` or
  `.claude/`, run `meta/core/tools/check-harness.sh` first; a failure holds
  the commit until fixed. Never force-push.
- Never create repositories: no `gh repo create`, no `git init`. The user
  makes the clone and the product remote.
- Allowed to change: `meta/product/` (practices through
  `meta/core/tools/practices.py` only; an architecture or persistence
  override only by a superseding decision), `.claude/settings.json` (allow
  entries only), `.claude/agents/` (new workers only, Haiku), `CONCEPT.md`,
  `README.md`, product files at the repo root, `src/`, `scripts/`, CI and
  container files, the root `backlog/` through the CLI.
- Never change: anything under `meta/core/`, `meta/_about.md`, `AGENTS.md`,
  `CLAUDE.md`, this skill, the core agents, deny entries and hooks in
  `.claude/settings.json`. They belong to the template (`HD-9`);
  `check-harness.sh` fails when they differ from the harness version.
- Scratch work that must survive a restart goes in `.cache/init/`
  (gitignored).
- Multi-line text for `backlog doc update --content` or `--append-notes` must
  contain real newlines (for example a `$'...'` string), not `\n`. Check docs
  with `backlog doc view <id>` after writing.

## 0. Preflight (every invocation)

1. Run `backlog instructions overview` once per conversation.
2. Template guard. Normalize a remote URL by dropping the scheme
   (`ssh://`, `https://`, `git@`), turning the `:` after the host into `/`,
   dropping a trailing `/` and `.git`, and lowercasing. The template
   normalizes to `github.com/codingsar/ghostinside`.
   - If `origin` is the template: ask the user whether this is a product
     clone. If yes, ask for the product remote URL (the user creates that
     repo), then run `git remote rename origin harness` and
     `git remote add origin <url>`. If no, stop: init never runs on the
     template.
   - If there is no `harness` remote, add it:
     `git remote add harness git@github.com:CodingSar/GhostInside.git`.
3. Shared history: `git fetch -q harness`, then `git merge-base HEAD
   harness/main`. If it fails, stop and explain: the clone must come from
   `git clone` of the template, not the GitHub template button, so harness
   upgrades can merge later.
4. On `main`. Working tree: on a first run it must be clean; on resume,
   uncommitted changes are left from an interrupted phase. Show
   `git status --short` and ask the user to keep (commit them under the
   current phase) or discard them. Never discard on your own.
5. `CONCEPT.md` at the repo root. If missing on a first run, ask the user to
   paste the concept and write it verbatim to `CONCEPT.md`.
6. `gh auth status`. If not logged in, say that pack PRs and the CI check
   will be skipped and reported, and that criterion 8 then stays unchecked.

## 1. Find or create the init task

`backlog task list --labels init-factory --json`, then sort `tasks` by status.

| Found | Mode | Action |
|---|---|---|
| none | init | Create the task below. |
| exactly one not Done | resume | Read it with `backlog task view <id> --plain`. Continue at the first unchecked criterion. Its notes hold the state of earlier phases. |
| more than one not Done | stop | Show them. Ask the user which one to continue and whether to archive the others. |
| all Done, `product-brief` doc exists | amend | Ask the user what changed (or read the new `CONCEPT.md`). Create the task below titled `Amend factory: <one-line delta>`, labels `init-factory,amend`. Every phase runs its Amend section. |
| all Done, no `product-brief` doc | stop | The earlier run is inconsistent. Report it and ask the user how to proceed. |

Create: title `Initialize factory for <product name or repo name>`, label
`init-factory`, description `Run of the init-factory skill.`, and exactly
these criteria, in order:

1. `Preflight passed: harness remote with shared history`
2. `Brief ratified and stored as Backlog doc product-brief`
3. `Domain and concern facets ratified`
4. `Stack and architecture ratified: stack.md has no TBD, decisions recorded in init-decisions`
5. `Practice packs ratified, vendored, locked and compiled; new packs proposed upstream`
6. `Environment provisioned and stack overlays written`
7. `Backlog seeded with milestones and draft slices`
8. `Walking skeleton green: install, migrations, check command, full tests, check-harness, CI`

Then `backlog task edit <id> -s "In Progress" -a @claude`, and
`backlog config set projectName "<product name>"`. Check criterion 1 with
the preflight output as evidence. Commit `CONCEPT.md`, the remote change,
and the task as `init-factory: preflight (<id>)`, and push.

## 2. Run the phases

For each unchecked criterion, in order:

| Criterion | Phase file | Gate |
|---|---|---|
| 2 | `.claude/skills/init-factory/phases/brief.md` | brief |
| 3 | `.claude/skills/init-factory/phases/facets.md` | facets |
| 4 | `.claude/skills/init-factory/phases/stack.md` | stack and architecture |
| 5 | `.claude/skills/init-factory/phases/practices.md` | packs |
| 6 | `.claude/skills/init-factory/phases/provision.md` | provision and seed (shared) |
| 7 | `.claude/skills/init-factory/phases/seed.md` | provision and seed (shared) |
| 8 | `.claude/skills/init-factory/phases/skeleton.md` | none: the evidence is deterministic |

Read the phase file. Do its steps. Hold its gate. Write its outputs. Then:

1. `backlog task edit <id> --check-ac <criterion number>`, only with the
   evidence the phase file names.
2. `backlog task edit <id> --append-notes "criterion <n>: <outputs>; evidence: <evidence>"`.
3. Commit and push.

Provision and seed share one gate: before writing anything for criterion 6,
draft the provision files and the seed drafts, show both in one table, and
after acceptance run both phases without another gate.

## Gate

Five gates in all (`HD-5`). Show one table:

| # | Item | Proposal | Why | Rejected alternatives |
|---|---|---|---|---|

Phase files say what goes in each column. Where a row had no alternative,
write `-`. The user accepts all, or edits rows by number. Show only the
changed rows again. The gate passes on explicit acceptance. Record the
ratified table, compressed, in the task notes.

## Decisions

Product decisions live in the root backlog as `decision-n`. Harness
decisions are `HD-n`; never create those here.

| Gate row | Record |
|---|---|
| The stack rows together | One decision: `Stack: <language version>, <framework>, <datastore>, <test runner>`. |
| A row that supersedes a default (architecture, datastore) | Its own decision, title starting `Supersedes HD-<n>:`. |
| Any other row that chose between real alternatives | Its own decision. |
| A row that keeps a default | No decision; its `init-decisions` row cites the `HD-n`. |

The decision CLI stores only a title and a status, and has no edit command.

1. `backlog decision create "<choice, one line>" -s accepted --plain`.
2. Rationale and rejected alternatives live in the Backlog doc
   `init-decisions` (create it on first use with
   `backlog doc create "init-decisions" -t specification --plain`). Read the
   doc, append one row per gate item, write the whole content back with
   `backlog doc update <doc id> --content`. Row:
   `| decision-<n> or HD-<n> | <item> | <choice> | <rationale> | <rejected alternatives> | criterion <n> |`
3. A later change is a new decision whose title starts `Supersedes
   decision-<n>:`. Never edit an old one.

## Stop rules

Stop and report instead of looping when:

- the template guard or shared-history check fails;
- the user says stop at a gate;
- a researched pack still fails `practices.py check` after one repair;
- the skeleton is still red after three fix rounds;
- a tool the phase needs is missing (for example Docker for a server
  datastore) and the user does not install it;
- a change would touch something under "Never change";
- a deny entry or the guard hook would need to change (needs the user's
  explicit confirmation, `AGENTS.md`, Governance).

Not a stop: the central practices repo is unreachable, or `gh` is missing.
Record it in the notes, continue as the practices and skeleton phases say,
and report it at the end.

## Finish

After criterion 8: follow `backlog instructions task-finalization`. Final
summary: the product brief doc id, decisions created, packs vendored and PRs
opened (or not opened), files provisioned, drafts seeded, skeleton evidence.
Set Done. Tell the user the next step: promote a draft
(`backlog draft promote <id>`) and run the orchestrator
(`meta/core/guides/orchestrate.md`).
