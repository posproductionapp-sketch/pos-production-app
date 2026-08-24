# POS Production App — Architecture

This directory contains the production architecture baseline for POS Production Development Specification V2.

## Phase boundary

This bootstrap establishes project structure, architecture boundaries, configuration conventions, and development guardrails. Database schema, migrations, persistence implementations, and production data wiring are intentionally deferred to the Database Phase.

## Architectural boundaries

- POS/application layer owns deterministic business workflows.
- AI Orchestrator coordinates specialist agents and produces the final AI-facing result.
- Specialist agents must not access the database directly.
- Deterministic backend services own pricing, VAT, discounts, stock, payments, and refunds.
- External integrations are isolated behind explicit interfaces/adapters.
- Secrets and OpenAI configuration are supplied through environment variables; no credentials are committed.

## Initial module map

```text
src/
  app/                 application/bootstrap boundary
  domain/              domain contracts and deterministic business rules
  agents/              orchestrator and specialist-agent boundaries
  services/            application services/use cases
  integrations/        external API/tool adapters
  infrastructure/      infrastructure boundaries; DB implementation deferred
  config/               environment/configuration loading

tests/
  architecture/        architecture/contract checks
  unit/                unit tests
  integration/         integration tests (DB deferred)
```

Database Phase may implement `src/infrastructure/database/` and migrations without changing the agent-to-backend boundary.
