import pytest
from decimal import Decimal
from typing import List, Optional
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide

class MockBroker(Broker):
    """Mock implementation to verify Protocol adherence."""
    def __init__(self, balance: Decimal):
        self._balance = balance
        self.orders: List[OrderRequest] = []
        self.positions: List[Position] = []

    def get_balance(self) -> Decimal:
        return self._balance

    def place_order(self, order: OrderRequest) -> OrderResult:
        self.orders.append(order)
        return OrderResult(
            order_id="mock_id_123",
            status="FILLED",
            filled_price=order.price or Decimal("50000"),
            filled_quantity=order.quantity
        )

    def get_positions(self) -> List[Position]:
        return self.positions

    def cancel_order(self, order_id: str) -> bool:
        return True

def test_broker_protocol_types():
    """Verify that MockBroker can be instantiated and used as a Broker."""
    broker: Broker = MockBroker(balance=Decimal("10000"))
    assert broker.get_balance() == Decimal("10000")

def test_order_structures():
    """Verify OrderRequest and OrderResult dataclasses."""
    req = OrderRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        quantity=Decimal("0.1"),
        price=Decimal("50000"),
        stop_loss=Decimal("49000"),
        take_profit=Decimal("52000")
    )
    
    broker = MockBroker(Decimal("10000"))
    res = broker.place_order(req)
    
    assert res.order_id == "mock_id_123"
    assert res.status == "FILLED"
    assert res.filled_quantity == Decimal("0.1")
    assert len(broker.orders) == 1
