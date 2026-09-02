# PRODX POS — Project Status

> Canonical working status tracker. Update this file at each milestone boundary and after material workflow changes.

## Last Verified

- Verification date: 2026-09-02
- PRODX POS core application, tests, CI, and development workflow are provider-independent.
- The autonomous provider-specific runner that could block development has been removed from the active development path.

## Owner / Execution Model

- Project Owner: repository owner
- Technical Lead / Executor: ChatGPT through the connected GitHub workflow
- Development interface: GPT/ChatGPT connector with direct repository access
- AI development is the default execution model; the Owner does not perform routine implementation, testing, diagnosis, review, or repository maintenance.
- OpenAI Platform API credentials are explicitly out of scope for the PRODX POS application, CI, tests, and core development workflow.
- Connector authentication is external to the application repository and must never be copied into application configuration.
- Owner-only actions are limited to business decisions, protected approvals, credentials genuinely required by deployment infrastructure, and operations unavailable to execution agents.

## Approved Engineering Workflow

`Owner Command → ChatGPT/GitHub Connector → Plan → Implement → Automated Tests → Architecture/Security/Integrity Gates → AI Technical Review → Fix Findings → Acceptance → Merge → Main Verification → Next Milestone`

AI Technical Review is mandatory for ordinary engineering changes. Human code review is not a required merge prerequisite. Deterministic automated gates and contextual AI review are separate controls; failure of either blocks acceptance. The AI review result must be recorded in repository-visible PR evidence before merge.

No milestone is considered complete without evidence from the applicable gates. Gates must not be weakened or bypassed.

## Provider Independence Rule

The repository must never require an OpenAI Platform API key to build, test, run CI, execute the POS application, or continue core development. A missing provider credential, provider quota, or provider outage must not stop core PRODX POS development.

If an AI-specific capability is introduced in the future, it must be optional, isolated behind an explicit integration boundary, and independently gated. It must not become a required dependency of the POS runtime or core CI.

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

- Core development must remain runnable without OpenAI Platform credentials.
- Provider availability must not determine whether application tests or core CI can execute.
- Full automated test/CI result for the post-change `main`: pending verification by GitHub Actions.
- M2/M3 acceptance: NOT COMPLETE until implementation, gates, AI technical review, acceptance, merge, and post-merge main verification are evidenced.

## Secret Policy

- No AI provider credentials belong in the PRODX POS application configuration.
- No provider API keys, access tokens, private keys, or other secrets may be committed to the repository.
- Connector authentication remains outside the application repository.
- Deployment credentials, when genuinely required by infrastructure, must use the deployment platform's supported secret mechanism and remain unrelated to the application development workflow.

## Completion Rule

A milestone may be marked complete only when implementation, relevant tests, production/security/architecture gates, AI technical review, acceptance, merge, and post-merge main verification all pass.

## Update Discipline

When work advances, update this file at the next meaningful milestone boundary with:
1. Current milestone and status.
2. PR/commit references.
3. Gates and AI review result.
4. Remaining blockers.
5. Next milestone.

Do not record secrets, tokens, private credentials, or other sensitive values here.
