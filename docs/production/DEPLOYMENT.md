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

The Compose app performs `alembic upgrade head` before starting the API and waits for PostgreSQL health before startup.

## Production prerequisites

- PostgreSQL storage must use durable backups and tested restore procedures.
- `AUTH_SECRET` and `POSTGRES_PASSWORD` must come from deployment secret storage, never Git.
- `ALLOWED_HOSTS` must contain only the actual public hostnames.
- TLS termination must be provided by the production ingress/load balancer.
- Database migration execution should be moved to a dedicated one-shot deployment job before enabling multiple application replicas.

## Current architecture boundary

The repository currently has no runtime Redis client or queue consumer. Redis is therefore **not** declared as an active production dependency in this deployment manifest; adding an unused service would create a false production guarantee. The Redis queue/cache requirement from the master specification remains an explicit infrastructure/application integration gate before a final production-readiness declaration.
