# Database Phase — Specification V2

## Status

**Implementation active — Database Decision Gate approved.**

PostgreSQL + SQLAlchemy 2.x + Alembic are the approved production persistence stack.

## Rules

- Database access is owned by `src/infrastructure/database/` and repository adapters.
- Domain and application layers depend on repository contracts, not SQL/ORM details.
- Agents never access the database directly.
- Transactions are controlled by application/use-case boundaries.
- Monetary values use exact decimal semantics; floating-point arithmetic is not a persistence contract.
- Auditability, tenant/store isolation, and idempotency are mandatory.
- Secrets and connection strings are environment-provided only.
- Repository adapters do not implicitly commit transactions.

## Implemented baseline

- PostgreSQL migration `0001_initial_pos_schema.py`.
- SQLAlchemy mappings for the approved POS tables.
- Environment-driven database engine/session factory.
- Transactional `SqlAlchemyOrderRepository` with store isolation.
- Integration coverage for order persistence and store isolation.

## Next production persistence work

1. Complete repository adapters for inventory, payments, refunds, audit, and idempotency.
2. Add explicit application transaction/unit-of-work boundaries.
3. Implement concurrency-safe inventory ledger operations with row locking.
4. Implement durable idempotency check + result persistence.
5. Implement audit writes inside the same business transaction where required.
6. Add end-to-end transaction tests against PostgreSQL.
