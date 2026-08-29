import { describe, expect, it } from 'vitest';
import { buildSalePayload, canAddToCart, cartSubtotal } from './pos_logic';

describe('POS checkout behavior', () => {
  it('prevents adding beyond backend-reported stock', () => {
    expect(canAddToCart(2, 0)).toBe(true);
    expect(canAddToCart(2, 1)).toBe(true);
    expect(canAddToCart(2, 2)).toBe(false);
  });

  it('calculates a cart display subtotal from current catalog prices', () => {
    expect(cartSubtotal([{ price: '10.00', quantity: 2 }, { price: '25.50', quantity: 1 }])).toBe(45.5);
  });

  it('creates a non-empty idempotency key and real sale payload', () => {
    const original = crypto.randomUUID;
    let count = 0;
    crypto.randomUUID = () => `uuid-${++count}`;
    try {
      const result = buildSalePayload([{ variant_id: 'v1', quantity: 2 }], 'cash');
      expect(result.idempotencyKey).toBe('uuid-2');
      expect(result.payload).toEqual({ items: [{ variant_id: 'v1', quantity: 2 }], payment_method: 'cash', payment_reference: 'POS-uuid-1' });
    } finally {
      crypto.randomUUID = original;
    }
  });
});
