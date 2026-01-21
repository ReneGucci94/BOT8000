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

from simulation.broker import InMemoryBroker

def main():
    print("--- TJR Trading Bot v2: Backtest Console (1H TIMEFRAME - PIVOT) ---")
    data_path = "data/raw/BTCUSDT-1h-2024-12.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print(f"Loading data from {data_path}...")
    candles = load_binance_csv(data_path, Timeframe.H1)
    print(f"Loaded {len(candles)} candles.")

    # Setup
    broker = InMemoryBroker(balance=Decimal("10000"))
    risk = RiskManager(RiskConfig(Decimal("0.01"))) # 1% Risk
    executor = TradeExecutor(broker, risk)
    strategy = TJRStrategy()
    backtester = Backtester()

    print("Running Backtest...")
    report = backtester.run(candles, broker, strategy, executor, Timeframe.H1)

    print("\n--- RESULTS (1H) ---")
    print(f"Initial Balance: ${report.initial_balance}")
    print(f"Final Balance:   ${report.final_balance:.2f}")
    print(f"Net Profit:      ${report.net_profit:.2f}")
    print(f"Total Fees Paid: ${broker.total_fees_paid:.2f}")
    print(f"Total Trades:    {report.total_trades}")
    print(f"Win Rate:        {report.win_rate:.2f}%")
    print(f"Max Drawdown:    ${report.max_drawdown:.2f}")
    print("----------------")


if __name__ == "__main__":
    main()
