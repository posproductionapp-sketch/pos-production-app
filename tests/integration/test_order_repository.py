from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.infrastructure.database.models import Base
from src.infrastructure.database.order_repository import OrderRepository


def test_order_repository_round_trip() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = OrderRepository(session)
        repository.add_order(
            order_id="order-1",
            store_id="store-1",
            state="pending",
            total_amount=Decimal("123.45"),
            currency="THB",
            items=[
                {
                    "id": "item-1",
                    "sku": "SKU-1",
                    "description": "Coffee",
                    "quantity": Decimal("2"),
                    "unit_amount": Decimal("50.00"),
                    "tax_amount": Decimal("6.55"),
                    "discount_amount": Decimal("0.00"),
                    "currency": "THB",
                }
            ],
        )
        session.commit()

    with Session(engine) as session:
        repository = OrderRepository(session)
        order = repository.get_order("order-1")
        items = repository.list_items("order-1")

        assert order is not None
        assert order.total_amount == Decimal("123.45")
        assert order.currency == "THB"
        assert len(items) == 1
        assert items[0].sku == "SKU-1"
