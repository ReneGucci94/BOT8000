from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Any
from .broker import Broker, OrderRequest, OrderResult, OrderSide, OrderType
from .risk import RiskManager

@dataclass(frozen=True)
class TradeSignal:
    """Strategy Signal converted to Execution Request."""
    symbol: str
    side: OrderSide
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    confidence: Optional[float] = None
    metadata: Optional[dict] = None

class TradeExecutor:
    def __init__(self, broker: Broker, risk_manager: RiskManager, strategy: Any = None):
        self.broker = broker
        self.risk_manager = risk_manager
        self.strategy = strategy

    def process_candle(self, candle: Any, market: Any, timeframe: Any):
        """Standard V3 loop: update broker -> check signal -> execute."""
        # 1. Update simulation/broker stops
        if hasattr(self.broker, 'update_positions'):
            self.broker.update_positions(candle.close)
            
        # 2. If no positions, look for new trades
        if not self.broker.get_positions() and self.strategy:
            signal = self.strategy.analyze(market, timeframe)
            if signal:
                self.execute_trade(signal)

    def execute_trade(self, signal: TradeSignal) -> Optional[OrderResult]:
        """
        Orchestrates trade execution:
        1. Get available balance.
        2. Calculate position size based on risk.
        3. Place order with broker.
        """
        balance = self.broker.get_balance()
        
        try:
            quantity = self.risk_manager.calculate_position_size(
                account_balance=balance,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss
            )
        except ValueError as e:
            # Handle invalid stops or zero division
            print(f"Risk Calculation Error: {e}")
            return None
            
        if quantity <= 0:
            print("Calculated Quantity is 0. Trade Aborted.")
            return None
            
        # Create Order Request
        order_req = OrderRequest(
            symbol=signal.symbol,
            side=signal.side,
            type=OrderType.LIMIT, # Assuming Limit Entry for now from Signal
            quantity=quantity,
            price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            metadata=signal.metadata
        )
        
        # Place Order
        result = self.broker.place_order(order_req)
        return result
