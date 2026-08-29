import { describe, expect, it } from 'vitest';

type User = { roles: string[] };
const access = (user: User, allowed: string[]) => allowed.some(role => user.roles.includes(role));

describe('RBAC navigation contract', () => {
  it('keeps settings admin-only', () => {
    expect(access({ roles: ['admin'] }, ['admin'])).toBe(true);
    expect(access({ roles: ['manager'] }, ['admin'])).toBe(false);
    expect(access({ roles: ['cashier'] }, ['admin'])).toBe(false);
  });
  it('allows inventory roles into inventory navigation', () => {
    expect(access({ roles: ['inventory'] }, ['admin', 'manager', 'inventory'])).toBe(true);
    expect(access({ roles: ['cashier'] }, ['admin', 'manager', 'inventory'])).toBe(false);
  });
});
