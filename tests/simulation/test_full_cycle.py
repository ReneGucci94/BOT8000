import pytest
from decimal import Decimal
from typing import List, Optional
from core.market import MarketState
from core.timeframe import Timeframe
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide
from execution.risk import RiskManager, RiskConfig
from execution.executor import TradeExecutor
from strategy.engine import TJRStrategy
from simulation.generator import MarketGenerator

class InMemoryBroker(Broker):
    """Simple Broker for Simulation (Stores state in memory)."""
    def __init__(self, balance: int = 10000):
        self._balance = Decimal(str(balance))
        self.orders: List[OrderRequest] = []
        self.positions: List[Position] = []
        self.equity_curve: List[Decimal] = [self._balance]
        
    def get_balance(self) -> Decimal:
        return self._balance

    def place_order(self, order: OrderRequest) -> OrderResult:
        # Simulate Fill immediately at Request Price
        self.orders.append(order)
        
        # Open a position
        pos = Position(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            entry_price=order.price if order.price else Decimal("0"),
            unrealized_pnl=Decimal("0")
        )
        self.positions.append(pos)
        
        return OrderResult(
            order_id=f"sim_{len(self.orders)}",
            status="FILLED",
            filled_price=order.price,
            filled_quantity=order.quantity
        )

    def get_positions(self) -> List[Position]:
        return self.positions
    
    def cancel_order(self, order_id: str) -> bool:
        return True

    def update_positions(self, current_price: Decimal):
        """Simulate TP/SL logic for open positions."""
        remaining_positions = []
        for pos in self.positions:
            # Find the original order for SL/TP
            # (Simplified: we use the last order we put in)
            last_order = [o for o in self.orders if o.symbol == pos.symbol][-1]
            
            closed = False
            pnl = Decimal("0")
            
            if pos.side == OrderSide.BUY:
                if last_order.stop_loss and current_price <= last_order.stop_loss:
                    # SL Hit
                    pnl = (last_order.stop_loss - pos.entry_price) * pos.quantity
                    closed = True
                elif last_order.take_profit and current_price >= last_order.take_profit:
                    # TP Hit
                    pnl = (last_order.take_profit - pos.entry_price) * pos.quantity
                    closed = True
            elif pos.side == OrderSide.SELL:
                if last_order.stop_loss and current_price >= last_order.stop_loss:
                    # SL Hit
                    pnl = (pos.entry_price - last_order.stop_loss) * pos.quantity
                    closed = True
                elif last_order.take_profit and current_price <= last_order.take_profit:
                    # TP Hit
                    pnl = (pos.entry_price - last_order.take_profit) * pos.quantity
                    closed = True
            
            if closed:
                self._balance += pnl
                self.equity_curve.append(self._balance)
            else:
                remaining_positions.append(pos)
        
        self.positions = remaining_positions

def test_full_paper_trading_simulation():
    """
    Runs the bot over 50 generated market cycles (approx 1000 candles).
    Expects positive trades or at least executed orders.
    """
    # 1. Init System
    broker = InMemoryBroker(balance=10000)
    risk = RiskManager(RiskConfig(Decimal("0.01"))) # 1% Risk
    executor = TradeExecutor(broker, risk)
    strategy = TJRStrategy()
    
    market = MarketState.empty("BTCUSDT")
    generator = MarketGenerator(start_price=50000)
    
    orders_placed = 0
    
    # 2. Simulation Loop
    print("\nStarting Simulation...")
    for i, candle in enumerate(generator.generate_cycle_stream(cycles=50)):
        # A. Update Market
        market = market.update(candle)
        
        # B. Check for SL/TP on current Price
        broker.update_positions(candle.close)
        
        # C. Analyze Strategy (If no open balance is tied up? For now simple)
        # Only trade if no open positions for simplicity in this sim
        if not broker.get_positions():
            signal = strategy.analyze(market, Timeframe.M5)
            if signal:
                result = executor.execute_trade(signal)
                if result and result.status == "FILLED":
                    orders_placed += 1
                
        # Optional: Print progress
        if i % 200 == 0:
            print(f"Candle {i}: Price {candle.close:.2f}, Balance {broker.get_balance():.2f}, Orders: {orders_placed}")
            
    print(f"\nSimulation Complete. Candles: {i+1}")
    print(f"Orders Placed: {orders_placed}")
    print(f"Final Balance: {broker.get_balance():.2f}")
    
    # 3. Verification
    # Given the generator is 100% Bullish Cycles (which bot is trained to spot)
    # we expect it to find trades. Profitability is variable due to noise.
    current_balance = broker.get_balance()
    win_count = len([e for i, e in enumerate(broker.equity_curve[1:]) if e > broker.equity_curve[i]])
    total_trades = len(broker.equity_curve) - 1
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
    
    print(f"Win Rate: {win_rate:.2f}% ({win_count}/{total_trades})")
    print(f"Final Balance: {current_balance:.2f}")

    assert orders_placed > 0, "No orders were placed by the strategy"
    assert current_balance > Decimal("8000"), "Strategy experienced excessive drawdown"
    assert len(broker.orders) == orders_placed

