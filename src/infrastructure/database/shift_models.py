"""ORM mappings for cash shifts."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models import Base


class ShiftModel(Base):
    __tablename__ = "shifts"
    __table_args__ = (
        UniqueConstraint("store_id", "state", name="uq_shift_store_state"),
        Index("ix_shifts_store_opened", "store_id", "opened_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    opened_by: Mapped[str] = mapped_column(String(36), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    opening_cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    closing_cash: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    closed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CashMovementModel(Base):
    __tablename__ = "cash_movements"
    __table_args__ = (Index("ix_cash_movements_shift_created", "shift_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    shift_id: Mapped[str] = mapped_column(ForeignKey("shifts.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
