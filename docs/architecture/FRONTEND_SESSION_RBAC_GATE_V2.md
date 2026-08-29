# Frontend Session and RBAC Gate

The frontend authenticates with the server-issued bearer token, hydrates identity from `GET /v1/me`, clears invalid sessions, displays tenant/store identity from the principal, and derives navigation access from server-provided roles. Backend authorization remains the security boundary.
