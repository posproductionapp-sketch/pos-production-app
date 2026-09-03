# PRODX POS — Antigravity Core Rules

These workspace rules apply to Google Antigravity when working in this repository.

## Mission

Treat PRODX POS as a production system, not a prototype. Work from the current repository state and existing project specifications. Preserve the repository's established architecture and quality controls.

## Non-negotiable invariants

- Financial Integrity: never use floating-point arithmetic for money; preserve exact decimal semantics and server authority.
- Inventory Integrity: inventory mutations are transactional, auditable, and protected against race conditions and invalid quantities.
- Multi-Tenant Isolation: every tenant/store-scoped operation must enforce the correct authorization and data boundary.
- Security by Default: never weaken authentication, authorization, validation, secret handling, or security headers to make work easier.
- Idempotency: preserve idempotency guarantees for operations that can be retried, especially sales, payments, refunds, and synchronization.
- Auditability: material business/security changes must remain traceable.
- Offline Resilience: offline-capable behavior must preserve correctness when reconnecting and synchronizing.
- Server Authority: client state is never authoritative for financial, inventory, permission, or other protected business decisions.

## Repository policy

- Read `AGENTS.md`, relevant `docs/`, tests, architecture contracts, and CI workflows before changing implementation.
- Treat `AGENTS.md` as the repository-level policy and this file as Antigravity-specific workspace guidance.
- Prefer small, reviewable changes on a dedicated branch.
- Never commit secrets, credentials, private keys, tokens, or environment-specific sensitive values.
- Never add an OpenAI Platform API key or make an OpenAI Platform API key a runtime, test, CI, or development requirement.
- External AI/provider integrations must remain optional and isolated behind an explicit boundary.

## Quality gates

- Do not remove, weaken, skip, or bypass an automated gate merely to obtain a passing result.
- A failing test or quality gate is blocking until diagnosed and fixed or explicitly identified as an external blocker.
- Run the narrowest relevant tests during iteration, then run the repository's required quality gates before acceptance.
- Do not claim a milestone is complete without repository-visible verification evidence.
- AI review is separate from deterministic CI gates; both are required by the repository policy.

## Change discipline

Before editing:
1. Identify the capability and its acceptance criteria.
2. Inspect affected architecture boundaries and existing patterns.
3. Identify security, financial, inventory, tenancy, idempotency, audit, offline, and migration risks.

After editing:
1. Review the actual diff for unintended changes.
2. Run relevant tests and quality gates.
3. Check migrations and integration behavior when database code changes.
4. Verify no policy or architecture gate was weakened.
5. Leave clear evidence for the next reviewer/agent.

## Agent boundaries

Antigravity may inspect, implement, test, refactor, and prepare PRs. It must not bypass branch protection, disable CI, rewrite history destructively, alter protected production infrastructure, or declare Production Ready without the required evidence.

When uncertain, preserve the existing invariant and stop for a decision rather than inventing a shortcut.
