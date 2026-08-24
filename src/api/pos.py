"""Store-scoped POS business API: catalog, sales, inventory, payments and shifts."""

from decimal import Decimal
from uuid import NAMESPACE_URL, uuid4, uuid5

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.uow import UnitOfWork
from src.domain.auth import Role
from src.infrastructure.database.catalog import CatalogRepository
from src.infrastructure.database.idempotency import SqlAlchemyIdempotencyRepository
from src.infrastructure.database.inventory import InventoryInsufficientStock, SqlAlchemyInventoryRepository
from src.infrastructure.database.models import OrderItemModel, OrderModel, PaymentModel, ProductVariantModel
from src.infrastructure.database.payment import PaymentConflict, RefundExceedsPayment, SqlAlchemyPaymentRepository, SqlAlchemyRefundRepository
from src.infrastructure.database.shifts import ShiftRepository


class VariantCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=300)
    price: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)


class StockRequest(BaseModel):
    variant_id: str = Field(min_length=1, max_length=36)
    quantity: Decimal = Field(gt=0)
    correlation_id: str = Field(min_length=1, max_length=100)


class SaleItem(BaseModel):
    variant_id: str = Field(min_length=1, max_length=36)
    quantity: Decimal = Field(gt=0)


class SaleRequest(BaseModel):
    items: list[SaleItem] = Field(min_length=1, max_length=100)
    payment_method: str = Field(min_length=1, max_length=50)
    payment_reference: str = Field(min_length=1, max_length=200)


class RefundRequest(BaseModel):
    payment_id: str = Field(min_length=1, max_length=36)
    amount: Decimal = Field(gt=0)
    provider_reference: str = Field(min_length=1, max_length=200)
    restock: bool = True
    correlation_id: str = Field(min_length=1, max_length=100)


class ShiftOpenRequest(BaseModel):
    opening_cash: Decimal = Field(ge=0)


class CashMovementRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=1, max_length=200)
    correlation_id: str = Field(min_length=1, max_length=100)


class ShiftCloseRequest(BaseModel):
    closing_cash: Decimal = Field(ge=0)


