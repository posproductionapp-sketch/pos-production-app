"""Store-scoped reporting queries.

Reports are read-only projections over authoritative transaction records. They
never mutate operational state and always require an explicit store boundary.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import (
    InventoryBalanceModel,
    InventoryMovementModel,
    OrderItemModel,
    OrderModel,
    PaymentModel,
    ProductVariantModel,
    RefundModel,
)
from src.infrastructure.database.shift_models import CashMovementModel, ShiftModel


class ReportRepository:
    def __init__(self, session: Session, *, store_id: str) -> None:
        self.session = session
        self.store_id = store_id

    def sales(self, *, start: datetime, end: datetime) -> dict[str, object]:
        order_filters = (
            OrderModel.store_id == self.store_id,
            OrderModel.created_at >= start,
            OrderModel.created_at < end,
            OrderModel.state == "paid",
        )
        gross = self.session.scalar(select(func.coalesce(func.sum(OrderModel.total_amount), 0)).where(*order_filters)) or Decimal("0")
        order_count = self.session.scalar(select(func.count(OrderModel.id)).where(*order_filters)) or 0
        item_count = self.session.scalar(
            select(func.coalesce(func.sum(OrderItemModel.quantity), 0))
            .join(OrderModel, OrderModel.id == OrderItemModel.order_id)
            .where(*order_filters)
        ) or Decimal("0")

        refund_filters = (
            OrderModel.store_id == self.store_id,
            RefundModel.created_at >= start,
            RefundModel.created_at < end,
        )
        refunds = self.session.scalar(
            select(func.coalesce(func.sum(RefundModel.amount), 0))
            .join(PaymentModel, PaymentModel.id == RefundModel.payment_id)
            .join(OrderModel, OrderModel.id == PaymentModel.order_id)
            .where(*refund_filters)
        ) or Decimal("0")

        payment_rows = self.session.execute(
            select(PaymentModel.provider, func.coalesce(func.sum(PaymentModel.amount), 0))
            .join(OrderModel, OrderModel.id == PaymentModel.order_id)
            .where(
                OrderModel.store_id == self.store_id,
                PaymentModel.created_at >= start,
                PaymentModel.created_at < end,
                PaymentModel.state == "captured",
            )
            .group_by(PaymentModel.provider)
            .order_by(PaymentModel.provider)
        ).all()

        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "order_count": int(order_count),
            "item_quantity": str(item_count),
            "gross_sales": str(gross),
            "refunds": str(refunds),
            "net_sales": str(gross - refunds),
            "payments_by_provider": {provider: str(amount) for provider, amount in payment_rows},
        }

    def inventory(self, *, start: datetime, end: datetime) -> dict[str, object]:
        balances = self.session.execute(
            select(ProductVariantModel.sku, ProductVariantModel.description, InventoryBalanceModel.quantity)
            .join(InventoryBalanceModel, InventoryBalanceModel.variant_id == ProductVariantModel.id)
            .where(
                ProductVariantModel.store_id == self.store_id,
                InventoryBalanceModel.store_id == self.store_id,
            )
            .order_by(ProductVariantModel.sku)
        ).all()

        movements = self.session.execute(
            select(
                ProductVariantModel.sku,
                InventoryMovementModel.reason,
                func.coalesce(func.sum(InventoryMovementModel.quantity_delta), 0),
            )
            .join(ProductVariantModel, ProductVariantModel.id == InventoryMovementModel.variant_id)
            .where(
                InventoryMovementModel.store_id == self.store_id,
                InventoryMovementModel.created_at >= start,
                InventoryMovementModel.created_at < end,
            )
            .group_by(ProductVariantModel.sku, InventoryMovementModel.reason)
            .order_by(ProductVariantModel.sku, InventoryMovementModel.reason)
        ).all()

        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "balances": [
                {"sku": sku, "description": description, "quantity": str(quantity)}
                for sku, description, quantity in balances
            ],
            "movements": [
                {"sku": sku, "reason": reason, "quantity_delta": str(quantity)}
                for sku, reason, quantity in movements
            ],
        }

    def shifts(self, *, start: datetime, end: datetime) -> list[dict[str, object]]:
        shifts = self.session.scalars(
            select(ShiftModel)
            .where(
                ShiftModel.store_id == self.store_id,
                ShiftModel.opened_at >= start,
                ShiftModel.opened_at < end,
            )
            .order_by(ShiftModel.opened_at)
        ).all()

        results: list[dict[str, object]] = []
        for shift in shifts:
            movements = self.session.execute(
                select(CashMovementModel.type, func.coalesce(func.sum(CashMovementModel.amount), 0))
                .where(CashMovementModel.shift_id == shift.id)
                .group_by(CashMovementModel.type)
            ).all()
            totals = {movement_type: amount for movement_type, amount in movements}
            expected = shift.opening_cash + totals.get("cash_in", Decimal("0")) + totals.get("sale", Decimal("0")) - totals.get("cash_out", Decimal("0")) - totals.get("refund", Decimal("0"))
            results.append(
                {
                    "shift_id": shift.id,
                    "state": shift.state,
                    "opened_at": shift.opened_at.isoformat(),
                    "closed_at": shift.closed_at.isoformat() if shift.closed_at else None,
                    "opening_cash": str(shift.opening_cash),
                    "closing_cash": str(shift.closing_cash) if shift.closing_cash is not None else None,
                    "expected_cash": str(expected),
                    "variance": str(shift.closing_cash - expected) if shift.closing_cash is not None else None,
                    "movements": {key: str(value) for key, value in totals.items()},
                }
            )
        return results
