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
- Do not bypass branch protection or merge gates.
- Treat CI failures as blocking until diagnosed and fixed or explicitly documented as an external blocker.
- Do not declare a milestone complete without evidence from the relevant verification gates.
- If a future external AI capability is needed, isolate it behind an optional integration boundary; it must never become a required dependency of the POS runtime or core CI.

## AI-only review policy

Routine repository review is an AI-operated control. Human review is not a required engineering step for ordinary changes because the Project Owner has explicitly selected an AI-only review workflow to reduce human review error and keep execution autonomous.

Every change must receive an explicit AI technical review by the connected ChatGPT/GitHub execution workflow before acceptance. The AI review must inspect the actual diff and relevant repository context and must verify, at minimum:

- Architecture and module-boundary compliance.
- Security and secret-handling constraints.
- Financial and inventory integrity invariants where applicable.
- Multi-tenant isolation and authorization boundaries where applicable.
- Idempotency, auditability, offline resilience, and server-authority requirements where applicable.
- Test coverage and CI evidence appropriate to the risk of the change.
- No unjustified weakening or bypass of quality gates.

AI review is separate from the automated test/quality gates: gates provide deterministic evidence, while AI review provides contextual engineering assessment. A change is blocked when either layer fails. The AI review result must be recorded in the PR discussion or other repository-visible evidence before merge.

Human involvement is limited to decisions or approvals that genuinely require Project Owner authority, such as business requirements, protected credentials, or external operations unavailable to the execution workflow. Human code review is not a mandatory merge prerequisite.

## Authority model

The Project Owner controls business decisions, protected approvals, credentials that are genuinely required by deployment infrastructure, and actions unavailable to the execution agents. Repository implementation should remain AI-operated through the connected GitHub workflow. Connector authentication and permissions are external to the PRODX application and must never be copied into the repository.

## Execution relationship

`Project Owner command -> ChatGPT/GitHub connector -> repository implementation -> automated gates -> AI technical review -> acceptance -> merge -> main verification -> report`

Owner involvement should be limited to decisions and approvals that genuinely require owner authority; routine coding, testing, diagnosis, refactoring, review, and repository maintenance are execution responsibilities.
