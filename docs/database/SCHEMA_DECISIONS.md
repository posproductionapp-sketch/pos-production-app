# Database Decision Gate

## Decision status

**NOT APPROVED FOR MIGRATIONS**

The logical model and schema review are now documented. Physical schema implementation remains blocked until the database technology and the remaining persistence decisions are explicitly approved.

## Required decisions

- Database engine: TBD
- ORM/query layer: TBD
- Migration tooling: TBD
- Isolation level / concurrency strategy: TBD
- Money and currency representation: exact decimal + explicit currency required
- Timestamp standard: timezone-aware, normalized storage required
- Tenant/store isolation: explicit application + database constraints required
- Audit retention: TBD
- Reference/seed data policy: TBD

## Gate rule

Codex may implement migrations only after these decisions are approved and recorded in this file.
