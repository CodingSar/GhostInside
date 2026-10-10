# Registry: persistence (default)

Decision: Backlog `HD-2`. PostgreSQL is the only datastore. This is a
default: `init-factory` may supersede it by a ratified decision (`HD-6`).

- No other database: no SQLite, no document store, no key-value store as
  primary storage. A cache or queue needs a Backlog decision first.
- Tests run against a real PostgreSQL. No in-memory fake of PostgreSQL. No
  mocked database.
- Connection string comes from the environment variable `DATABASE_URL`. This
  is the default name; `init-factory` confirms or changes it.
- Each slice owns its tables. Table names are prefixed with the slice name.
  Migrations live in the slice's `migrations/` folder and run in order.
- Only a slice's `store` file runs queries against its own tables.
- Mocks: the database is never mocked. Mock only clock, randomness, and
  network.
