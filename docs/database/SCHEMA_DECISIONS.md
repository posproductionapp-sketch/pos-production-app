# Database Decision Gate

## Decision status

**APPROVED FOR MIGRATIONS**

Approved by project owner on 2026-08-24. Physical database implementation may proceed using the decisions below.

## Approved decisions

- Database engine: PostgreSQL
- ORM/query layer: SQLAlchemy 2.x
- Migration tooling: Alembic
- Isolation/concurrency: PostgreSQL READ COMMITTED by default; explicit row locking (`SELECT ... FOR UPDATE`) for stock/order critical sections; transactions owned by application services
- Money representation: PostgreSQL NUMERIC with explicit ISO currency code; application uses Decimal
- Timestamp standard: timezone-aware timestamps normalized to UTC
- Tenant/store isolation: explicit `tenant_id` / `store_id` ownership columns with application checks and database constraints where applicable
- Audit retention: immutable audit records retained according to production compliance policy; no destructive update of audit history
- Reference/seed data: versioned deterministic seed set; migrations must be safe to re-run

## Gate rule

Codex may implement migrations and persistence adapters using these approved decisions. Any change to these decisions requires updating this document and passing the architecture review gate again.
