# PRODX POS Agent Policy

## OpenCode primary

OpenCode is the primary implementation agent for PRODX POS. Codex is an authorized secondary/review agent when available and useful, but Codex availability or quota must never block implementation progress.

OpenCode may perform the full engineering workflow within the repository, subject to the same Production requirements:

- Work only from the current repository state and existing project specifications.
- Preserve Architecture, Security, Financial Integrity, Inventory Integrity, Multi-Tenant Isolation, Idempotency, Auditability, Offline Resilience, and Server Authority requirements.
- Read existing documentation, tests, CI workflows, and architecture contracts before changing implementation.
- Prefer small, reviewable changes on a dedicated branch.
- Run relevant tests and quality gates after changes; do not weaken or remove gates to make a check pass.
- Never commit secrets, credentials, private keys, tokens, or environment-specific sensitive values.
- Do not bypass branch protection, required reviews, or merge gates.
- Treat CI failures as blocking until diagnosed and fixed or explicitly documented as an external blocker.
- Do not declare a milestone complete without evidence from the relevant verification gates.
- Codex review is supplemental and must not be treated as a prerequisite when unavailable or rate-limited; the same mandatory automated gates and independent review policy still apply.

## Authority model

This file authorizes OpenCode as the primary implementation agent. It does not grant credentials or bypass GitHub/OCI permissions. Provider authentication and execution permissions remain controlled by the environment.

## Preferred execution model

Use OpenCode's full-access build agent for implementation and repository maintenance. Use plan/read-only mode for investigation when implementation authority is not needed. Use Codex as a secondary review/analysis agent when available, without making it a single point of failure.

The execution relationship is:

`OpenCode available -> OpenCode primary`

`Codex available -> secondary review/analysis`

`Codex unavailable/limited -> continue with OpenCode`

`All work -> same Production Gates and review policy.`
