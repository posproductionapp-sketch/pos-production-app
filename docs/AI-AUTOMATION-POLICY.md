# AI Autonomous Engineering Workflow

## Owner approval policy

Project owner has approved an AI-first autonomous engineering workflow for development, with human approval retained as the production safety boundary.

### Development phase

- AI agents may inspect the repository, triage issues, implement fixes, create/update PRs, run tests, diagnose CI failures, and iterate on fixes automatically.
- OpenCode is the primary implementation agent using the configured OpenAI model and repository secret `OPENAI_API_KEY`.
- Automation should not require routine owner button-clicks or `/opencode` comments for normal engineering work.
- AI must preserve production, security, architecture, testing, financial integrity, inventory integrity, multi-tenant isolation, idempotency, auditability, offline resilience, server-authority, and merge gates.
- AI must not weaken or bypass required checks, branch protection, secret-management rules, or other repository safety controls.
- AI-generated changes should be validated by the existing CI gates before being considered complete.
- Fork/untrusted-code protections must remain in place; privileged secrets must never be exposed to untrusted workflows.

### Human approval boundary

Until the project is genuinely operating in production:

- AI **must not auto-merge** production-bound changes.
- AI **must not deploy to production**.
- The project owner is the final approver for merges and production release decisions.

### Production transition

When the project owner explicitly declares that the project is live in production, this policy may be revised to enable controlled AI auto-merge and deployment, subject to all required quality, security, release, and rollback gates.

This document records the owner's approved operating policy and should be treated as a repository-level engineering constraint.