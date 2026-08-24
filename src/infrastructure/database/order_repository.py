"""Persistence operations for orders and their line items."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import OrderItemModel, OrderModel


class OrderRepository:
    """Small transaction-neutral repository for order persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_order(
        self,
        *,
        order_id: str,
        store_id: str,
        state: str,
        total_amount: Decimal,
        currency: str,
        items: list[dict[str, Any]],
    ) -> OrderModel:
        order = OrderModel(
            id=order_id,
            store_id=store_id,
            state=state,
            total_amount=total_amount,
            currency=currency,
        )
        self._session.add(order)
        self._session.flush()
        for item in items:
            self._session.add(
                OrderItemModel(
                    id=item["id"],
                    order_id=order_id,
                    sku=item["sku"],
                    description=item["description"],
                    quantity=item["quantity"],
                    unit_amount=item["unit_amount"],
                    tax_amount=item["tax_amount"],
                    discount_amount=item["discount_amount"],
                    currency=item["currency"],
                )
            )
        return order

    def get_order(self, order_id: str) -> OrderModel | None:
        return self._session.scalar(select(OrderModel).where(OrderModel.id == order_id))

    def list_items(self, order_id: str) -> list[OrderItemModel]:
        statement = select(OrderItemModel).where(OrderItemModel.order_id == order_id).order_by(OrderItemModel.id)
        return list(self._session.scalars(statement))
