"""SQLAlchemy 2.x persistence models for the approved POS schema."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def id_column() -> Mapped[str]:
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))


class Store(Base):
    __tablename__ = "stores"
    id: Mapped[str] = id_column()
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = id_column()
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (UniqueConstraint("store_id", "sku", name="uq_variant_store_sku"),)
    id: Mapped[str] = id_column()
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    sku: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(300), default="")


class Price(Base):
    __tablename__ = "prices"
    id: Mapped[str] = id_column()
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_store_created", "store_id", "created_at"),)
    id: Mapped[str] = id_column()
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    state: Mapped[str] = mapped_column(String(32), index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[str] = id_column()
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    sku: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(300))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    unit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))


class InventoryBalance(Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (UniqueConstraint("store_id", "variant_id", name="uq_inventory_store_variant"),)
    id: Mapped[str] = id_column()
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (Index("ix_inventory_movements_store_created", "store_id", "created_at"),)
    id: Mapped[str] = id_column()
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    reason: Mapped[str] = mapped_column(String(64))
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("provider", "provider_reference", name="uq_payment_provider_reference"),)
    id: Mapped[str] = id_column()
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    provider: Mapped[str] = mapped_column(String(50))
    provider_reference: Mapped[str] = mapped_column(String(200))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))
    state: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Refund(Base):
    __tablename__ = "refunds"
    id: Mapped[str] = id_column()
    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))
    state: Mapped[str] = mapped_column(String(32))
    provider_reference: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_store_created", "store_id", "created_at"),)
    id: Mapped[str] = id_column()
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)
    store_id: Mapped[str] = mapped_column(String(36), index=True)
    actor_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(100))
    resource_id: Mapped[str] = mapped_column(String(100))
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = (UniqueConstraint("tenant_id", "store_id", "operation", "key", name="uq_idempotency_scope"),)
    id: Mapped[str] = id_column()
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)
    store_id: Mapped[str] = mapped_column(String(36), index=True)
    operation: Mapped[str] = mapped_column(String(100))
    key: Mapped[str] = mapped_column(String(200))
    result_reference: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
