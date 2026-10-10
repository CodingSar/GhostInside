# Phase: brief

Goal: a product brief the rest of init can trust. Every field traces to the
concept, to a user answer, or is marked `ASSUMED:`.

## Checklist

| Field | Question it answers |
|---|---|
| name | What is the product called? |
| one-liner | What is it, in one sentence? |
| users | Who uses it, in which roles? |
| core jobs | What must those users get done? 3 to 7 items. |
| scale | How many users, how much data, what load, at launch and in a year? |
| data sensitivity and compliance | Personal, financial, health, or regulated data? Which regimes apply? |
| deploy target | Where does it run: cloud, on-prem, device, desktop, CLI on user machines? |
| integrations | Which external systems does it talk to, and how? |
| non-goals | What is explicitly out of scope? |
| language preference | Any language, framework, or hosting the team requires or refuses? |

## Steps

1. Read `CONCEPT.md` in full.
2. For each field, fill it from the concept and keep the quote it came from.
   A field the concept does not answer is a gap. Two passages that disagree
   are a gap.
3. Interview: ask about gaps only, at most four questions per round, with
   `AskUserQuestion`. Put your recommended option first. Do not ask what the
   concept already answers.
4. A gap the user leaves open becomes `ASSUMED: <your best value>`.
5. Gate: one row per field, Proposal = the value, Why = the source.

## Output

Backlog doc `product-brief`:
`backlog doc create "product-brief" -t specification --plain`, then
`backlog doc update <doc id> --content "<markdown>"`. Shape:

```markdown
# <name>

<one-liner>

| Field | Value | Source |
|---|---|---|
| users | ... | CONCEPT.md: "<quote>" / user, <date> / ASSUMED |
```

Evidence for the criterion: the doc id, and no field empty.

## Amend

Read the new `CONCEPT.md` or the user's description of the change. Compare
field by field with `product-brief`. Ask only about fields that changed or
are new. Update the doc. In the task notes, list the changed fields; later
phases use that list to decide what to revisit.
