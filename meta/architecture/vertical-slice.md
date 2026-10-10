# Architecture: vertical slices (default)

Decision: Backlog `decision-1`. Default style for every project the factory
builds. A project may override it only by a new accepted decision, which
`init-factory` proposes and the user ratifies (`decision-6`).

## Unit

A slice is one feature, end to end: its entry point, its rules, its storage,
its tests. A slice is one folder. Everything a worker needs for a slice is in
that folder.

## Layout

Root `src/` is the default. `init-factory` may change the root and file
extensions; the shape stays.

```
src/
  slices/
    <slice>/
      index    public entry; the only file other slices may import
      logic    business rules
      store    persistence for tables this slice owns
      migrations/   this slice's migrations, prefixed <slice>_
      tests/   one file per entry point, test names carry AC<n>
  shared/      kernel: database connection, base error types, config
```

## Rules

- A slice reaches another slice only through that slice's `index`.
- A slice owns its tables. No other slice queries them. Cross-slice data comes
  through `index` calls.
- `shared/` holds no business rules. Adding to it needs a Backlog decision.
- A new feature is a new slice folder. No `services/`, `utils/`, or
  `helpers/` folders.
- Signatures come first: the entry signature exists, as a stub, before any
  logic.

## Why

A small model holds one folder in context. The allowlist for a step is one
slice folder plus `shared/` if needed, so a wrong-file edit is easy to
detect.
