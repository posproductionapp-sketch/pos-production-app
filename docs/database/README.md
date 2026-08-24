# Database Phase — Specification V2

## Scope

Define the persistence boundary before implementing a database engine or schema.

## Rules

- Database access is owned by `src/infrastructure/database/` and repository adapters.
- Domain and application layers depend on repository contracts, not SQL/ORM details.
- Agents never access the database directly.
- Transactions are controlled by application/use-case boundaries.
- Monetary values must use exact decimal semantics; floating-point arithmetic is not a persistence contract.
- Auditability, tenant/store isolation, and idempotency must be explicit requirements before schema implementation.
- Secrets and connection strings are environment-provided only.

## Deferred until schema design

- SQL/ORM selection and configuration
- migrations
- tables and indexes
- foreign keys and constraints
- seed data
- backup/restore configuration
- production connection wiring

## Next database deliverable

Produce the V2 logical data model and review it against sales, orders, inventory, payments, refunds, users/roles, stores, audit logs, and idempotency requirements before creating migrations.
