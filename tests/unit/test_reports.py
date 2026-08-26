from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.infrastructure.database.models import (
    Base,
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
from src.infrastructure.database.reports import ReportRepository
from src.infrastructure.database.shift_models import CashMovementModel, ShiftModel


def test_reports_are_store_scoped_and_financially_exact():
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    start = datetime(2026, 8, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 1, tzinfo=timezone.utc)

    with Session(engine) as session:
        session.add_all([
            StoreModel(id="store-1", tenant_id="tenant-1", name="One", created_at=start),
            StoreModel(id="store-2", tenant_id="tenant-1", name="Two", created_at=start),
        ])
        session.flush()
        session.add_all([
            ProductModel(id="product-1", store_id="store-1", name="Coffee", created_at=start),
            ProductModel(id="product-2", store_id="store-2", name="Coffee", created_at=start),
        ])
        session.flush()
        session.add_all([
            ProductVariantModel(id="variant-1", store_id="store-1", product_id="product-1", sku="COFFEE-1", description="Coffee"),
            ProductVariantModel(id="variant-2", store_id="store-2", product_id="product-2", sku="COFFEE-1", description="Coffee"),
        ])
        session.add_all([
            PriceModel(id="price-1", store_id="store-1", variant_id="variant-1", amount=Decimal("50.00"), currency="THB"),
            PriceModel(id="price-2", store_id="store-2", variant_id="variant-2", amount=Decimal("80.00"), currency="THB"),
            InventoryBalanceModel(id="balance-1", store_id="store-1", variant_id="variant-1", quantity=Decimal("4"), updated_at=start),
            InventoryMovementModel(id="movement-1", store_id="store-1", variant_id="variant-1", quantity_delta=Decimal("5"), reason="stock_receipt", correlation_id="receipt-1", created_at=start),
            InventoryMovementModel(id="movement-2", store_id="store-1", variant_id="variant-1", quantity_delta=Decimal("-1"), reason="sale", correlation_id="order-1", created_at=start),
        ])
        session.add_all([
            OrderModel(id="order-1", store_id="store-1", state="paid", total_amount=Decimal("100.00"), currency="THB", created_at=start, updated_at=start),
            OrderItemModel(id="item-1", order_id="order-1", sku="COFFEE-1", description="Coffee", quantity=Decimal("2"), unit_amount=Decimal("50.00"), tax_amount=Decimal("0"), discount_amount=Decimal("0"), currency="THB"),
            PaymentModel(id="payment-1", order_id="order-1", provider="cash", provider_reference="cash-1", amount=Decimal("100.00"), currency="THB", state="captured", created_at=start),
            RefundModel(id="refund-1", payment_id="payment-1", amount=Decimal("50.00"), currency="THB", state="captured", provider_reference="refund-1", created_at=start),
        ])
        session.add(ShiftModel(id="shift-1", tenant_id="tenant-1", store_id="store-1", opened_by="user", opened_at=start, opening_cash=Decimal("100.00"), closing_cash=Decimal("150.00"), state="closed", closed_by="user", closed_at=start))
        session.add_all([
            CashMovementModel(id="cash-1", shift_id="shift-1", type="sale", amount=Decimal("100.00"), reason="sale", actor_id="user", correlation_id="order-1", created_at=start),
            CashMovementModel(id="cash-2", shift_id="shift-1", type="refund", amount=Decimal("50.00"), reason="refund", actor_id="user", correlation_id="refund-1", created_at=start),
        ])
        session.commit()

        sales = ReportRepository(session, store_id="store-1").sales(start=start, end=end)
        assert sales["order_count"] == 1
        assert sales["gross_sales"] == "100.00"
        assert sales["refunds"] == "50.00"
        assert sales["net_sales"] == "50.00"
        assert sales["payments_by_provider"] == {"cash": "100.00"}

        inventory = ReportRepository(session, store_id="store-1").inventory(start=start, end=end)
        assert inventory["balances"] == [{"sku": "COFFEE-1", "description": "Coffee", "quantity": "4.000"}]
        assert len(inventory["movements"]) == 2

        shifts = ReportRepository(session, store_id="store-1").shifts(start=start, end=end)
        assert shifts[0]["expected_cash"] == "150.00"
        assert shifts[0]["variance"] == "0.00"

        other_store = ReportRepository(session, store_id="store-2").sales(start=start, end=end)
        assert other_store["order_count"] == 0
        assert other_store["gross_sales"] == "0.00"