def build_pos_router(principal_dependency, session_dependency) -> APIRouter:
    router = APIRouter(prefix="/v1")

    def require(current, *roles: Role) -> None:
        try:
            current.require(*roles)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail="Insufficient role") from exc

    @router.post("/catalog/variants")
    def create_variant(payload: VariantCreate, current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.INVENTORY)
        with UnitOfWork(session):
            variant = CatalogRepository(session, store_id=current.store_id).create_variant(product_name=payload.product_name, sku=payload.sku, description=payload.description, price=payload.price, currency=payload.currency)
            return {"variant_id": variant.id, "sku": variant.sku}

    @router.post("/inventory/receive")
    def receive_stock(payload: StockRequest, current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.INVENTORY)
        with UnitOfWork(session):
            quantity = SqlAlchemyInventoryRepository(session, store_id=current.store_id).adjust(variant_id=payload.variant_id, delta=payload.quantity, reason="stock_receipt", correlation_id=payload.correlation_id)
            return {"variant_id": payload.variant_id, "quantity": str(quantity)}

    @router.post("/sales")
    def sale(payload: SaleRequest, current=Depends(principal_dependency), idempotency_key: str = Header(default="", alias="Idempotency-Key"), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.CASHIER)
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Idempotency-Key is required")
        operation = "sale"
        order_id = str(uuid5(NAMESPACE_URL, f"{current.tenant_id}:{current.store_id}:{operation}:{idempotency_key}"))
        with UnitOfWork(session):
            idem = SqlAlchemyIdempotencyRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
            existing = idem.get(operation, idempotency_key)
            if existing:
                order = session.get(OrderModel, existing.result_reference)
                if order is None:
                    raise HTTPException(status_code=409, detail="Idempotency record is inconsistent")
                return {"order_id": order.id, "state": order.state, "total": str(order.total_amount), "currency": order.currency, "duplicate": True}
            catalog = CatalogRepository(session, store_id=current.store_id)
            inventory = SqlAlchemyInventoryRepository(session, store_id=current.store_id)
            total = Decimal("0")
            currency = None
            prepared = []
            for item in payload.items:
                variant, price = catalog.get_variant_price(item.variant_id)
                if currency is None:
                    currency = price.currency
                if price.currency != currency:
                    raise HTTPException(status_code=400, detail="All sale items must use the same currency")
                total += price.amount * item.quantity
                prepared.append((variant, price, item.quantity))
            for variant, _, quantity in prepared:
                try:
                    inventory.adjust(variant_id=variant.id, delta=-quantity, reason="sale", correlation_id=order_id)
                except InventoryInsufficientStock as exc:
                    raise HTTPException(status_code=409, detail="Insufficient inventory") from exc
            order = OrderModel(id=order_id, store_id=current.store_id, state="paid", total_amount=total, currency=currency)
            session.add(order)
            for variant, price, quantity in prepared:
                session.add(OrderItemModel(id=str(uuid4()), order_id=order_id, sku=variant.sku, description=variant.description, quantity=quantity, unit_amount=price.amount, tax_amount=Decimal("0"), discount_amount=Decimal("0"), currency=price.currency))
            try:
                payment = SqlAlchemyPaymentRepository(session).record(order_id=order_id, provider=payload.payment_method, provider_reference=payload.payment_reference, amount=total, currency=currency, state="captured")
            except (PaymentConflict, ValueError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if payload.payment_method.lower() == "cash":
                shift_repo = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
                shift = shift_repo.current()
                if shift is None:
                    raise HTTPException(status_code=409, detail="An open shift is required for cash sales")
                shift_repo.add_cash_movement(shift_id=shift.id, movement_type="sale", amount=total, reason="cash sale", actor_id=current.user_id, correlation_id=order_id)
            idem.reserve(operation, idempotency_key, order_id)
            return {"order_id": order_id, "payment_id": payment.id, "state": order.state, "total": str(total), "currency": currency, "duplicate": False}

    @router.post("/refunds")
    def refund(payload: RefundRequest, current=Depends(principal_dependency), idempotency_key: str = Header(default="", alias="Idempotency-Key"), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER)
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Idempotency-Key is required")
        operation = "refund"
        refund_id = str(uuid5(NAMESPACE_URL, f"{current.tenant_id}:{current.store_id}:{operation}:{idempotency_key}"))
        with UnitOfWork(session):
            idem = SqlAlchemyIdempotencyRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
            existing = idem.get(operation, idempotency_key)
            if existing:
                return {"refund_id": existing.result_reference, "duplicate": True}
            payment = session.get(PaymentModel, payload.payment_id)
            if payment is None:
                raise HTTPException(status_code=404, detail="Payment not found")
            order = session.get(OrderModel, payment.order_id)
            if order is None or order.store_id != current.store_id:
                raise HTTPException(status_code=404, detail="Payment not found")
            try:
                refund = SqlAlchemyRefundRepository(session).record(payment_id=payload.payment_id, amount=payload.amount, currency=payment.currency, state="captured", provider_reference=payload.provider_reference)
            except (RefundExceedsPayment, ValueError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if payload.restock:
                fraction = payload.amount / order.total_amount
                inventory = SqlAlchemyInventoryRepository(session, store_id=current.store_id)
                for item in session.scalars(select(OrderItemModel).where(OrderItemModel.order_id == order.id)):
                    variant = session.scalar(select(ProductVariantModel).where(ProductVariantModel.store_id == current.store_id, ProductVariantModel.sku == item.sku))
                    if variant is None:
                        raise HTTPException(status_code=409, detail=f"Variant for SKU {item.sku} not found")
                    inventory.adjust(variant_id=variant.id, delta=item.quantity * fraction, reason="refund_restock", correlation_id=payload.correlation_id)
            if payment.provider.lower() == "cash":
                shift_repo = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
                shift = shift_repo.current()
                if shift is None:
                    raise HTTPException(status_code=409, detail="An open shift is required for cash refunds")
                shift_repo.add_cash_movement(shift_id=shift.id, movement_type="refund", amount=payload.amount, reason="cash refund", actor_id=current.user_id, correlation_id=payload.correlation_id)
            idem.reserve(operation, idempotency_key, refund_id)
            return {"refund_id": refund_id, "payment_id": payment.id, "amount": str(refund.amount), "duplicate": False}

    @router.post("/shifts/open")
    def open_shift(payload: ShiftOpenRequest, current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.CASHIER)
        with UnitOfWork(session):
            shift = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id).open(actor_id=current.user_id, opening_cash=payload.opening_cash)
            return {"shift_id": shift.id, "state": shift.state, "opening_cash": str(shift.opening_cash)}

    def cash_movement(movement_type: str):
        def handler(payload: CashMovementRequest, current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
            require(current, Role.ADMIN, Role.MANAGER, Role.CASHIER)
            with UnitOfWork(session):
                repo = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
                shift = repo.current()
                if shift is None:
                    raise HTTPException(status_code=409, detail="No open shift")
                movement = repo.add_cash_movement(shift_id=shift.id, movement_type=movement_type, amount=payload.amount, reason=payload.reason, actor_id=current.user_id, correlation_id=payload.correlation_id)
                return {"movement_id": movement.id, "shift_id": shift.id}
        return handler

    router.add_api_route("/shifts/cash-in", cash_movement("cash_in"), methods=["POST"])
    router.add_api_route("/shifts/cash-out", cash_movement("cash_out"), methods=["POST"])

    @router.post("/shifts/close")
    def close_shift(payload: ShiftCloseRequest, current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER)
        with UnitOfWork(session):
            shift = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id).close(actor_id=current.user_id, closing_cash=payload.closing_cash)
            return {"shift_id": shift.id, "state": shift.state, "closing_cash": str(shift.closing_cash)}

    return router
