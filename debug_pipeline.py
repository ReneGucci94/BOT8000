import sys
import logging
from src.agents.worker import OptimizerWorker
from src.database import init_db

# Configure logging to stdout
logging.basicConfig(level=logging.DEBUG)

def debug_run():
    init_db()
    
    # Config similar to what the pipeline uses
    config = {
        'pair': 'BTCUSDT',
        'timeframe': '4h',
        'year': 2024,
        'months': [1, 2],
        'stop_loss': 2000,
        'take_profit_multiplier': 2.0,
        'fee_rate': 0.001,
        'initial_balance': 10000,
        'risk_per_trade_pct': 1.0,
        'backtest_run_id': '00000000-0000-0000-0000-000000000000', # Dummy UUID
        'use_ml_model': False # Disable ML for basic logic test
    }
    
    print("Initializing Worker...")
    worker = OptimizerWorker("DEBUG_WORKER")
    
    print("Running Execute...")
    try:
        result = worker.execute(config)
        print("RESULT:", result)
    except Exception as e:
        print("EXCEPTION:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_run()
