import sys
import os
from decimal import Decimal
from typing import List

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

from core.timeframe import Timeframe
from core.market import MarketState
from utils.data_loader import load_binance_csv
from simulation.backtest import Backtester
from strategy.engine import TJRStrategy
from execution.executor import TradeExecutor
from execution.risk import RiskManager, RiskConfig
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderSide

# Re-using InMemoryBroker logic
class InMemoryBroker(Broker):
    def __init__(self, balance: int = 10000):
        self._balance = Decimal(str(balance))
        self.orders = []
        self.positions = []
        self.equity_curve = [self._balance]
        
    def get_balance(self) -> Decimal:
        return self._balance

    def place_order(self, order: OrderRequest) -> OrderResult:
        self.orders.append(order)
        pos = Position(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            entry_price=order.price if order.price else Decimal("0"),
            unrealized_pnl=Decimal("0")
        )
        self.positions.append(pos)
        return OrderResult(f"id_{len(self.orders)}", "FILLED", order.price, order.quantity)

    def get_positions(self) -> List[Position]:
        return self.positions
    
    def cancel_order(self, order_id: str) -> bool:
        return True

    def update_positions(self, current_price: Decimal):
        remaining = []
        for pos in self.positions:
            order = [o for o in self.orders if o.symbol == pos.symbol][-1]
            closed = False
            pnl = Decimal("0")
            
            if pos.side == OrderSide.BUY:
                if order.stop_loss and current_price <= order.stop_loss:
                    pnl = (order.stop_loss - pos.entry_price) * pos.quantity
                    closed = True
                elif order.take_profit and current_price >= order.take_profit:
                    pnl = (order.take_profit - pos.entry_price) * pos.quantity
                    closed = True
            elif pos.side == OrderSide.SELL:
                if order.stop_loss and current_price >= order.stop_loss:
                    pnl = (pos.entry_price - order.stop_loss) * pos.quantity
                    closed = True
                elif order.take_profit and current_price <= order.take_profit:
                    pnl = (pos.entry_price - order.take_profit) * pos.quantity
                    closed = True
            
            if closed:
                self._balance += pnl
                self.equity_curve.append(self._balance)
            else:
                remaining.append(pos)
        self.positions = remaining

def main():
    print("--- TJR Trading Bot v2: Backtest Console ---")
    data_path = "data/raw/BTCUSDT-5m-2024-12.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print(f"Loading data from {data_path}...")
    candles = load_binance_csv(data_path, Timeframe.M5)
    print(f"Loaded {len(candles)} candles.")

    # Setup
    broker = InMemoryBroker(10000)
    risk = RiskManager(RiskConfig(Decimal("0.01"))) # 1% Risk
    executor = TradeExecutor(broker, risk)
    strategy = TJRStrategy()
    backtester = Backtester()

    print("Running Backtest...")
    report = backtester.run(candles, broker, strategy, executor)

    print("\n--- RESULTS ---")
    print(f"Initial Balance: ${report.initial_balance}")
    print(f"Final Balance:   ${report.final_balance:.2f}")
    print(f"Net Profit:      ${report.net_profit:.2f}")
    print(f"Total Trades:    {report.total_trades}")
    print(f"Win Rate:        {report.win_rate:.2f}%")
    print(f"Max Drawdown:    ${report.max_drawdown:.2f}")
    print("----------------")

if __name__ == "__main__":
    main()
