# Reporting

Phase 10 exposes read-only, store-scoped operational reports from authoritative transaction data.

## Endpoints

- `GET /v1/reports/sales?start=<ISO-8601>&end=<ISO-8601>` — paid order count, item quantity, gross sales, refunds, net sales, and captured payments by provider.
- `GET /v1/reports/inventory?start=<ISO-8601>&end=<ISO-8601>` — current balances plus inventory movement totals by SKU and reason.
- `GET /v1/reports/shifts?start=<ISO-8601>&end=<ISO-8601>` — shift lifecycle, cash movement totals, expected cash, and closing variance.

All timestamps must include an offset or `Z` and are normalized to UTC. Reports are restricted to manager/admin roles and are always scoped to the authenticated store.

Report queries are read-only. They do not create, update, lock, or otherwise mutate operational records.
