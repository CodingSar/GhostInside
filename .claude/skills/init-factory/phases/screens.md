# Phase: screens

Goal: the screens of the core jobs, agreed on a picture rather than in prose.
A mockup shows the user missing states, navigation, and the data each screen
needs before facets, stack, or backlog depend on them. Every screen traces to
a core job of `product-brief`.

Mockups are for eliciting answers. They are not product code: never copy or
import them into the source root. The working UI is built slice by slice
after the walking skeleton.

## Skip rule

Read the `interface` field of `product-brief`. If it names no GUI (web UI,
mobile app, desktop GUI), skip this phase and its gate. Check the criterion
with the evidence `n/a: interface is <value>` and write nothing else.

## Mockup rules

- One file per screen: `meta/product/screens/<screen id>.html`, the id in
  kebab-case.
- Static and self-contained: one HTML file, inline CSS, no JavaScript, no
  external fonts, scripts, or images. It opens from disk in any browser.
- Low fidelity: grey boxes, system font, real labels. Layout and content,
  not visual design.
- A banner at the top: `MOCKUP - not product code`.
- Data: realistic sample values from the brief's users and core jobs, never
  lorem ipsum.
- States: one section per state the screen can be in that the brief or the
  data imply: populated, empty, loading, error, and any permission
  variant. Each section is headed with the state's name.
- Actions: every button, link, and form is labelled with the action it
  starts. Links between screens point at the other screen's file, so the
  set clicks through.
- `meta/product/screens/_about.md`: one line per screen, the id in
  backticks, with its purpose.

## Steps

1. From `product-brief`, list the screens: for each core job, the screens a
   user moves through to get it done. Merge screens two jobs share. At most
   eight; more, propose which to merge or defer.
2. Write the mockups by the rules above.
3. Show them. If an Artifact tool is available, publish the set as one
   private artifact, following that tool's rules, and give the user the
   link. Otherwise give the file paths to open in a browser.
4. Interview on what the mockups expose, with `AskUserQuestion`, at most
   four questions per round, recommended option first: unclear actions,
   missing or extra states, data the brief does not mention, navigation
   between screens. Do not ask what the brief already answers.
5. Revise the mockups from the answers and show the changed ones again. A
   question the user leaves open becomes `ASSUMED: <your best value>` in the
   doc.
6. Gate: one row per screen. Proposal = the id, its states, its actions.
   Why = the core job and the answers behind it. Rejected alternatives =
   merged, deferred, or dropped screens, or `-`.

## Output

1. `meta/product/screens/`: the ratified mockups and `_about.md`.
2. Backlog doc `product-screens`:
   `backlog doc create "product-screens" -t specification --plain`, then
   `backlog doc update <doc id> --content "<markdown>"`. Shape:

```markdown
# Screens

| Screen | Core job | Role | Data shown | Actions | States | Source |
|---|---|---|---|---|---|---|
| `<id>` | ... | ... | ... | `<action>` -> `<screen id or result>`, ... | ... | user, <date> / ASSUMED |
```

Evidence for the criterion: the doc id, one mockup file per row, and no
field empty.

## Amend

Run only if the changed brief fields include `interface` or the core jobs.
Propose added, changed, and retired screens; show only their mockups. Gate:
one row per changed screen, Rejected alternatives = the old version. After
acceptance, update the files and the doc. List in the task notes the
screens changed; the seed phase uses that list.
