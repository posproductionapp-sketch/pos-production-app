# PRODX POS — Project Status

> Canonical working status tracker. Update this file at each milestone boundary and after material workflow changes.

## Last Verified

- Verification date: 2026-09-02
- OpenAI API is intentionally **not required** for core development or CI.
- OpenCode autonomous workflow was removed from `main` because it required `OPENAI_API_KEY` and could block development when provider quota was exhausted.

## Owner / Execution Model

- Project Owner: repository owner
- Technical Lead / Executor: ChatGPT
- Primary coding agent: Codex when available
- AI coding providers are optional development assistants, never a dependency of the POS runtime or core quality gates.
- Owner-only actions are limited to credentials, protected approvals, and operations unavailable to the execution agents.

## Approved Engineering Workflow

`Plan → Implement → Automated Tests → Architecture/Security/Integrity Gates → Independent Review when available → Fix findings → Acceptance → Merge → Main Verification → Next Milestone`

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

## Current Milestone Focus

**M2/M3 verification and reconciliation** remain the current feature-development focus. Before advancing to M4, the implementation present on `main` must be inspected against the POS Production Development Specification V2 and the applicable architecture/security/integrity contracts. Existing implementation must not be assumed complete solely because files or schemas exist.

## Verification / Acceptance State

- Core development must remain runnable without OpenAI API credentials.
- AI provider availability must not determine whether application tests or core CI can execute.
- Full automated test/CI result for the post-change `main`: pending verification by GitHub Actions.
- M2/M3 acceptance: NOT COMPLETE until implementation, gates, independent review when required by risk tier, acceptance, merge, and post-merge main verification are evidenced.

## Secret / Provider Configuration

- `OPENAI_API_KEY`: optional provider credential only; not required by the core application or core development workflow.
- `ANTHROPIC_API_KEY`: optional provider credential only; not required by the core application or core development workflow.
- Provider credentials must never be committed to the repository.
- If an external AI provider is reintroduced later, it must be isolated behind an optional integration boundary and must not become a required application/CI dependency.

## Completion Rule

A milestone may be marked complete only when implementation, relevant tests, production/security/architecture gates, independent review when required by risk tier, acceptance, merge, and post-merge main verification all pass.

## Update Discipline

When work advances, update this file at the next meaningful milestone boundary with:
1. Current milestone and status.
2. PR/commit references.
3. Gates and review result.
4. Remaining blockers.
5. Next milestone.

Do not record secrets, tokens, private credentials, or other sensitive values here.
