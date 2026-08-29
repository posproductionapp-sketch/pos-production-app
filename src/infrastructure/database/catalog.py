"""Store-scoped catalog persistence."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import InventoryBalanceModel, PriceModel, ProductModel, ProductVariantModel


class CatalogRepository:
    def __init__(self, session: Session, *, store_id: str) -> None:
        self.session = session
        self.store_id = store_id

    def create_variant(self, *, product_name: str, sku: str, description: str, price: Decimal, currency: str) -> ProductVariantModel:
        if price < 0:
            raise ValueError("Price cannot be negative")
        product = ProductModel(id=str(uuid4()), store_id=self.store_id, name=product_name)
        variant = ProductVariantModel(id=str(uuid4()), store_id=self.store_id, product_id=product.id, sku=sku, description=description)
        price_row = PriceModel(id=str(uuid4()), store_id=self.store_id, variant_id=variant.id, amount=price, currency=currency.upper())
        self.session.add_all([product, variant, price_row])
        self.session.flush()
        return variant

    def get_variant_price(self, variant_id: str) -> tuple[ProductVariantModel, PriceModel]:
        row = self.session.execute(
            select(ProductVariantModel, PriceModel)
            .join(PriceModel, PriceModel.variant_id == ProductVariantModel.id)
            .where(ProductVariantModel.id == variant_id, ProductVariantModel.store_id == self.store_id, PriceModel.store_id == self.store_id)
        ).one_or_none()
        if row is None:
            raise KeyError(variant_id)
        return row

    def list_variants(self) -> list[dict[str, object]]:
        rows = self.session.execute(
            select(ProductVariantModel, ProductModel, PriceModel, InventoryBalanceModel.quantity)
            .join(ProductModel, ProductModel.id == ProductVariantModel.product_id)
            .join(PriceModel, PriceModel.variant_id == ProductVariantModel.id)
            .outerjoin(
                InventoryBalanceModel,
                (InventoryBalanceModel.variant_id == ProductVariantModel.id)
                & (InventoryBalanceModel.store_id == self.store_id),
            )
            .where(
                ProductVariantModel.store_id == self.store_id,
                ProductModel.store_id == self.store_id,
                PriceModel.store_id == self.store_id,
            )
            .order_by(ProductModel.name, ProductVariantModel.sku)
        )
        return [
            {
                "variant_id": variant.id,
                "sku": variant.sku,
                "name": product.name,
                "description": variant.description,
                "price": str(price.amount),
                "currency": price.currency,
                "stock": str(stock or Decimal("0")),
            }
            for variant, product, price, stock in rows
        ]
