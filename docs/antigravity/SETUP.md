# Antigravity Setup for PRODX POS

This repository contains workspace-level Google Antigravity rules and custom agents under `.agents/`.

## What is already configured in the repository

- `.agents/rules/prodx-core.md` — core PRODX production rules.
- `.agents/agents/prodx-engineer.md` — implementation agent.
- `.agents/agents/prodx-qa.md` — independent QA/verification agent.
- `.agents/agents/prodx-security.md` — security/architecture-risk agent.
- `.agents/agents/prodx-reviewer.md` — final independent AI technical reviewer.
- `AGENTS.md` — repository-wide connector-first and AI-only review policy.

Antigravity supports workspace custom agents/rules and the CLI can operate in Linux and remote/SSH environments. These repository files provide the PRODX policy layer; they do not install Antigravity or grant it credentials automatically.

## Recommended model for an owner without a local development machine

Use a persistent Linux cloud development machine as the Antigravity worker. GitHub Codespaces remains a valid existing development environment, but this repository does **not** assume that the full Antigravity IDE is installed inside Codespaces. If the Antigravity CLI is experimentally used inside a Codespace, treat the Codespace lifecycle and authentication behavior as an environment-specific constraint rather than a production dependency.

Recommended separation:

`Owner/mobile -> ChatGPT + GitHub connector -> GitHub -> Antigravity worker -> PR -> CI gates -> AI review -> merge`

The Antigravity worker may be a cloud VM/server that the owner controls. Antigravity Remote Control can provide browser access to Antigravity sessions running on machines/servers; the worker must remain persistent enough for the intended development workflow.

## One-time worker setup

1. Provision a persistent Linux development machine/VM under the owner's control.
2. Install Antigravity CLI using Google's official Linux installer.
3. Sign in with the Google account that has the Google AI Pro subscription using the supported account-auth flow. Do **not** use a third-party token bridge or proxy.
4. Clone `posproductionapp-sketch/pos-production-app` and open the repository from the worker workspace.
5. Confirm the four `prodx-*` custom agents are discoverable from `.agents/agents/` and keep `prodx-core.md` enabled as the workspace rule.
6. Configure GitHub access using Antigravity's supported authenticated tooling. Never copy ChatGPT connector credentials, GitHub tokens, Google OAuth tokens, or provider secrets into the repository.
7. Keep sandbox/permission controls enabled. Start with approval for writes and command execution; expand only after the worker has been validated.
8. Optionally enable Antigravity Remote Control so the worker can be operated from a browser/mobile device.

## Codespaces note

The existing GitHub Codespace should not be modified merely to install the Antigravity desktop IDE. The official Antigravity CLI is a native Linux CLI and is documented for remote/SSH workflows, but Google does not document GitHub Codespaces as a first-class Antigravity IDE deployment target. If Codespace CLI use is tested later, it must remain optional and must not change PRODX runtime or CI requirements.

## Operating model

`Owner command -> ChatGPT/GitHub connector -> repository -> Antigravity cloud worker -> tests -> GitHub PR -> CI gates -> independent AI review -> acceptance -> merge -> main verification`

Antigravity is an implementation/verification worker. The repository's automated gates and AI review policy remain authoritative.

## Prohibited shortcuts

- Do not add an OpenAI Platform API key dependency.
- Do not add a Gemini API key to the application runtime merely to operate the development workflow.
- Do not use third-party software to extract, proxy, or reuse Antigravity account tokens.
- Do not bypass CI or branch protection.
- Do not disable or weaken architecture/security/quality tests.
- Do not put credentials or tokens in repository files.
- Do not treat local/cloud Antigravity success as production certification.

## Subscription note

Google AI Pro can provide access to Antigravity subject to Google's current plan limits, model availability, and quotas. The repository must remain provider-independent at runtime.
