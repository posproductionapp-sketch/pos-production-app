# PRODX Runner Access Architecture

## Purpose

Define the approved access model for PRODX automation when Codex is unavailable and OpenCode acts as the fallback implementation runner.

## Trust boundaries

`GitHub PR/Issue -> GitHub Actions -> OpenCode -> OCI`

Each boundary must be independently authenticated and least-privileged. Repository credentials must never be copied into source files, logs, or committed configuration.

## GitHub Actions

- Use the minimum required job permissions.
- Repository write access is limited to the runner job that needs it.
- Use `id-token: write` only for jobs that exchange an OIDC identity with OCI.
- Production deployment remains behind repository/environment protection and required checks.
- Direct pushes to `main` are prohibited by branch protection.

## OpenCode

Approved role: fallback implementation agent when Codex is unavailable or rate-limited.

Allowed:
- read repository files
- edit implementation files
- run deterministic tests and builds
- inspect git status/diff
- create a feature branch
- create/update a PR

Denied by default:
- reading secrets or credential stores
- direct writes to `main`
- disabling or weakening CI gates
- destructive infrastructure operations without an explicit protected workflow
- committing credentials, tokens, private keys, or generated secret material

## OCI identity

Preferred model: short-lived workload identity/OIDC from GitHub Actions rather than long-lived OCI private keys.

The OCI trust policy must restrict the identity to the PRODX repository and approved branch/environment conditions. IAM permissions must be scoped to the PRODX compartment/resources required by the workflow. Tenancy-wide administrator access is not permitted for the runner.

## Infrastructure workflow

1. Runner authenticates to GitHub and, only where required, obtains a short-lived OCI identity.
2. Runner validates the target compartment/resource state before making changes.
3. Network resources are created or reconciled idempotently.
4. Private database networking and NSG rules are established before PostgreSQL provisioning.
5. Compute/application resources are reconciled only after database/network gates pass.
6. Connectivity and migration checks run before deployment promotion.
7. Production deployment requires all mandatory Architecture, Security, Testing, and Production gates.

## Safety and recovery

All infrastructure actions must be idempotent where practical. Existing resources must be detected before creation. Failures must stop the workflow rather than silently continue with partial state. Recovery procedures must be documented before destructive changes are allowed.

## Completion criteria

Runner access is considered production-ready only after verifying:

- GitHub workflow permissions are correct.
- OIDC trust is restricted to PRODX.
- OCI identity exchange succeeds without a long-lived private key in the repository.
- IAM scope is limited to the intended PRODX compartment/resources.
- OpenCode can read/edit/test and create a PR.
- Secrets are inaccessible to the implementation agent except through explicitly required protected workflow inputs.
- Branch and environment protections remain active.
- End-to-end runner verification passes.

This document defines architecture and policy. It does not itself grant OCI permissions or create cloud credentials.