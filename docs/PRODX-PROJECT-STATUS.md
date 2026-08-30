# PRODX POS — Project Status

> Canonical working status tracker. Update this file at each milestone boundary and after material workflow changes.

## Owner / Execution Model

- Project Owner: repository owner
- Technical Lead / Executor: ChatGPT
- Primary coding agent: Codex
- Fallback coding agent: OpenCode when Codex is unavailable or rate-limited
- OpenCode work must receive independent review before a milestone is accepted.
- Owner-only actions are limited to credentials, protected approvals, and operations unavailable to the execution agents.

## Approved Engineering Workflow

`Plan → Implement → Automated Tests → Architecture/Security/Integrity Gates → Independent Review (OpenCode/Codex) → Fix findings → Acceptance → Merge → Main Verification → Next Milestone`

No milestone is considered complete without evidence from the applicable gates. Gates must not be weakened or bypassed.

## Milestone Roadmap

| Milestone | Scope | Status |
|---|---|---|
| M0 | Architecture | Baseline established |
| M1 | Database | Baseline established; PostgreSQL/migration/integration gates established |
| M2 | Authentication & Authorization | In progress / verify against current main |
| M3 | Catalog & Inventory | In progress / verify against current main |
| M4 | POS / Checkout | Next feature milestone after workflow/policy backlog is reconciled |
| M5 | Payments | Planned |
| M6 | Shift & Cash | Planned; schema work exists |
| M7 | Void & Refund | Planned |
| M8 | Offline | Planned |
| M9 | Hardware | Planned |
| M10 | Reports | Planned |
| M11 | Production Hardening | Planned |
| M12 | Production Deployment | Planned |

## Current Repository State

- PR25: merged into `main`.
- Current known PR25 merge commit: `ac11528a`.
- Open PRs after PR25 include workflow/agent-policy work: PR27, PR28, PR29, PR30.
- PR27: authorizes OpenCode as a fallback implementation agent.
- PR28: adds a guarded GitHub Actions OpenCode fallback runner.
- PR29: documents runner access architecture.
- PR30: documents the canonical PRODX architecture/workflow standard.
- These policy/runner PRs are not themselves POS business-feature milestones.

## Secret / Provider Configuration

- `OPENAI_API_KEY`: expected to be supplied through GitHub Actions secrets/environment only.
- `ANTHROPIC_API_KEY`: expected to be supplied through GitHub Actions secrets/environment only.
- Provider credentials must never be committed to the repository.

## Completion Rule

A milestone may be marked complete only when implementation, relevant tests, production/security/architecture gates, independent OpenCode/Codex review, acceptance, merge, and post-merge main verification all pass.

## Update Discipline

When work advances, update this file at the next meaningful milestone boundary with:
1. Current milestone and status.
2. PR/commit references.
3. Gates and review result.
4. Remaining blockers.
5. Next milestone.

Do not record secrets, tokens, private credentials, or other sensitive values here.
