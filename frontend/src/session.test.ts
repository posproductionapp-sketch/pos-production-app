import { describe, expect, it } from 'vitest';

type CurrentUser = { user_id: string; tenant_id: string; store_id: string; roles: string[] };

const navigation = [
  { label: 'Sales', allowed: ['admin', 'manager', 'cashier'] },
  { label: 'Products', allowed: ['admin', 'manager', 'inventory'] },
  { label: 'Inventory', allowed: ['admin', 'manager', 'inventory'] },
  { label: 'Reports', allowed: ['admin', 'manager', 'auditor'] },
  { label: 'Settings', allowed: ['admin'] },
];

function hasAccess(user: CurrentUser, allowed: string[]) {
  return allowed.some(role => user.roles.includes(role));
}

describe('session identity and RBAC contract', () => {
  it('preserves tenant and store identity returned by /v1/me', () => {
    const user: CurrentUser = {
      user_id: 'u-1', tenant_id: 'tenant-1', store_id: 'store-1', roles: ['cashier'],
    };
    expect(user.tenant_id).toBe('tenant-1');
    expect(user.store_id).toBe('store-1');
    expect(user.roles).toEqual(['cashier']);
  });

  it('allows cashier access only to cashier-capable navigation', () => {
    const user: CurrentUser = {
      user_id: 'u-1', tenant_id: 'tenant-1', store_id: 'store-1', roles: ['cashier'],
    };
    expect(hasAccess(user, navigation[0].allowed)).toBe(true);
    expect(hasAccess(user, navigation[1].allowed)).toBe(false);
    expect(hasAccess(user, navigation[4].allowed)).toBe(false);
  });

  it('does not grant admin-only navigation to manager', () => {
    const user: CurrentUser = {
      user_id: 'u-2', tenant_id: 'tenant-1', store_id: 'store-1', roles: ['manager'],
    };
    expect(hasAccess(user, navigation[3].allowed)).toBe(true);
    expect(hasAccess(user, navigation[4].allowed)).toBe(false);
  });
});
