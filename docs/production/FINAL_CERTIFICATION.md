# Production Certification

This document records the production-readiness gate for the POS service.

## Certified baseline

- Repository mainline includes the business-core and production-runtime hardening changes.
- CI requires architecture contracts, compilation, tests, PostgreSQL migration, connectivity, downgrade/upgrade, and migration idempotency.
- Production runtime requires PostgreSQL and an AUTH_SECRET of at least 32 characters.
- Production API documentation endpoints are disabled.
- Security response headers and request correlation IDs are emitted by the HTTP boundary.

## Remaining release gates

1. Observability: structured logs, metrics, traces, alert rules, and operational dashboards.
2. Offline/sync: durable command ledger, retries, conflict handling, replay safety, and recovery tests.
3. E2E: critical checkout, refund, shift, inventory, authentication, and offline-reconnect journeys.
4. Security: tenant/store isolation, RBAC coverage, rate limiting, secret rotation, and dependency/security scans.
5. Deployment: container hardening, migration strategy, backup/restore verification, smoke tests, and rollback procedure.
6. Final certification: all release gates green on the exact release commit.
