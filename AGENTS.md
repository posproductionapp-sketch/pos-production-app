# PRODX POS Agent Policy

## Connector-first autonomous execution

ChatGPT through the connected GitHub workflow is the primary development interface for PRODX POS. The Project Owner issues natural-language commands through the connector; the AI execution workflow is responsible for repository inspection, implementation, testing, quality gates, review coordination, and reporting.

The PRODX POS repository must not require or invoke an OpenAI Platform API key for application runtime, CI, tests, or the core development workflow. No OpenAI Platform API-key environment-variable dependency may be introduced. GPT/connector authentication is external to the application repository and must not be implemented as an application credential.

The AI execution workflow may perform the full engineering workflow within the repository, subject to the same Production requirements:

- Work only from the current repository state and existing project specifications.
- Preserve Architecture, Security, Financial Integrity, Inventory Integrity, Multi-Tenant Isolation, Idempotency, Auditability, Offline Resilience, and Server Authority requirements.
- Read existing documentation, tests, CI workflows, and architecture contracts before changing implementation.
- Prefer small, reviewable changes on a dedicated branch.
- Run relevant tests and quality gates after changes; do not weaken or remove gates to make a check pass.
- Never commit secrets, credentials, private keys, tokens, or environment-specific sensitive values.
- Do not add provider API-key configuration merely to unblock development or tests.
- Do not bypass branch protection, required reviews, or merge gates.
- Treat CI failures as blocking until diagnosed and fixed or explicitly documented as an external blocker.
- Do not declare a milestone complete without evidence from the relevant verification gates.
- If a future external AI capability is needed, isolate it behind an optional integration boundary; it must never become a required dependency of the POS runtime or core CI.

## Authority model

The Project Owner controls business decisions, protected approvals, credentials that are genuinely required by deployment infrastructure, and actions unavailable to the execution agents. Repository implementation should remain AI-operated through the connected GitHub workflow. Connector authentication and permissions are external to the PRODX application and must never be copied into the repository.

## Execution relationship

`Project Owner command -> ChatGPT/GitHub connector -> repository implementation -> automated gates -> review -> acceptance -> merge -> main verification -> report`

Owner involvement should be limited to decisions and approvals that genuinely require owner authority; routine coding, testing, diagnosis, refactoring, and repository maintenance are execution responsibilities.
