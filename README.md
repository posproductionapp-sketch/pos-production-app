# pos-production-app

Production POS system for sales, inventory, orders, payments, refunds, shifts, and store operations.

## Architecture

- Domain: deterministic business rules, money invariants, shift lifecycle, and authorization primitives.
- Application: use cases and Unit of Work transaction boundaries.
- Infrastructure: PostgreSQL/SQLAlchemy repositories, catalog, inventory locking, audit, idempotency, payments/refunds, authentication, shifts/cash, and sync ledger.
- API: FastAPI HTTP boundary with bearer authentication, RBAC, health/readiness, request correlation, security headers, catalog, sales, inventory, payments/refunds, and shift/cash endpoints.
- Database: Alembic migrations; current head is `0003_shifts_and_cash`.

## Production business flow

`catalog -> stock receipt -> sale/checkout -> payment -> refund/restock -> shift/cash control`

Sales and refunds require idempotency keys. Inventory changes are transaction-scoped and row-locked. Payment/refund amounts use exact decimals and cumulative refunds cannot exceed the captured payment. Store and tenant context is enforced at the application boundary.

## Development

```bash
export DATABASE_URL='postgresql+psycopg://pos:pos@localhost:5432/pos_test'
export AUTH_SECRET='replace-with-a-random-secret-of-at-least-32-characters'
alembic upgrade head
pytest
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Production deployment requirements are documented in `docs/production/READINESS.md`.
