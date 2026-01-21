import sys
import os
import glob
from decimal import Decimal
from typing import List

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

from core.timeframe import Timeframe
from utils.data_loader import load_binance_csv
from simulation.backtest import Backtester
from strategy.engine import TJRStrategy
from execution.executor import TradeExecutor
from execution.risk import RiskManager, RiskConfig
from simulation.broker import InMemoryBroker

def run_backtest_for_file(file_path: str, timeframe: Timeframe):
    # Setup
    broker = InMemoryBroker(balance=Decimal("10000"))
    risk = RiskManager(RiskConfig(Decimal("0.01"))) # 1% Risk
    executor = TradeExecutor(broker, risk)
    strategy = TJRStrategy()
    backtester = Backtester()

    # Load data
    candles = load_binance_csv(file_path, timeframe)
    
    # Run
    report = backtester.run(candles, broker, strategy, executor, timeframe)
    
    return report, broker.total_fees_paid

def main():
    # SETTINGS
    TARGET_TIMEFRAME = Timeframe.H1
    GLO_PATTERN = "*-1h-*.csv"
    
    print(f"--- TJR Trading Bot v2: Multi-Month Backtest ({TARGET_TIMEFRAME.value.upper()}) ---")
    data_dir = "data/raw/"
    csv_files = sorted(glob.glob(os.path.join(data_dir, GLO_PATTERN)))
    
    if not csv_files:
        print(f"No {TARGET_TIMEFRAME.value} CSV files found in {data_dir}")
        return

    results = []
    
    print(f"{'Month':<15} | {'Net Profit':<11} | {'Fees':<10} | {'Win Rate':<8} | {'Trades':<6} | {'Max DD':<9}")
    print("-" * 75)

    total_net = Decimal("0")
    total_fees = Decimal("0")
    total_trades = 0
    months_profitable = 0

    for file_path in csv_files:
        month_name = os.path.basename(file_path).split("-")[2] # Extract YYYY-MM
        
        try:
            report, fees = run_backtest_for_file(file_path, TARGET_TIMEFRAME)
            
            if report.net_profit > 0:
                months_profitable += 1
                
            print(f"{month_name:<15} | ${report.net_profit:>10.2f} | ${fees:>9.2f} | {report.win_rate:>7.2f}% | {report.total_trades:>6} | ${report.max_drawdown:>8.2f}")
            
            results.append({
                "month": month_name,
                "profit": report.net_profit,
                "fees": fees,
                "win_rate": report.win_rate,
                "trades": report.total_trades,
                "dd": report.max_drawdown
            })
            
            total_net += report.net_profit
            total_fees += fees
            total_trades += report.total_trades
            
        except Exception as e:
            print(f"{month_name:<15} | Error: {e}")

    print("-" * 75)
    print(f"{'TOTAL':<15} | ${total_net:>10.2f} | ${total_fees:>9.2f} | {'N/A':<8} | {total_trades:>6} | {'N/A':<9}")
    print(f"\nMonths Profitable: {months_profitable}/{len(csv_files)}")
    print(f"Total Strategy Net (After Fees) for {TARGET_TIMEFRAME.value}: ${total_net:.2f}")

if __name__ == "__main__":
    main()
