import pytest
from decimal import Decimal
from typing import List, Optional
from dataclasses import dataclass
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide
from execution.risk import RiskManager, RiskConfig
# Executor will be imported from execution.executor

# Mock Broker (Reused or localized)
class MockBroker(Broker):
    def __init__(self, balance: Decimal):
        self._balance = balance
        self.orders: List[OrderRequest] = []
        
    def get_balance(self) -> Decimal:
        return self._balance

    def place_order(self, order: OrderRequest) -> OrderResult:
        self.orders.append(order)
        return OrderResult("id_1", "FILLED", order.price, order.quantity)

    def get_positions(self) -> List[Position]:
        return []
    
    def cancel_order(self, order_id: str) -> bool:
        return True

# Helper to define Signal here if not yet in module, 
# but test implies it should be in module.
from execution.executor import TradeExecutor, TradeSignal

def test_execute_long_trade():
    """
    Signal: Buy BTC at 50000, SL 49000.
    Balance: 10000. Risk 1% ($100).
    Expected Qty: 0.1.
    """
    broker = MockBroker(Decimal("10000"))
    risk = RiskManager(RiskConfig(Decimal("0.01")))
    executor = TradeExecutor(broker, risk)
    
    signal = TradeSignal(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        entry_price=Decimal("50000"),
        stop_loss=Decimal("49000"),
        take_profit=Decimal("52000")
    )
    
    result = executor.execute_trade(signal)
    
    assert result is not None
    assert result.status == "FILLED"
    assert result.filled_quantity == Decimal("0.1")
    
    # Check Broker received order
    assert len(broker.orders) == 1
    order = broker.orders[0]
    assert order.symbol == "BTCUSDT"
    assert order.side == OrderSide.BUY
    assert order.quantity == Decimal("0.1")
    assert order.stop_loss == Decimal("49000")

def test_execute_short_trade():
    """
    Signal: Sell BTC at 50000, SL 51000.
    Balance: 10000. Risk 1% ($100).
    Expected Qty: 0.1.
    """
    broker = MockBroker(Decimal("10000"))
    risk = RiskManager(RiskConfig(Decimal("0.01")))
    executor = TradeExecutor(broker, risk)
    
    signal = TradeSignal(
        symbol="BTCUSDT",
        side=OrderSide.SELL,
        entry_price=Decimal("50000"),
        stop_loss=Decimal("51000"),
        take_profit=Decimal("48000")
    )
    
    result = executor.execute_trade(signal)
    
    assert result.filled_quantity == Decimal("0.1")
    assert broker.orders[0].side == OrderSide.SELL
