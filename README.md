# pos-production-app

Production POS system for sales, inventory, orders, and store operations.

## Architecture

- Domain: deterministic business rules and authorization primitives.
- Application: use cases and Unit of Work transaction boundaries.
- Infrastructure: PostgreSQL/SQLAlchemy repositories, audit, idempotency, payments/refunds, authentication, and sync ledger.
- API: FastAPI HTTP boundary with bearer authentication, RBAC, health/readiness, request correlation, and security headers.
- Database: Alembic migrations; current head is `0002_auth_and_sync`.

## Development

```bash
export DATABASE_URL='postgresql+psycopg://pos:pos@localhost:5432/pos_test'
export AUTH_SECRET='replace-with-a-random-secret-of-at-least-32-characters'
alembic upgrade head
pytest
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Production deployment requirements are documented in `docs/production/READINESS.md`.
