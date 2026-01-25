
import sys
import os
import asyncio
from decimal import Decimal
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from src.database.connection import get_db_session
from src.database.models import Strategy
from sqlalchemy import desc
# from src.core.config import Config # Config not found, removing for now if unused or fixing path
# Checking if Config is actually needed. RiskManager uses RiskConfig which is imported from risk.
# StrategyRegistry is used. TJRStrategy is used.
# Let's remove this line for now.
# from src.strategy.registry import StrategyRegistry
from src.strategy.engine import TJRStrategy
from src.simulation.broker import InMemoryBroker
from src.utils.data_loader import load_binance_csv
from src.core.market import MarketState
from src.execution.executor import TradeExecutor
from src.execution.broker import OrderRequest, OrderSide, OrderType
from src.execution.risk import RiskManager, RiskConfig
from src.core.timeframe import Timeframe

def run_validation():
    print("=== OOS VALIDATION START (Data: May 2024) ===")
    
    # 1. Fetch Top 3 Strategies
    print("Fetching top 3 strategies...")
    with get_db_session() as db:
        strategies = db.query(Strategy)\
            .filter(Strategy.status == 'APPROVED')\
            .order_by(desc(Strategy.profit_factor))\
            .limit(3)\
            .all()
        strategy_data = []
        for s in strategies:
             strategy_data.append({
                 "name": s.name,
                 "pf": float(s.profit_factor) if s.profit_factor else 0.0,
                 "params": s.parameters,
                 "id": s.id
             })

    if not strategy_data:
        print("No approved strategies found.")
        return

    target_strategy_name = "TJR_Base_mut_58f9db"
    
    # 2. Define OOS Months
    oos_months = [
        {"name": "JUNE 2024", "file": "BTCUSDT-4h-2024-06.csv"},
        {"name": "JULY 2024", "file": "BTCUSDT-4h-2024-07.csv"}
    ]

    for month_info in oos_months:
        print(f"\n{'#'*20} TESTING {month_info['name']} {'#'*20}")
        
        data_path = os.path.join(os.getcwd(), 'data', 'raw', month_info['file'])
        if not os.path.exists(data_path):
            print(f"Error: File not found {data_path}")
            continue
            
        all_candles = load_binance_csv(data_path, Timeframe.H4)
        all_candles.sort(key=lambda c: c.timestamp)
        print(f"Data Loaded: {len(all_candles)} candles (4h).")

        for strat_info in strategy_data:
            if strat_info['name'] != target_strategy_name:
                continue
                
            print(f"\n>>> Strategy: {strat_info['name']}")
            
            # Instantiate Components
            raw_params = strat_info['params']
            sl_val = raw_params.get('stop_loss')
            tp_val = raw_params.get('take_profit_multiplier')
            
            strategy = TJRStrategy(
                fixed_stop_loss=Decimal(str(sl_val)),
                take_profit_multiplier=Decimal(str(tp_val))
            )
            
            broker = InMemoryBroker(
                balance=Decimal("10000"),
                fee_rate=Decimal("0.001")
            )
            
            risk_manager = RiskManager(
                config=RiskConfig(risk_percentage=Decimal("0.01"))
            )
            
            market = MarketState.empty("BTCUSDT")
            trades_count = 0
            
            for candle in all_candles:
                market = market.update(candle)
                broker.update_positions(Decimal(str(candle.close)))
                
                if not broker.get_positions():
                    signal = strategy.analyze(market, Timeframe.H4)
                    if signal:
                         # Signal object contains calculated SL/TP
                         sl_price = signal.stop_loss
                         tp_price = signal.take_profit
                         
                         if sl_price and tp_price:
                             entry_price = Decimal(str(candle.close))
                             size = risk_manager.calculate_position_size(
                                 account_balance=broker.get_balance(),
                                 entry_price=entry_price,
                                 stop_loss=sl_price
                             )
                             
                             if size > 0:
                                 order_req = OrderRequest(
                                     symbol="BTCUSDT",
                                     side=signal.side,
                                     type=OrderType.MARKET, 
                                     quantity=size,
                                     price=entry_price, 
                                     stop_loss=sl_price,
                                     take_profit=tp_price
                                 )
                                 
                                 broker.place_order(order_req)
                                 trades_count += 1
            
            # Metrics
            closed_trades = broker.get_closed_positions()
            wins = [t for t in closed_trades if t.pnl > 0]
            losses = [t for t in closed_trades if t.pnl <= 0]
            
            gross_profit = sum(t.pnl for t in wins)
            gross_loss = abs(sum(t.pnl for t in losses))
            
            pf = 0.0
            if gross_loss == 0:
                if gross_profit > 0:
                    pf = float('inf')
            else:
                pf = float(gross_profit / gross_loss)
                
            win_rate = (len(wins) / len(closed_trades) * 100) if closed_trades else 0.0
            
            print(f"Trades: {len(closed_trades)}")
            print(f"PF: {pf:.2f}")
            print(f"WR: {win_rate:.1f}%")
            
            if pf > 1.5:
                print(">>> STATUS: PASS (Robust)")
            else:
                print(">>> STATUS: FAIL or WEAK")

if __name__ == "__main__":
    run_validation()
