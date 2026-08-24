"""Initial approved POS production schema.

Revision ID: 0001_initial_pos_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_pos_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("stores", sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_stores_tenant_id", "stores", ["tenant_id"])

    op.create_table("products", sa.Column("id", sa.String(36), primary_key=True), sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_products_store_id", "products", ["store_id"])

    op.create_table("product_variants", sa.Column("id", sa.String(36), primary_key=True), sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False), sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False), sa.Column("sku", sa.String(100), nullable=False), sa.Column("description", sa.String(300), nullable=False, server_default=""), sa.UniqueConstraint("store_id", "sku", name="uq_variant_store_sku"))
    op.create_index("ix_product_variants_store_id", "product_variants", ["store_id"])
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])

    op.create_table("prices", sa.Column("id", sa.String(36), primary_key=True), sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False), sa.Column("variant_id", sa.String(36), sa.ForeignKey("product_variants.id"), nullable=False), sa.Column("amount", sa.Numeric(18, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False))
    op.create_index("ix_prices_store_id", "prices", ["store_id"])
    op.create_index("ix_prices_variant_id", "prices", ["variant_id"])

    op.create_table("orders", sa.Column("id", sa.String(36), primary_key=True), sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False), sa.Column("state", sa.String(32), nullable=False), sa.Column("total_amount", sa.Numeric(18, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_orders_store_id", "orders", ["store_id"])
    op.create_index("ix_orders_state", "orders", ["state"])
    op.create_index("ix_orders_store_created", "orders", ["store_id", "created_at"])

    op.create_table("order_items", sa.Column("id", sa.String(36), primary_key=True), sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id"), nullable=False), sa.Column("sku", sa.String(100), nullable=False), sa.Column("description", sa.String(300), nullable=False), sa.Column("quantity", sa.Numeric(18, 3), nullable=False), sa.Column("unit_amount", sa.Numeric(18, 2), nullable=False), sa.Column("tax_amount", sa.Numeric(18, 2), nullable=False), sa.Column("discount_amount", sa.Numeric(18, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False))
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    op.create_table("inventory_balances", sa.Column("id", sa.String(36), primary_key=True), sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False), sa.Column("variant_id", sa.String(36), sa.ForeignKey("product_variants.id"), nullable=False), sa.Column("quantity", sa.Numeric(18, 3), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("store_id", "variant_id", name="uq_inventory_store_variant"))
    op.create_index("ix_inventory_balances_store_id", "inventory_balances", ["store_id"])
    op.create_index("ix_inventory_balances_variant_id", "inventory_balances", ["variant_id"])

    op.create_table("inventory_movements", sa.Column("id", sa.String(36), primary_key=True), sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False), sa.Column("variant_id", sa.String(36), sa.ForeignKey("product_variants.id"), nullable=False), sa.Column("quantity_delta", sa.Numeric(18, 3), nullable=False), sa.Column("reason", sa.String(64), nullable=False), sa.Column("correlation_id", sa.String(100), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_inventory_movements_store_created", "inventory_movements", ["store_id", "created_at"])

    op.create_table("payments", sa.Column("id", sa.String(36), primary_key=True), sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id"), nullable=False), sa.Column("provider", sa.String(50), nullable=False), sa.Column("provider_reference", sa.String(200), nullable=False), sa.Column("amount", sa.Numeric(18, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("state", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("provider", "provider_reference", name="uq_payment_provider_reference"))
    op.create_index("ix_payments_order_id", "payments", ["order_id"])

    op.create_table("refunds", sa.Column("id", sa.String(36), primary_key=True), sa.Column("payment_id", sa.String(36), sa.ForeignKey("payments.id"), nullable=False), sa.Column("amount", sa.Numeric(18, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("state", sa.String(32), nullable=False), sa.Column("provider_reference", sa.String(200), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_refunds_payment_id", "refunds", ["payment_id"])

    op.create_table("audit_logs", sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), nullable=False), sa.Column("store_id", sa.String(36), nullable=False), sa.Column("actor_id", sa.String(36), nullable=False), sa.Column("action", sa.String(100), nullable=False), sa.Column("resource_type", sa.String(100), nullable=False), sa.Column("resource_id", sa.String(100), nullable=False), sa.Column("correlation_id", sa.String(100), nullable=False), sa.Column("metadata_json", sa.Text, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_audit_store_created", "audit_logs", ["store_id", "created_at"])

    op.create_table("idempotency_keys", sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), nullable=False), sa.Column("store_id", sa.String(36), nullable=False), sa.Column("operation", sa.String(100), nullable=False), sa.Column("key", sa.String(200), nullable=False), sa.Column("result_reference", sa.String(200), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", "store_id", "operation", "key", name="uq_idempotency_scope"))
    op.create_index("ix_idempotency_keys_tenant_id", "idempotency_keys", ["tenant_id"])
    op.create_index("ix_idempotency_keys_store_id", "idempotency_keys", ["store_id"])


def downgrade() -> None:
    for table in ["idempotency_keys", "audit_logs", "refunds", "payments", "inventory_movements", "inventory_balances", "order_items", "orders", "prices", "product_variants", "products", "stores"]:
        op.drop_table(table)
