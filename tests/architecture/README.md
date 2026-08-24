# Architecture Test Skeleton

These tests are the enforcement layer for `docs/architecture/CONTRACTS.md`.

## Required checks

- Domain imports remain framework/vendor/AI independent.
- Specialist agents cannot access persistence directly.
- Services use explicit interfaces for external integrations.
- Configuration is environment-driven and contains no committed secrets.
- Database implementations remain deferred until the Database Phase gate.

Executable checks should be added once the application language/build/test stack is selected. The test directory must not become a second source of architectural rules; every assertion should map back to a documented contract.
