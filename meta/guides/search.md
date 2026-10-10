# Searcher how-to

Goal: find what the harness says about the topics you were given, and return
it as a packet. You do not judge relevance beyond the topic names, and you do
not design.

## 1. Topics

The prompt gives topics from a closed menu:

| Topic | Look in |
|---|---|
| `architecture` | `meta/architecture/` |
| `registry` | `meta/registry/` |
| `practices:testing` | `meta/practices/` (domain row first, then `generic`) |
| `slice:<name>` | `src/slices/<name>/` (the folder named in the prompt) |

Any topic outside this table is a gap with `reason: unknown topic`.

## 2. Procedure

1. Read `meta/_about.md`. Read only the `_about.md` of each directory your
   topics name.
2. Read the files those catalogs name for your topics. Stop there.
3. For `slice:<name>`: if the folder exists, read its `index` entry file only.
   If the folder does not exist, record a gap with `reason: no slice folder`.
   That is expected for new slices, so it is not a stop by itself.
4. Practices: for `practices:testing`, use the row whose domain matches the
   domain in `meta/registry/`, if any; otherwise the `generic` row.

Matching is exact. No synonyms, no guessing a closest file.

## 3. Packet format

Your final reply is the packet. Use this shape, and keep empty sections as
`none`:

```
topic: <topic>
rules:
  - source: <file>:<line>
    text: "<verbatim rule>"
decisions:
  - id: <backlog decision id>
    title: <title>
facts:
  - source: <file>:<line>
    text: "<verbatim value, such as a command or name>"
gaps:
  - topic: <topic>
    reason: <unknown topic | no file | no slice folder | file missing>
```

Copy rules and facts verbatim with their source location. Do not summarise.
Do not add advice, recommendations, or code.

Decision ids come from `backlog decision list --plain`. Run it once if a
catalog names a decision.

## 4. Final line

`RESULT: ok gaps=<count>` when there are no gaps, else `RESULT: gaps gaps=<count>`.
