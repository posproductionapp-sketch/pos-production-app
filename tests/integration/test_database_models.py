"""Contract tests for the persistence mapping against the approved schema."""

from sqlalchemy import inspect

from src.infrastructure.database.models import (
    AuditLogModel,
    Base,
    IdempotencyKeyModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    OrderItemModel,
    OrderModel,
    PaymentModel,
    PriceModel,
    ProductModel,
    ProductVariantModel,
    RefundModel,
    StoreModel,
)


def test_all_approved_tables_are_mapped() -> None:
    expected = {
        "stores", "products", "product_variants", "prices", "orders",
        "order_items", "inventory_balances", "inventory_movements", "payments",
        "refunds", "audit_logs", "idempotency_keys",
    }
    assert set(Base.metadata.tables) == expected


def test_order_mapping_matches_money_precision() -> None:
    table = OrderModel.__table__
    assert str(table.c.total_amount.type) == "NUMERIC(18, 2)"
    assert table.c.currency.type.length == 3
    assert table.c.state.type.length == 32


def test_inventory_and_idempotency_constraints_are_present() -> None:
    inventory = inspect(InventoryBalanceModel).local_table
    idem = inspect(IdempotencyKeyModel).local_table
    assert any(c.name == "uq_inventory_store_variant" for c in inventory.constraints)
    assert any(c.name == "uq_idempotency_scope" for c in idem.constraints)
