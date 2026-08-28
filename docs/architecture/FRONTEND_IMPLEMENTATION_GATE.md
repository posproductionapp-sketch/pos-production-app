# Frontend Implementation Gate

Status: **OPEN — frontend workspace not yet present**

## Repository verification

The current `main` branch is a Python/FastAPI production POS core. The repository does not currently contain a `package.json` or a discoverable React/TypeScript frontend workspace.

## Decision

Do not introduce an arbitrary frontend framework or build system into the repository until the frontend workspace decision is explicit.

The approved UI contracts are ready:

- `docs/design/PRODX_POS_FINAL_LOGO.md`
- `docs/design/PRODX_POS_COMPONENT_FOUNDATION.md`
- `docs/design/PRODX_POS_LOGIN_UI_SPEC.md`

## Required next implementation decision

Create the frontend workspace according to the project specification (React + TypeScript PWA is the recommended baseline), then implement the Login UI against the existing `POST /v1/auth/login` API.

## Safety constraints

- Do not alter domain, application, database, authentication, or architecture gates merely to enable UI work.
- Do not duplicate backend authentication logic in the client.
- Do not invent unsupported authentication endpoints or flows.
- Keep the final logo and design tokens as shared reusable assets.
- Require build, lint/type checks, and relevant E2E coverage before declaring the Login UI production-ready.

## Gate outcome

**BLOCKED only on frontend workspace creation/selection.** Backend authentication and the UI specification are already available for integration.
