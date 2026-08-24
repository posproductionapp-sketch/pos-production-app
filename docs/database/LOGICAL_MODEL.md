# V2 Logical Data Model — Draft

Status: design baseline only. No migrations are created by this document.

## Core bounded areas

1. **Organization / tenancy** — stores, store configuration, operational scope.
2. **Identity / authorization** — users, roles, permissions, user-store assignments.
3. **Catalog** — products, variants/SKUs, prices, tax configuration.
4. **Sales** — sales transactions and immutable line-item snapshots.
5. **Orders** — order lifecycle and fulfillment state.
6. **Inventory** — stock locations, balances, movements, adjustments, and reasons.
7. **Payments** — payment attempts, captures, refunds, payment method metadata.
8. **Audit** — actor, action, resource, before/after metadata, timestamp, correlation/idempotency identifiers.
9. **Idempotency** — request key scoped to tenant/store and operation, with durable result reference.

## Integrity requirements

- Every operational record has an explicit store/tenant scope where applicable.
- Sale and payment records retain the historical values required for audit and reconciliation.
- Inventory changes are represented as movements; balances are derived/maintained from those movements under transaction control.
- Refunds reference the original payment/sale context and cannot exceed refundable amounts.
- Idempotency keys are unique within their defined scope.
- Monetary amounts use decimal/exact numeric storage with explicit currency.
- Timestamps are timezone-aware and normalized consistently.
- Soft deletion is not a substitute for audit history.

## Review gate

Before migrations: review cardinalities, unique constraints, lifecycle states, indexes, transaction boundaries, concurrency strategy, retention/audit policy, and tenant/store isolation.
