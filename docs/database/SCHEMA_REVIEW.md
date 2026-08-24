# Database Schema Review — Specification V2

Status: **Review baseline — no migrations yet**

## 1. Tenant / store boundary

Every operational aggregate is scoped to a store. If the deployment supports multiple tenants, tenant ownership is explicit and store belongs to exactly one tenant. Cross-store reads/writes require an application-level authorization decision.

## 2. Identity and authorization

Core entities:
- `users`
- `roles`
- `permissions`
- `user_roles`
- `user_store_assignments`

Authorization is evaluated before application services execute privileged operations. Database foreign keys enforce referential integrity but are not the authorization mechanism.

## 3. Catalog

Core entities:
- `products`
- `product_variants`
- `prices`
- `tax_profiles`

SKU/variant identity is unique within the intended scope. Historical sale lines store the effective product description, SKU, unit price, tax values, and discount values needed for audit rather than relying on mutable catalog state.

## 4. Sales and orders

Core entities:
- `sales`
- `sale_items`
- `orders`
- `order_items`

A sale is financially authoritative once finalized. Sale item snapshots are immutable after finalization. Order lifecycle state changes are constrained to valid transitions at the application layer and represented durably in the database.

## 5. Inventory

Core entities:
- `stock_locations`
- `inventory_balances`
- `inventory_movements`
- `inventory_adjustments`

Inventory movements are append-oriented records. Balance updates occur in the same transaction as the movement that caused them. Concurrency control must prevent lost updates and negative stock where policy disallows it.

## 6. Payments and refunds

Core entities:
- `payments`
- `payment_attempts`
- `refunds`

Payment provider references are unique within the provider's scope. Refund amount cannot exceed the refundable captured amount. Sensitive payment credentials/card data are never persisted; only provider-safe metadata is stored.

## 7. Audit

Core entity: `audit_logs`

Required attributes include actor, store/tenant scope, action, resource type/id, timestamp, correlation id, and structured before/after metadata where appropriate. Audit records are append-oriented and are not used as a substitute for transactional state.

## 8. Idempotency

Core entity: `idempotency_keys`

Uniqueness is scoped by tenant/store + operation + key. A successful request stores a durable reference to its result. Retry handling must return the original result rather than executing the operation twice.

## 9. Key constraints and indexes

Minimum review set before migrations:

- PK on every entity.
- FK for every required aggregate relationship.
- Unique constraints for SKU/business identifiers, provider references, and scoped idempotency keys.
- Composite indexes beginning with store/tenant scope for high-volume operational queries.
- Timestamp indexes for audit, movements, orders, and payments where query patterns require them.
- Check/enum constraints for currency, positive monetary quantities, and lifecycle states where supported by the selected database.
- Explicit `created_at` / `updated_at` policy; finalized financial records must not silently mutate historical values.

## 10. Transaction boundaries

Transactions are owned by application use cases. At minimum:

- finalize sale + inventory movement + payment state transition must be coordinated according to payment workflow;
- inventory movement + balance update is atomic;
- refund + refundable-amount update is atomic;
- idempotency record creation and successful result persistence are coordinated to prevent duplicate execution.

## 11. Migration gate

Do not create production migrations until the team approves:

1. database engine/ORM choice;
2. exact column types and nullability;
3. cardinalities and cascade/restrict behavior;
4. unique and composite indexes;
5. concurrency strategy;
6. retention and audit policy;
7. tenant/store isolation strategy;
8. seed/reference-data strategy.
