# Architecture Contracts

Status: Foundation baseline
Source of truth: POS Production Development Specification V2

## 1. Dependency direction

- `app` may coordinate domain/services/configuration.
- `services` may depend on domain contracts and explicit integration interfaces.
- `domain` must remain deterministic and must not depend on AI, database, HTTP, or vendor SDKs.
- `agents` may orchestrate specialist capabilities but must not access persistence directly.
- `integrations` owns adapters for external systems and vendor SDKs.
- `infrastructure` owns technical implementations; database persistence remains deferred until Database Phase.
- `config` owns environment/configuration loading and validation only.

## 2. Deterministic business boundary

Pricing, VAT, discounts, stock, payments, and refunds are deterministic backend responsibilities. AI output must not silently override these decisions.

## 3. Agent boundary

Specialist agents communicate through explicit contracts. They do not import database clients, ORM models, repository implementations, payment gateways, or other infrastructure details directly.

## 4. Integration boundary

External APIs and tools are accessed through explicit interfaces/adapters. Domain and service logic must not depend on vendor-specific clients.

## 5. Configuration and secrets

Secrets are supplied through environment variables or the deployment secret manager. Credentials, API keys, and production secrets must never be committed to the repository.

## 6. Database phase gate

No database schema, migration, ORM model, persistence implementation, or production data wiring is introduced by this foundation phase. Database work begins only after the Database Phase decision gate is approved.

## 7. Contract-test intent

Architecture tests must enforce at minimum:

1. domain has no infrastructure/AI/vendor dependency;
2. agents have no direct database dependency;
3. services depend on explicit contracts rather than vendor SDKs;
4. configuration does not contain committed secrets;
5. database implementation remains behind the infrastructure boundary until the phase gate is opened.
