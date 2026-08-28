# Production Deployment

Phase 12 provides a deployable backend container, production Compose definition, and GitHub Actions container build/publish workflow.

## Container

The runtime image uses a versioned Python 3.12 slim base, installs only runtime dependencies, runs as UID/GID `10001`, exposes port 8000, and includes a `/health` container health check.

The container workflow builds on pull requests and publishes to GitHub Container Registry on `main`/version tags. Published images include provenance and SBOM attestations.

## Compose

Copy `.env.production.example` to the deployment environment, replace every placeholder, then run:

```bash
docker compose --env-file .env.production -f compose.production.yml up -d --build
```

The Compose app waits for healthy PostgreSQL and Redis services, applies `alembic upgrade head` before starting the API, and exposes health checks for the application and dependencies. Redis is an active production dependency and is configured with append-only persistence.

## Production prerequisites

- PostgreSQL storage must use durable backups and tested restore procedures.
- `AUTH_SECRET` and `POSTGRES_PASSWORD` must come from deployment secret storage, never Git.
- `ALLOWED_HOSTS` must contain only the actual public hostnames.
- TLS termination must be provided by the production ingress/load balancer.
- Database migration execution should be moved to a dedicated one-shot deployment job before enabling multiple application replicas.
- Redis persistence, capacity, monitoring, and recovery procedures must be validated for the selected production topology.

## Release gate

A release is production-ready only when the Production Certification workflow is green on the exact release commit, migrations succeed on a clean PostgreSQL instance, downgrade/upgrade idempotency passes, backup/restore certification passes, the disposable production stack starts and passes `/health` and `/ready`, the production migration rollback safety check passes, hardware-agent certification passes, and all required deployment controls above are verified in the target environment.
