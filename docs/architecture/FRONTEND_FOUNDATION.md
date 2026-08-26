# Frontend Foundation

The POS web client is introduced as a separate React/TypeScript/Vite application under `frontend/` while the existing FastAPI service remains the authoritative backend boundary.

## Initial scope

- Responsive, production-oriented login experience.
- Authentication request wired to `POST /v1/auth/login`.
- Backend remains authoritative for tenant, store, role, and permission context.
- No bearer token is persisted in `localStorage`.
- API base URL is environment-configurable.
- Frontend build is a required CI quality check.

## Next implementation gates

1. Define a typed API client and session boundary.
2. Add tenant/store context hydration from `/v1/me`.
3. Implement authenticated application shell and RBAC-aware navigation.
4. Introduce IndexedDB-backed offline command/outbox integration only after the sync contract is finalized.
5. Add browser E2E coverage for login, checkout, refund, shift, and reconnect flows.
