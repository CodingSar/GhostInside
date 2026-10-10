---
name: init-factory
description: Configure a cloned GhostInside harness for one product. Turns CONCEPT.md into a ratified brief, facets, stack, vendored practice packs, a provisioned environment, a seeded backlog, and a green walking skeleton. Re-run on an initialized clone to amend after the concept changes. Use when the user runs /init-factory or asks to initialize, set up, or amend the factory for a product.
---

# init-factory

You run in the main thread. Do every phase yourself. Do not hand phases to
the Haiku workers in `.claude/agents/`; they need a configured harness, which
is what this skill builds. Research subagents and the deep-research skill are
allowed where a phase file says so.

Design: Backlog `decision-4` to `decision-8`. Plan of record for this skill:
`TASK-2` in the template.

## Ground rules

- Propose, the user ratifies (`decision-5`). Nothing a gate covers is written
  before the gate passes.
- Use the Backlog CLI for every Backlog change. Read `backlog instructions
  task-execution` before step 1 and `task-finalization` before closing.
- Commit and push after each phase. Message: `init-factory: <phase>`, with
  the init task id. Never force-push.
- Allowed to change: `meta/registry/`, `meta/practices/` (through
  `meta/tools/practices.py` only), `meta/architecture/` (only by a superseding
  decision), `meta/guides/stack/`, `.claude/settings.json` (allow entries
  only), `.claude/agents/` (new workers only, Haiku), product files at the
  repo root, `src/`, CI and container files.
- Never change: core guides in `meta/guides/` (outside `stack/`),
  `meta/tools/`, `meta/docs/`, `AGENTS.md`, deny entries in
  `.claude/settings.json`. These belong to the template (`decision-7`).
- Scratch work that must survive a restart goes in `.cache/init/`
  (gitignored).

## 0. Preflight (every invocation)

1. Run `backlog instructions overview` once per conversation.
2. Template guard. Template remote: `git@github.com:CodingSar/GhostInside.git`
   (also `https://github.com/CodingSar/GhostInside` with or without `.git`).
   - If `origin` is the template: ask the user whether this is a product
     clone. If yes, ask for the product remote URL, then run
     `git remote rename origin harness` and `git remote add origin <url>`.
     If no, stop: init never runs on the template.
   - If there is no `harness` remote, add it with the template URL.
3. Shared history: `git fetch -q harness`, then `git merge-base HEAD
   harness/main`. If it fails, stop and explain: the clone must come from
   `git clone` of the template, not the GitHub template button, so harness
   upgrades can merge later.
4. Working tree clean and on `main`. Otherwise stop and report.
5. `CONCEPT.md` at the repo root. If missing on a first run, ask the user to
   paste the concept and write it verbatim to `CONCEPT.md`.
6. `gh auth status`. If not logged in, say that pack PRs will be skipped and
   reported; continue.

## 1. Find or create the init task

`backlog task list --labels init-factory --plain`

| Found | Mode | Action |
|---|---|---|
| none | init | Create the task below. |
| one not Done | resume | Read it with `--plain`. Continue at the first unchecked criterion. Its notes hold the state of earlier phases. |
| all Done, `product-brief` doc exists | amend | Ask the user what changed (or read the new `CONCEPT.md`). Create the task below titled `Amend factory: <one-line delta>`, labels `init-factory,amend`. Every phase runs its Amend section. |

Create: title `Initialize factory for <product name or repo name>`, label
`init-factory`, description `Run of the init-factory skill.`, and exactly
these criteria, in order:

1. `Preflight passed: harness remote with shared history`
2. `Brief ratified and stored as Backlog doc product-brief`
3. `Domain and concern facets ratified`
4. `Stack and architecture ratified: registry has no TBD, decisions recorded in init-decisions`
5. `Practice packs ratified, vendored, locked and compiled; new packs proposed upstream`
6. `Environment provisioned and stack overlays written`
7. `Backlog seeded with milestones and draft slices`
8. `Walking skeleton green: lint, full tests, check-harness, CI`

Then `backlog task edit <id> -s "In Progress" -a @claude`. Check criterion 1
with the preflight output as evidence.

## 2. Run the phases

For each unchecked criterion, in order:

| Criterion | Phase file |
|---|---|
| 2 | `.claude/skills/init-factory/phases/brief.md` |
| 3 | `.claude/skills/init-factory/phases/facets.md` |
| 4 | `.claude/skills/init-factory/phases/stack.md` |
| 5 | `.claude/skills/init-factory/phases/practices.md` |
| 6 | `.claude/skills/init-factory/phases/provision.md` |
| 7 | `.claude/skills/init-factory/phases/seed.md` |
| 8 | `.claude/skills/init-factory/phases/skeleton.md` |

Read the phase file. Do its steps. Hold its gate. Write its outputs. Check
the criterion with the evidence the phase file names. Append a note:
`phase <n>: <outputs>; evidence: <evidence>`. Commit and push.

## Gate

One gate per phase. Show one table:

| # | Item | Proposal | Why | Rejected alternatives |
|---|---|---|---|---|

The user accepts all, or edits rows by number. Show only the changed rows
again. The gate passes on explicit acceptance. Record the ratified table,
compressed, in the task notes.

## Decisions

Every ratified choice that is more than a plain registry value becomes a
Backlog decision. The decision CLI stores only a title, so:

1. `backlog decision create "<choice, one line>" -s accepted --plain`.
   A choice that replaces an earlier decision starts its title with
   `Supersedes decision-<n>:`.
2. Add a row to the Backlog doc `init-decisions` (create it on first use
   with `backlog doc create "init-decisions" -t specification`). Read the
   doc, append the row, write the whole content back with
   `backlog doc update <doc id> --content`. Row:
   `| decision-<n> | <choice> | <rationale> | <rejected alternatives> | phase <n> |`
3. Every harness file that cites a superseded decision now cites the new one.

## Stop rules

Stop and report instead of looping when:

- the template guard or shared-history check fails;
- the user says stop at a gate;
- a researched pack still fails `practices.py check` after one repair;
- the skeleton is still red after three fix rounds;
- a change would touch something under "Never change";
- a deny entry would need to change (needs the user's explicit confirmation,
  `meta/docs/harness-review.md` rule 5).

## Finish

After criterion 8: follow `backlog instructions task-finalization`. Final
summary: the product brief doc id, decisions created, packs vendored and PRs
opened, files provisioned, drafts seeded, skeleton evidence. Set Done. Tell
the user the next step: promote a draft and run the orchestrator
(`meta/guides/orchestrate.md`).
