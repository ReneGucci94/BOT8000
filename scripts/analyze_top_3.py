
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.database.connection import get_db_session
from src.database.models import Strategy, Trade
from sqlalchemy import desc, func

def calculate_max_drawdown(trades):
    if not trades:
        return 0.0
    
    cumulative_profit = 0
    peak = 0
    max_dd = 0
    
    for t in trades:
        pl = float(t.profit_loss) if t.profit_loss is not None else 0.0
        cumulative_profit += pl
        
        if cumulative_profit > peak:
            peak = cumulative_profit
        
        dd = peak - cumulative_profit
        if dd > max_dd:
            max_dd = dd
            
    return max_dd

def analyze_top_strategies():
    with get_db_session() as db:
        strategies = db.query(Strategy)\
            .filter(Strategy.status == 'APPROVED')\
            .order_by(desc(Strategy.profit_factor))\
            .limit(3)\
            .all()

        print("DEBUG: Trade Counts by Strategy Version:")
        trade_counts = db.query(Trade.strategy_version, func.count(Trade.id))\
            .group_by(Trade.strategy_version).all()
        for tv, count in trade_counts:
            print(f"  {tv}: {count} trades")
        print("\n")

        print(f"Found {len(strategies)} approved strategies.\n")

        for i, s in enumerate(strategies, 1):
            # Fetch trades for this strategy
            # Try matching by name first
            trades = db.query(Trade).filter(Trade.strategy_version == s.name).order_by(Trade.timestamp).all()
            
            # If no trades found, try matching by ID if applicable (though model says String(50))
            if not trades:
                 trades = db.query(Trade).filter(Trade.strategy_version == str(s.strategy_id)).order_by(Trade.timestamp).all()

            total_trades = len(trades)
            
            # Infer info from trades if missing in params
            pair = "N/A"
            timeframe = "N/A"
            if trades:
                pair = trades[0].pair
                timeframe = trades[0].timeframe
            
            # Calculate metrics
            max_dd = calculate_max_drawdown(trades)
            
            print(f"=== STRATEGY #{i}: {s.name} ===")
            print(f"Base Strategy: {s.base_strategy}")
            print(f"Status: {s.status}")
            
            # Performance
            print("\n--- Performance (Calculated from DB) ---")
            print(f"Total Trades: {total_trades}")
            print(f"Win Rate: {float(s.win_rate) if s.win_rate else 0.0:.1f}%")
            print(f"Profit Factor: {float(s.profit_factor) if s.profit_factor else 0.0:.2f}")
            print(f"Max Drawdown: {max_dd:.2f}")
            print(f"Sharpe Ratio: {float(s.sharpe_ratio) if s.sharpe_ratio else 'N/A'}")

            # Parameters
            params = s.parameters or {}
            print("\n--- Parameters ---")
            print(f"Pair: {pair}")
            print(f"Timeframe: {timeframe}")
            print(f"Stop Loss: {params.get('stop_loss', 'N/A')} pips (or multiplier)")
            print(f"Take Profit: {params.get('take_profit_multiplier', 'N/A')} (multiplier)")
            if 'risk_reward' in params:
                print(f"Risk Reward: {params['risk_reward']}")
            
            # Filters (ML)
            filters = s.filters or {}
            print("\n--- ML Filters ---")
            if filters and 'ml_avoidance' in filters:
                avoidance = filters['ml_avoidance']
                print(f"Description: {avoidance.get('description', 'N/A')}")
                print("Conditions:")
                for cond in avoidance.get('conditions', []):
                    print(f"  - {cond}")
            elif filters:
                 for k, v in filters.items():
                    print(f"{k}: {v}")
            else:
                print("None")
            
            print("\n" + "="*30 + "\n")

if __name__ == "__main__":
    analyze_top_strategies()
