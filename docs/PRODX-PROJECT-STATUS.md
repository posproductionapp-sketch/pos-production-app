# PRODX POS — Project Status

> Canonical working status tracker. Update this file at each milestone boundary and after material workflow changes.

## Last Verified

- Verification date: 2026-08-31
- Current main after PR31: `36c4ac50f70e366dade22e6e516a7c36fbd9eefd`
- PR31 (`docs: add PRODX project status tracker`): merged successfully.
- This tracker is now present on `main` and is the canonical project-status record.

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

- PR25: merged into `main`; known merge commit before the status-tracker update was `ac11528a`.
- PR31: merged into `main` as commit `36c4ac50f70e366dade22e6e516a7c36fbd9eefd`.
- PR27: open; authorizes OpenCode as a fallback implementation agent.
- PR28: open; adds a guarded GitHub Actions OpenCode fallback runner.
- PR29: open; documents runner access architecture.
- PR30: open; documents the canonical PRODX architecture/workflow standard.
- The PR27–30 workflow/policy items are not themselves POS business-feature milestones.

## Current Milestone Focus

**M2/M3 verification and reconciliation** are the current feature-development focus. Before advancing to M4, the implementation present on `main` must be inspected against the POS Production Development Specification V2 and the applicable architecture/security/integrity contracts. Existing implementation must not be assumed complete solely because files or schemas exist.

## Verification / Acceptance State

- PR31 merge: PASS.
- Main status-tracker presence: PASS.
- Full automated test/CI result for the current `main`: not yet re-verified in this status update.
- Independent OpenCode review for the current feature milestone: not yet evidenced in this status update.
- M2/M3 acceptance: NOT COMPLETE until implementation, gates, independent review, acceptance, merge, and post-merge main verification are evidenced.

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
