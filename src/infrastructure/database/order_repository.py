"""SQLAlchemy implementation of the domain OrderRepository port."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.contracts import Money
from src.domain.order import Order, OrderState
from src.domain.order_repository import OrderRepository
from src.infrastructure.database.models import Order as OrderModel


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, order: Order) -> None:
        model = self._session.get(OrderModel, order.order_id)
        if model is None:
            model = OrderModel(
                id=order.order_id,
                store_id="default",
                state=order.state.value,
                total_amount=order.total.amount,
                currency=order.total.currency,
            )
            self._session.add(model)
            return
        model.state = order.state.value
        model.total_amount = order.total.amount
        model.currency = order.total.currency

    def get(self, order_id: str) -> Order | None:
        model = self._session.scalar(select(OrderModel).where(OrderModel.id == order_id))
        if model is None:
            return None
        return Order(
            order_id=model.id,
            total=Money(Decimal(model.total_amount), model.currency),
            state=OrderState(model.state),
        )
