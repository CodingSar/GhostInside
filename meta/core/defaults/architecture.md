# Architecture: modules of slices (default)

Decision: `HD-1`, amended by `HD-11`. Default for every product. A product
overrides it only with `meta/product/architecture.md`, written for a ratified
superseding decision (`HD-6`, `HD-9`). An override keeps the skeleton the
tools rely on: `modules/<module>/slices/<slice>/`, the entry file stems, and
the catalogs.

## Units

| Unit | Is | Owns |
|---|---|---|
| module | One area of the domain, such as `billing` or `accounts`. | Its tables, migrations, and public API. |
| slice | One use case of a module: one command or one query, such as `create-invoice`. | Its handler, its pure rules, its test. |
| `app/` | The composition root. | Startup, config loading, wiring of routes, CLI commands, and jobs to module `index` functions. |
| `shared/` | The kernel. | Datastore connection, base error types, config reader, clock. |

## Layout

Source root and extensions come from `meta/product/stack.md`. Names below are
file stems; the stack's extension and the test file idiom of the `test.md`
overlay apply.

```
src/
  _about.md              catalog: one row per module, its purpose
  app/                   composition root, no business rules
  shared/                kernel, no business rules
  modules/
    <module>/
      _about.md          purpose, public API, tables owned, one line per slice
      index              public API; the only file app/ and other modules import
      store              queries for this module's tables
      model              types and rules shared by two or more slices (optional)
      migrations/        this module's migrations; tables prefixed <module>_
      slices/
        <slice>/
          handler        entry point of the use case
          rules          pure rules of this use case only (optional)
          test           the slice's tests, named per the test.md overlay
```

Module and slice names use the name case in `meta/product/stack.md`
(kebab by default, snake where the language imports folders by name). Entry
file stems (`index`, `handler`) follow the stack's entry file stems row.

## Import rules

1. A slice imports its own files, its module's `store` and `model`, and
   `shared/`. Never a sibling slice.
2. A module reaches another module only through that module's `index`.
3. `app/` imports module `index` files and `shared/` only.
4. `shared/` imports nothing from `modules/` or `app/`.
5. `index` re-exports handlers and types. It holds no logic.

The stack's boundary checker enforces rules 1 to 4, through the check command
in `meta/product/stack.md`.

## Ownership

- A module owns its tables. Only its `store` queries them. Other modules get
  that data through `index`.
- Code a second slice of the same module needs moves to the module's `model`.
  Code another module needs is exposed through `index`. Code with no business
  rule that every module needs goes to `shared/`; adding to `shared/` needs a
  product decision.
- No file or folder named `utils`, `util`, `helpers`, `helper`, `services`,
  `service`, `common`, `lib`, `misc`, `manager`, or `managers` under the
  source root.
- Request parsing for one use case stays in its handler. `app/` only maps a
  route or command to an `index` function.

## Size

| Limit | Cap | On breach |
|---|---|---|
| Lines per source file | 200 | Split by responsibility inside the slice or module. |
| Lines per test file | 300 | Split the slice; it holds more than one use case. |
| Slices per module | 12 | Propose a module split; it needs a product decision. |
| Folders inside a slice | 0 | Slices are flat. |

`meta/core/tools/structure.py` enforces the layout, the catalogs, the
forbidden names, and these caps.

## Growth

- A new use case of an existing module is a new slice folder.
- A new area of the domain is a new module, named in the task plan.
- Splitting or merging modules needs a product decision.
- Signatures come first: the handler signature exists, as a stub, before any
  logic.

## Catalogs

`src/_about.md` names every module, in backticks. Each module's `_about.md`
names every slice, in backticks. `structure.py` fails when a name is missing.
The orchestrator adds the lines when a task creates a module or slice, right
after the test-first step.

## Why

A small model holds one slice folder in context. A step's allowlist is one
slice folder, plus the module's `store`, `model`, `index`, `migrations/`, or
`_about.md` when the plan names them, so a wrong-file edit is easy to detect.
Modules keep table ownership in one place while use cases stay small and
separate.
