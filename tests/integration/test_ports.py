from decimal import Decimal

from src.app.ports import InventoryPort, PaymentGatewayPort
from src.domain.payment_stock import Payment, StockReservation
from src.domain.contracts import Money


class FakeInventory:
    def __init__(self) -> None:
        self.reservations = []

    def reserve(self, reservation: StockReservation) -> bool:
        self.reservations.append(reservation)
        return True

    def release(self, reservation: StockReservation) -> bool:
        self.reservations.remove(reservation)
        return True


class FakeGateway:
    def authorize(self, payment: Payment) -> bool:
        return payment.amount.amount > 0


def test_ports_accept_contract_compatible_adapters() -> None:
    inventory: InventoryPort = FakeInventory()
    gateway: PaymentGatewayPort = FakeGateway()
    reservation = StockReservation("coffee", Decimal("2"))
    payment = Payment("pay-1", Money(Decimal("100")), "cash")

    assert inventory.reserve(reservation)
    assert gateway.authorize(payment)
    assert inventory.release(reservation)
