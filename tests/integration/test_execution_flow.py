import pytest
from decimal import Decimal
from typing import List
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide
from execution.risk import RiskManager, RiskConfig
from execution.executor import TradeExecutor, TradeSignal

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

def test_full_execution_flow():
    """
    Integration Test: Execution Engine
    Flow: Signal -> Executor -> Risk Calc -> Broker Order
    
    Scenario:
    - Account: $10,000
    - Risk: 2% ($200)
    
    Signal:
    - Entry: $50,000
    - Stop Loss: $49,000 (Diff: $1,000)
    - Take Profit: $52,000
    
    Expected Calculation:
    - Risk Amount = $200
    - Position Size = $200 / $1,000 = 0.2 BTC
    
    Verification:
    - Broker receives BUY Order for 0.2 BTC at $50,000 limit.
    """
    # 1. Setup
    broker = MockBroker(balance=Decimal("10000"))
    risk_config = RiskConfig(risk_percentage=Decimal("0.02")) # 2%
    risk_manager = RiskManager(risk_config)
    executor = TradeExecutor(broker, risk_manager)
    
    # 2. Signal Injection
    signal = TradeSignal(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        entry_price=Decimal("50000"),
        stop_loss=Decimal("49000"),
        take_profit=Decimal("52000")
    )
    
    # 3. Execution
    result = executor.execute_trade(signal)
    
    # 4. Verification
    assert result is not None
    assert result.status == "FILLED"
    assert result.filled_quantity == Decimal("0.2") # Critical Check
    
    assert len(broker.orders) == 1
    placed_order = broker.orders[0]
    
    assert placed_order.symbol == "BTCUSDT"
    assert placed_order.side == OrderSide.BUY
    assert placed_order.type == OrderType.LIMIT
    assert placed_order.quantity == Decimal("0.2")
    assert placed_order.price == Decimal("50000")
    assert placed_order.stop_loss == Decimal("49000")
    assert placed_order.take_profit == Decimal("52000")
