# Architecture Contracts

Status: Production implementation phase
Source of truth: POS Production Development Specification V2
Database Decision Gate: **APPROVED**

## 1. Dependency direction

- `app` may coordinate domain/services/configuration and application transaction boundaries.
- `services` may depend on domain contracts and explicit integration interfaces.
- `domain` must remain deterministic and must not depend on AI, database, HTTP, or vendor SDKs.
- `agents` may orchestrate specialist capabilities but must not access persistence directly.
- `integrations` owns adapters for external systems and vendor SDKs.
- `infrastructure` owns technical implementations, including the approved PostgreSQL/SQLAlchemy persistence boundary.
- `config` owns environment/configuration loading and validation only.

## 2. Deterministic business boundary

Pricing, VAT, discounts, stock, payments, and refunds are deterministic backend responsibilities. AI output must not silently override these decisions.

## 3. Agent boundary

Specialist agents communicate through explicit contracts. They do not import database clients, ORM models, repository implementations, payment gateways, or other infrastructure details directly.

## 4. Integration boundary

External APIs and tools are accessed through explicit interfaces/adapters. Domain and service logic must not depend on vendor-specific clients.

## 5. Configuration and secrets

Secrets are supplied through environment variables or the deployment secret manager. Credentials, API keys, and production secrets must never be committed to the repository.

## 6. Database implementation boundary

The Database Decision Gate is approved. PostgreSQL + SQLAlchemy 2.x + Alembic are authorized by the reviewed schema decisions.

Database implementation must remain under `src/infrastructure/database/`. Domain objects and application contracts must not import ORM models or database sessions directly.

Repository adapters must not commit transactions implicitly. Application/use-case boundaries own commit/rollback so financial, inventory, idempotency, and audit operations can remain atomic.

## 7. Contract-test intent

Architecture tests must enforce at minimum:

1. domain has no infrastructure/AI/vendor dependency;
2. agents have no direct database dependency;
3. services depend on explicit contracts rather than vendor SDKs;
4. configuration does not contain committed secrets;
5. database implementations remain behind the infrastructure boundary;
6. persistence adapters preserve store/tenant isolation;
7. transaction ownership remains at application/use-case boundaries.
