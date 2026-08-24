"""SQLAlchemy adapter for the domain order repository contract.

The adapter deliberately does not commit. Application/use-case transaction
boundaries own commit/rollback so order state changes remain atomic with any
other work performed by the use case.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.contracts import Money
from src.domain.order import Order, OrderState
from src.domain.order_repository import OrderRepository
from src.infrastructure.database.models import OrderModel


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session, *, store_id: str) -> None:
        if not store_id:
            raise ValueError("store_id is required")
        self._session = session
        self._store_id = store_id

    def save(self, order: Order) -> None:
        model = self._session.get(OrderModel, order.order_id)
        if model is None:
            model = OrderModel(
                id=order.order_id,
                store_id=self._store_id,
                state=order.state.value,
                total_amount=order.total.amount,
                currency=order.total.currency,
            )
            self._session.add(model)
        else:
            if model.store_id != self._store_id:
                raise ValueError("Order belongs to a different store")
            model.state = order.state.value
            model.total_amount = order.total.amount
            model.currency = order.total.currency
        self._session.flush()

    def get(self, order_id: str) -> Order | None:
        model = self._session.scalar(
            select(OrderModel).where(
                OrderModel.id == order_id,
                OrderModel.store_id == self._store_id,
            )
        )
        if model is None:
            return None
        try:
            state = OrderState(model.state)
        except ValueError as exc:
            raise ValueError(f"Unknown persisted order state: {model.state}") from exc
        return Order(
            order_id=model.id,
            total=Money(model.total_amount, model.currency),
            state=state,
        )
