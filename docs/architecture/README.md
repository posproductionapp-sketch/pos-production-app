# POS Production App — Architecture

This directory contains the production architecture baseline for POS Production Development Specification V2.

## Phase boundary

This bootstrap establishes project structure, architecture boundaries, configuration conventions, and development guardrails. Database schema, migrations, persistence implementations, and production data wiring are intentionally deferred to the Database Phase.

## Architectural boundaries

- POS/application layer owns deterministic business workflows.
- AI Orchestrator coordinates specialist agents and produces the final AI-facing result when an AI capability is explicitly enabled.
- Specialist agents must not access the database directly.
- Deterministic backend services own pricing, VAT, discounts, stock, payments, and refunds.
- External integrations are isolated behind explicit interfaces/adapters.
- The PRODX POS runtime and core CI must not depend on an external AI provider credential.
- GPT/ChatGPT connector authentication is an external development-plane concern and must never be copied into application configuration.
- Secrets required by the application or deployment infrastructure are supplied only through the appropriate environment/deployment secret mechanism; no credentials are committed.

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

## Development-plane boundary

The approved development model is:

`Project Owner command → ChatGPT/GitHub connector → repository → automated gates → review → acceptance → merge → main verification`

This development-plane connector is not an application dependency. PRODX POS must remain fully buildable, testable, and runnable without an OpenAI Platform API credential.
