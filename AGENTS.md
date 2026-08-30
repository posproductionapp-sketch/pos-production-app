# PRODX POS Agent Policy

## OpenCode fallback

OpenCode is an authorized fallback coding agent for PRODX POS when Codex is unavailable, rate-limited, or otherwise unable to execute the assigned repository work.

OpenCode may perform the same engineering workflow within the repository, subject to the same Production requirements:

- Work only from the current repository state and existing project specifications.
- Preserve Architecture, Security, Financial Integrity, Inventory Integrity, Multi-Tenant Isolation, Idempotency, Auditability, Offline Resilience, and Server Authority requirements.
- Read existing documentation, tests, CI workflows, and architecture contracts before changing implementation.
- Prefer small, reviewable changes on a dedicated branch.
- Run relevant tests and quality gates after changes; do not weaken or remove gates to make a check pass.
- Never commit secrets, credentials, private keys, tokens, or environment-specific sensitive values.
- Do not bypass branch protection, required reviews, or merge gates.
- Treat CI failures as blocking until diagnosed and fixed or explicitly documented as an external blocker.
- Do not declare a milestone complete without evidence from the relevant verification gates.
- When Codex becomes available again, OpenCode work remains subject to the same review and acceptance gates; Codex does not need to overwrite valid OpenCode work.

## Authority model

This file authorizes OpenCode as a fallback implementation agent. It does not grant credentials or bypass GitHub/OCI permissions. Provider authentication and local execution permissions remain controlled by the environment.

## Preferred execution model

Use OpenCode's full-access build agent only inside the PRODX repository, with repository permissions required for the assigned task. Use plan/read-only mode for investigation when implementation authority is not needed.

The fallback relationship is:

`Codex available -> Codex primary`

`Codex unavailable/limited -> OpenCode fallback`

`Both available -> either may execute, but all changes use the same Production Gates and review policy.`
