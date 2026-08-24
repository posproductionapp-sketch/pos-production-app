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
    SyncCommandModel,
    UserModel,
)
from src.infrastructure.database import shift_models  # noqa: F401 - register shift mappings


def test_all_approved_tables_are_mapped() -> None:
    expected = {
        "stores", "products", "product_variants", "prices", "orders",
        "order_items", "inventory_balances", "inventory_movements", "payments",
        "refunds", "audit_logs", "idempotency_keys", "users", "sync_commands",
        "shifts", "cash_movements",
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


def test_auth_sync_and_shift_constraints_are_present() -> None:
    assert any(c.name == "uq_user_tenant_username" for c in inspect(UserModel).local_table.constraints)
    assert any(c.name == "uq_sync_command_scope" for c in inspect(SyncCommandModel).local_table.constraints)
    assert any(c.name == "uq_shift_store_state" for c in inspect(shift_models.ShiftModel).local_table.constraints)
