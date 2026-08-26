# Production Hardening

Phase 11 hardens the HTTP and deployment boundary without weakening domain or database gates.

## Runtime controls

- Production startup fails if `DATABASE_URL`, `AUTH_SECRET`, or `ALLOWED_HOSTS` is missing/invalid.
- Production `ALLOWED_HOSTS` cannot use the wildcard `*`.
- Incoming request bodies are bounded by `MAX_REQUEST_BODY_BYTES` (2 MiB by default).
- Production API documentation is disabled.
- Security response headers include HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy`.
- All API responses are non-cacheable.
- Request IDs are generated or propagated and included in structured HTTP metrics.

## CI controls

The quality gate runs the complete Python test suite, PostgreSQL migration checks, hardware-agent tests, and a dependency vulnerability audit with `pip-audit`.

## Deployment requirements

Set `APP_ENV=production`, a PostgreSQL `DATABASE_URL`, a random `AUTH_SECRET` of at least 32 characters, and explicit comma-separated `ALLOWED_HOSTS`. Do not commit any of these values.
