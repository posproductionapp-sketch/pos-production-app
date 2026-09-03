# Antigravity Setup for PRODX POS

This repository contains workspace-level Google Antigravity rules and custom agents under `.agents/`.

## What is already configured in the repository

- `.agents/rules/prodx-core.md` — core PRODX production rules.
- `.agents/agents/prodx-engineer.md` — implementation agent.
- `.agents/agents/prodx-qa.md` — independent QA/verification agent.
- `.agents/agents/prodx-security.md` — security/architecture-risk agent.
- `.agents/agents/prodx-reviewer.md` — final independent AI technical reviewer.
- `AGENTS.md` — repository-wide connector-first and AI-only review policy.

Antigravity automatically discovers workspace custom agents in `.agents/agents/` and workspace rules in `.agents/rules/`.

## One-time local setup

1. Install/open Google Antigravity 2.0 or the Antigravity CLI on the development machine.
2. Sign in with the Google account that has the Google AI Pro subscription.
3. Open this repository as the workspace.
4. Open the Agent Manager (`/agents`) and confirm the four `prodx-*` agents are discoverable.
5. In the Rules customization panel, make `prodx-core.md` an **Always On** workspace rule. Keep it workspace-scoped so it follows this repository rather than changing unrelated projects.
6. Connect GitHub/MCP only through Antigravity's own authenticated tooling. Never copy connector credentials, GitHub tokens, or provider API keys into the repository.
7. Keep Antigravity's local permission/sandbox controls enabled. Start with review/approval for writes and command execution; increase permissions only when the local workflow has been verified.

## Operating model

`Owner command -> ChatGPT/GitHub connector -> repository -> Antigravity local agent -> tests -> GitHub PR -> CI gates -> independent AI review -> acceptance -> merge -> main verification`

Antigravity is an implementation/verification worker. The repository's automated gates and AI review policy remain authoritative.

## Prohibited shortcuts

- Do not add an OpenAI Platform API key dependency.
- Do not bypass CI or branch protection.
- Do not disable or weaken architecture/security/quality tests.
- Do not put credentials or tokens in repository files.
- Do not treat local Antigravity success as production certification.

## Subscription note

Google AI Pro provides access to Antigravity with a higher quota than non-subscribed individual access. Quotas and model availability are controlled by Google and may change; the repository must remain provider-independent at runtime.
