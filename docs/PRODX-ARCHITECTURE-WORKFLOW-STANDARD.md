# PRODX Architecture & Workflow Standard

**Status:** Approved baseline  
**Applies to:** PRODX POS production development  
**Authority:** Project engineering standard; changes require explicit approval

## 1. Purpose

This document is the canonical engineering baseline for PRODX POS. All implementation, infrastructure, review, testing, and merge decisions must conform to this standard unless an explicit architecture exception is approved.

## 2. Architecture Principles

PRODX is developed as a production system, not a prototype. The architecture must preserve:

- **Multi-Tenant Data Isolation** — tenant/store boundaries are enforced server-side and at persistence boundaries.
- **Security by Default** — authentication, authorization, secret handling, input validation, least privilege, and secure defaults are mandatory.
- **Financial Integrity** — monetary values use exact decimal semantics; sales, payments, refunds, voids, VAT, and cash operations must remain auditable and consistent.
- **Inventory Integrity** — inventory changes follow controlled ledger/transaction semantics and cannot silently create inconsistent stock.
- **Server Authority** — authoritative business and financial state is determined by the backend/database, not by the client.
- **Idempotency** — retried operations must not create duplicate financial or inventory effects.
- **Auditability** — security-sensitive and business-critical mutations retain sufficient audit evidence.
- **Offline Resilience** — offline operation must use explicit outbox/synchronization semantics and preserve idempotency and conflict safety.
- **Deterministic Domain Logic** — domain behavior remains vendor-independent and testable.
- **Observability & Recovery** — production paths must support health checks, meaningful logs/metrics, backup/recovery, and operational verification.

## 3. System Architecture Baseline

The approved baseline consists of:

- POS Client: React + TypeScript PWA, responsive across mobile/tablet/desktop where applicable.
- Local client persistence/offline queue: IndexedDB + Service Worker/outbox pattern where required.
- Backend API: Node.js + TypeScript service architecture (NestJS or equivalent), typed/versioned APIs and OpenAPI contract.
- Database: PostgreSQL; money stored using `NUMERIC/DECIMAL`, timestamps normalized to UTC, with business timezone handled explicitly.
- Queue/cache: Redis where required for asynchronous work, caching, and coordination.
- Hardware Agent: local Node.js/Electron runtime for printer/cash-drawer and other approved hardware integration.
- Infrastructure: infrastructure-as-code and guarded deployment automation; application services remain isolated from public network exposure unless explicitly required.

## 4. Quality Gate Model

Every capability or milestone follows the same gate sequence:

1. **Architecture Gate** — confirm the change respects approved boundaries and domain contracts.
2. **Implementation Gate** — implement only within the approved capability scope.
3. **Automated Quality Gates** — compile/type checks, lint/static checks where applicable, unit/integration tests, migration checks, security/architecture contracts, and relevant frontend/backend certification.
4. **AI Technical Review** — the connected ChatGPT/GitHub development AI inspects the actual diff and relevant repository context for correctness, architecture, security, integrity, regression risk, and test sufficiency.
5. **AI Review Evidence Gate** — the AI review result is recorded in repository-visible PR evidence. Human code review is not a mandatory control for ordinary engineering changes.
6. **Milestone Acceptance Gate** — verify Definition of Done and all required evidence before merge.
7. **Merge Gate** — merge only when the required automated gates and AI review evidence are green; never bypass branch protection or failed required checks.
8. **Main Verification** — after merge, verify the resulting main branch and production-relevant checks again.

## 5. Risk and Review Rules

- AI technical review is mandatory for ordinary engineering changes.
- High-risk changes require deeper AI analysis and stronger automated evidence before acceptance.
- Database, authentication/authorization, financial, inventory, offline synchronization, infrastructure, and deployment changes are treated as high-impact areas unless explicitly classified otherwise.
- Human code review is not required for ordinary changes under the approved AI-only review policy. Owner involvement remains limited to business decisions, protected approvals, credentials genuinely required by deployment infrastructure, and operations unavailable to execution agents.
- Unavailable AI review capability blocks acceptance; it must not be replaced by a weaker human or ad-hoc review path.
- Credentials, private keys, passwords, tokens, and other secrets must never be committed to source control.

## 6. Database and Migration Rules

- One authoritative migration lineage/head must be maintained.
- Schema invariants should be enforced at the database boundary where practical.
- Migration upgrade/downgrade behavior must be tested for correctness and repeatability.
- Database-backed tests must run against the intended PostgreSQL version/configuration used by CI or the production-equivalent environment.
- Cross-tenant access must be explicitly tested and rejected.
- Concurrency-sensitive operations must be protected with appropriate transactions, constraints, locking, and/or idempotency mechanisms.

## 7. Infrastructure and Deployment Rules

Infrastructure is part of the production system and follows the same gate philosophy as application code.

- Infrastructure changes are isolated from certified application changes where practical.
- Terraform formatting/validation and applicable plan checks are mandatory before infrastructure acceptance.
- Existing manually-created resources must be imported/reconciled or intentionally removed before Terraform applies that could create duplicates.
- Production deployment is never implied by a successful code merge; deployment requires its own explicit verification gate.
- Public exposure is minimized; PostgreSQL and Redis remain private/internal unless a documented architecture decision explicitly requires otherwise.

## 8. Definition of Done

A capability is not complete merely because the implementation exists. It is complete only when:

- architecture contracts pass;
- relevant automated tests pass;
- database migrations and integration tests pass where applicable;
- security and tenant-isolation checks pass;
- required AI technical review and repository-visible review evidence pass;
- no required gate is bypassed or weakened;
- milestone acceptance criteria are satisfied; and
- post-merge/main verification is successful.

## 9. Change Control

This document is the canonical reference for PRODX engineering workflow and architecture. If implementation pressure conflicts with this standard, the standard wins. Any change to the standard itself requires explicit project-owner approval and should be recorded as a deliberate architecture/workflow decision rather than silently changing the rules in implementation.
