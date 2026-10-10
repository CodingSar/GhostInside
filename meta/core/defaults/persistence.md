# Persistence: PostgreSQL only (default)

Decision: `HD-2`. A product overrides it only with
`meta/product/persistence.md`, written for a ratified superseding decision
(`HD-6`, `HD-9`).

- PostgreSQL is the only datastore. No SQLite, no document store, no
  key-value store as primary storage. A cache or queue needs a product
  decision first.
- The connection string comes from the connection variable in
  `meta/product/stack.md` (default `DATABASE_URL`).
- A module owns its tables. Table names start with `<module>_`. Migrations
  live in the module's `migrations/` folder and run in order.
- Only the module's `store` runs queries against its tables.
- Tests run against a real PostgreSQL, as the test guide says.
