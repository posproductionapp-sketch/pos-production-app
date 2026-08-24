# Database Decision Gate Review

Status: APPROVED

Database implementation is authorized.

Decision basis:
- `docs/database/SCHEMA_REVIEW.md` is approved for migration implementation.
- `docs/database/SCHEMA_DECISIONS.md` authorizes PostgreSQL + SQLAlchemy 2.x + Alembic.
- The initial POS schema migration and SQLAlchemy persistence mappings are already present on `main`.

Operational rule:
- Database implementation must remain behind `src/infrastructure/database/` and repository adapters.
- Domain code remains infrastructure-agnostic.
- Application use cases own transaction boundaries.
- Tenant/store isolation, idempotency, auditability, and exact decimal money semantics remain mandatory.
