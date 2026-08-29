"""Store-scoped POS business API: catalog, sales, inventory, payments and shifts."""

from decimal import Decimal, ROUND_HALF_UP
from uuid import NAMESPACE_URL, uuid4, uuid5

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.contracts import CheckoutRequest
from src.app.uow import UnitOfWork
from src.config.settings import load_settings
from src.domain.auth import Role
from src.domain.contracts import Cart, LineItem, Money
from src.infrastructure.database.catalog import CatalogRepository
from src.infrastructure.database.idempotency import IdempotencyConflict, SqlAlchemyIdempotencyRepository
from src.infrastructure.database.inventory import InventoryInsufficientStock, SqlAlchemyInventoryRepository
from src.infrastructure.database.models import OrderItemModel, OrderModel, PaymentModel, ProductVariantModel
from src.infrastructure.database.payment import PaymentConflict, RefundExceedsPayment, SqlAlchemyPaymentRepository, SqlAlchemyRefundRepository
from src.infrastructure.database.shifts import ShiftRepository
from src.services.checkout import CheckoutService
from src.services.deterministic_pricing import PercentageDiscountPolicy, SubtotalPricingPolicy, VatRatePolicy

_CENT = Decimal("0.01")


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
    discount_rate: Decimal = Field(default=Decimal("0"), ge=0, le=1)


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


def _checkout_service(discount_rate: Decimal) -> CheckoutService:
    return CheckoutService(SubtotalPricingPolicy(), PercentageDiscountPolicy(discount_rate), VatRatePolicy(load_settings().vat_rate))


def _allocate(total: Decimal, bases: list[Decimal]) -> list[Decimal]:
    if not bases:
        return []
    base_total = sum(bases, Decimal("0"))
    if total == 0 or base_total == 0:
        return [Decimal("0")] * len(bases)
    allocations: list[Decimal] = []
    running = Decimal("0")
    for index, base in enumerate(bases):
        if index == len(bases) - 1:
            value = total - running
        else:
            value = (total * base / base_total).quantize(_CENT, rounding=ROUND_HALF_UP)
            running += value
        allocations.append(value)
    return allocations


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

    @router.get("/catalog/variants")
    def list_variants(current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.CASHIER, Role.INVENTORY)
        return {"items": CatalogRepository(session, store_id=current.store_id).list_variants()}

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
        if payload.discount_rate > 0:
            require(current, Role.ADMIN, Role.MANAGER)
        operation = "sale"
        order_id = str(uuid5(NAMESPACE_URL, f"{current.tenant_id}:{current.store_id}:{operation}:{idempotency_key}"))
        with UnitOfWork(session):
            idem = SqlAlchemyIdempotencyRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
            try:
                reserved, created = idem.reserve_new(operation, idempotency_key, order_id)
            except IdempotencyConflict as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if not created:
                return {"order_id": reserved.result_reference, "duplicate": True}

            catalog = CatalogRepository(session, store_id=current.store_id)
            inventory = SqlAlchemyInventoryRepository(session, store_id=current.store_id)
            line_items: list[LineItem] = []
            prepared = []
            currency: str | None = None
            for item in payload.items:
                try:
                    variant, price = catalog.get_variant_price(item.variant_id)
                except KeyError as exc:
                    raise HTTPException(status_code=404, detail="Product variant not found") from exc
                available = inventory.quantity(variant_id=variant.id)
                if item.quantity > available:
                    raise HTTPException(status_code=409, detail="Insufficient inventory")
                if currency is None:
                    currency = price.currency
                if price.currency != currency:
                    raise HTTPException(status_code=400, detail="All sale items must use the same currency")
                line_items.append(LineItem(variant.id, item.quantity, Money(price.amount, price.currency)))
                prepared.append((variant, price, item.quantity))

            cart = Cart(tuple(line_items))
            try:
                quote = _checkout_service(payload.discount_rate).quote(CheckoutRequest(cart))
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            line_subtotals = [(price.amount * quantity).quantize(_CENT, rounding=ROUND_HALF_UP) for _, price, quantity in prepared]
            line_discounts = _allocate(quote.discount.amount, line_subtotals)
            taxable_lines = [subtotal - discount for subtotal, discount in zip(line_subtotals, line_discounts)]
            line_taxes = _allocate(quote.vat.amount, taxable_lines)

            for variant, _, quantity in prepared:
                try:
                    inventory.adjust(variant_id=variant.id, delta=-quantity, reason="sale", correlation_id=order_id)
                except InventoryInsufficientStock as exc:
                    raise HTTPException(status_code=409, detail="Insufficient inventory") from exc

            order = OrderModel(id=order_id, store_id=current.store_id, state="paid", total_amount=quote.total.amount, currency=currency)
            session.add(order)
            for index, (variant, price, quantity) in enumerate(prepared):
                session.add(OrderItemModel(id=str(uuid4()), order_id=order_id, sku=variant.sku, description=variant.description, quantity=quantity, unit_amount=price.amount, tax_amount=line_taxes[index], discount_amount=line_discounts[index], currency=price.currency))
            try:
                payment = SqlAlchemyPaymentRepository(session).record(order_id=order_id, provider=payload.payment_method, provider_reference=payload.payment_reference, amount=quote.total.amount, currency=currency, state="captured")
            except (PaymentConflict, ValueError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if payload.payment_method.lower() == "cash":
                shift_repo = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
                shift = shift_repo.current()
                if shift is None:
                    raise HTTPException(status_code=409, detail="An open shift is required for cash sales")
                shift_repo.add_cash_movement(shift_id=shift.id, movement_type="sale", amount=quote.total.amount, reason="cash sale", actor_id=current.user_id, correlation_id=order_id)
            return {"order_id": order_id, "payment_id": payment.id, "state": order.state, "subtotal": str(quote.subtotal.amount), "discount": str(quote.discount.amount), "tax": str(quote.vat.amount), "total": str(quote.total.amount), "currency": currency, "duplicate": False}

    @router.get("/shifts/current")
    def current_shift(current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.CASHIER)
        shift = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id).current()
        if shift is None:
            return None
        return {"shift_id": shift.id, "state": shift.state, "opening_cash": str(shift.opening_cash)}

    @router.post("/refunds")
    def refund(payload: RefundRequest, current=Depends(principal_dependency), idempotency_key: str = Header(default="", alias="Idempotency-Key"), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER)
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Idempotency-Key is required")
        operation = "refund"
        refund_id = str(uuid5(NAMESPACE_URL, f"{current.tenant_id}:{current.store_id}:{operation}:{idempotency_key}"))
        with UnitOfWork(session):
            idem = SqlAlchemyIdempotencyRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
            try:
                reserved, created = idem.reserve_new(operation, idempotency_key, refund_id)
            except IdempotencyConflict as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if not created:
                return {"refund_id": reserved.result_reference, "duplicate": True}

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
            return {"refund_id": refund_id, "payment_id": payment.id, "amount": str(refund.amount), "duplicate": False}

    @router.post("/shifts/open")
    def open_shift(payload: ShiftOpenRequest, current=Depends(principal_dependency), session: Session = Depends(session_dependency)):
        require(current, Role.ADMIN, Role.MANAGER, Role.CASHIER)
        with UnitOfWork(session):
            try:
                shift = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id).open(actor_id=current.user_id, opening_cash=payload.opening_cash)
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
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
            try:
                shift = ShiftRepository(session, tenant_id=current.tenant_id, store_id=current.store_id).close(actor_id=current.user_id, closing_cash=payload.closing_cash)
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            return {"shift_id": shift.id, "state": shift.state, "closing_cash": str(shift.closing_cash)}

    return router
