# Frontend Session and RBAC Completion Gate

## Acceptance criteria

- After successful login, the client must call `GET /v1/me` using the bearer token.
- The client must not enter the authenticated application state unless `/v1/me` succeeds.
- The client must clear the session token when `/v1/me` rejects the session.
- Tenant and store identity shown by the UI must come from the authenticated `/v1/me` principal, never from editable client state.
- Navigation visibility/access affordances must be derived from server-provided roles.
- Backend authorization remains authoritative; frontend RBAC is a UX guard and must never be treated as a security boundary.
- Regression tests must cover session hydration and representative role restrictions.
