export type SaleLine = { variant_id: string; quantity: number };

export function canAddToCart(stock: number, quantity: number): boolean {
  return Number.isFinite(stock) && stock >= 0 && quantity >= 0 && quantity < stock;
}

export function cartSubtotal(items: Array<{ price: string; quantity: number }>): number {
  return items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0);
}

export function buildSalePayload(items: SaleLine[], paymentMethod: string) {
  if (!items.length) throw new Error('Cart cannot be empty');
  if (!paymentMethod) throw new Error('Payment method is required');
  return {
    payload: { items, payment_method: paymentMethod, payment_reference: `POS-${crypto.randomUUID()}` },
    idempotencyKey: crypto.randomUUID(),
  };
}
