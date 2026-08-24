# Production Readiness Gate

## Implemented

- Repository adapters are separated from domain/application contracts.
- Unit of Work owns application transaction commit/rollback.
- Inventory balance updates use row locking and reject negative stock.
- Idempotency keys are durable and race-safe without breaking the outer transaction.
- Payments are idempotent by provider/reference and require positive amounts.
- Refunds lock the payment and enforce cumulative refund <= payment.
- Audit events are append-only records written through the persistence boundary.
- Authentication uses PBKDF2 password hashing and HMAC-signed, expiring bearer tokens.
- RBAC is enforced by explicit domain roles and protected API dependencies.
- Offline commands have a durable command ledger and deterministic replay semantics.
- API exposes health/readiness checks and baseline security headers.
- Alembic imports the approved SQLAlchemy metadata and migration `0002_auth_and_sync` adds users/sync state.
- Unit, integration, architecture, and end-to-end tests are included in CI.

## Required deployment controls

These are operational controls and must be configured by the deployment environment:

1. Set `DATABASE_URL` to managed PostgreSQL.
2. Set `AUTH_SECRET` to a randomly generated secret of at least 32 characters and rotate it through the secret manager.
3. Set `APP_ENV=production`.
4. Run `alembic upgrade head` before serving traffic.
5. Terminate TLS at the ingress/load balancer and enforce HTTPS.
6. Run multiple API workers behind a health-aware load balancer.
7. Configure PostgreSQL backups, point-in-time recovery, monitoring, and alerting.
8. Store logs centrally and retain audit logs according to business/legal policy.
9. Restrict database network access to the application workload.
10. Do not expose `/docs` or database administration endpoints publicly without an explicit security policy.

## Release gate

A release is production-ready only when CI is green, migrations succeed on a clean PostgreSQL instance, integration/E2E tests pass, secrets are supplied by the deployment platform, and the operational controls above are verified.
