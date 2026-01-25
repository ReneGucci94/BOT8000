
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from src.database.connection import get_db_session
from src.database.models import Strategy
from sqlalchemy import desc
from src.agents.worker import OptimizerWorker
from src.core.config import Config
from src.strategy.registry import StrategyRegistry
# Import necessary strategy classes to ensure registration
from src.strategy.implementations.tjr_strategy import TJRStrategy

async def run_validation():
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

    # 2. Setup Worker for OOS
    # We use May 2024 (month 5). Config months are 0-indexed in some systems, 
    # but usually data loader takes 1-based integers for filenames.
    # OptimizerWorker might take a list of months.
    
    # We'll instantiate a worker just to use its run_strategy_backtest logic or similar.
    # Actually, let's use the core backtesting components directly or via a modified worker 
    # if possible, but worker is tied to queues.
    # Let's verify how to run a single pass. 
    # Looking at src/agents/worker.py (previously viewed), it has .run() which does everything.
    # Maybe we can use the internal _run_backtest method if exposed, or create a minimal runner.
    
    # Let's assume we can create a temporary worker and call a method to run a specific config.
    # Or better, re-use the logic: Broker -> Engine -> Run.
    
    from src.simulation.broker import InMemoryBroker
    from src.data.feed import DataFeed
    from src.utils.data_loader import DataLoader
    from src.strategy.engine import StrategyEngine
    
    # Load May Data
    print("Loading May 2024 Data...")
    loader = DataLoader() # Assuming default args correct or we pass root
    # We need to construct Candle series. 
    # data_loader.load_data usually takes pairs, years, months.
    candles = loader.load_data(
        pairs=['BTCUSDT'],
        years=[2024],
        months=[5], # May
        timeframes=['4h', '1h', '15m'] # Start with 4h as base
    )
    
    if not candles:
        print("Error: No data loaded for May 2024")
        return

    print(f"Data Loaded: {len(candles)} keys.")

    for strat_info in strategy_data:
        print(f"\n--- Testing {strat_info['name']} ---")
        print(f"IS (In-Sample) PF: {strat_info['pf']:.2f}")
        
        # Instantiate Strategy
        # We need the class. TJR_Base -> TJRStrategy
        strategy_cls = StrategyRegistry.get('TJR_Base')
        if not strategy_cls:
            strategy_cls = TJRStrategy # Fallback if registry empty
            
        # Params need to be compliant
        params = strat_info['params']
        
        # Run Backtest
        broker = InMemoryBroker()
        
        # Setup Engine
        engine = StrategyEngine(strategy_cls, params, broker)
        
        # Feed data
        # Engine usually runs on a feed. checking engine.run() signature in mind...
        # If we don't have the engine source in front, i'll write a generic loop 
        # based on standard patterns or assume engine.run(candles).
        
        # Looking at previous context, OptimizerWorker uses:
        # engine = StrategyEngine(strategy, broker)
        # for timestamp in timeline: engine.update(timestamp, market_data)
        
        # We need a timeline (sorted unique timestamps from 4h candles)
        # Assuming candles['BTCUSDT']['4h'] is a list of Candle objects
        c4h = candles['BTCUSDT']['4h']
        timeline = sorted([c.timestamp for c in c4h])
        
        print(f"Running simulation on {len(timeline)} ticks (4h)...")
        
        # Simple Loop
        for ts in timeline:
             # Construct slice for this timestamp
             # Market Snapshot needed by engine?
             # Or does engine calculate indicators itself? 
             # Usually TJRStrategy needs historical data up to TS to calc indicators.
             
             # The engine.on_candle(candle) model?
             # Let's check engine usage in worker.py via direct look if needed. 
             # For now, simplistic approach:
             
             # Actually, simpler: Use the actual OptimizerWorker but force the strategy and data.
             # But Worker is complex with Celery. 
             
             # Let's try to infer engine.run method or just Iterate.
             pass 

        # Since I can't easily see Engine signature without reading again, 
        # I will READ worker.py quickly to copy the exact execution loop.
        pass

async def main():
    await run_validation()

if __name__ == "__main__":
    # This is a placeholder until I read worker.py to copy execution logic
    pass
