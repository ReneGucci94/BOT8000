# scripts/validate_alpha_engine.py
from src.agents.worker import OptimizerWorker
from src.utils.data_loader import load_binance_csv
from src.core.timeframe import Timeframe
import uuid

def run_comparison():
    # Dataset config
    pair = 'BTCUSDT'
    tf_str = '4h'
    timeframe = Timeframe(tf_str)
    year = 2024
    months = [1]
    
    config_base = {
        'pair': pair,
        'timeframe': tf_str,
        'year': year,
        'months': months,
        'stop_loss': 2000,
        'take_profit_multiplier': 2.0,
        'initial_balance': 10000,
        'fee_rate': 0.001,
        'risk_per_trade_pct': 1.0,
        'backtest_run_id': str(uuid.uuid4())
    }
    
    print(f"Loading data for {pair} {tf_str} {year}...")
    
    # Test 1: Legacy TJR
    print("\nRunning Test 1: Legacy TJR Strategy...")
    worker_legacy = OptimizerWorker("legacy-test")
    config_legacy = {**config_base, 'use_alpha_engine': False}
    result_legacy = worker_legacy.run(config_legacy)
    
    # Test 2: Alpha Engine
    print("\nRunning Test 2: Pure Alpha Engine...")
    worker_alpha = OptimizerWorker("alpha-test")
    config_alpha = {**config_base, 'use_alpha_engine': True, 'alpha_threshold': 0.1}
    result_alpha = worker_alpha.run(config_alpha)
    
    # Compare
    print("\n" + "="*30)
    print("      VALIDATION RESULTS")
    print("="*30)
    print(f"Legacy TJR:")
    print(f"  Trades: {result_legacy.get('total_trades', 0)}")
    print(f"  PF: {result_legacy.get('profit_factor', 0):.2f}")
    print(f"  Win Rate: {result_legacy.get('win_rate', 0):.1f}%")
    print(f"  Final Balance: ${result_legacy.get('final_balance', 0):.2f}")
    
    print(f"\nAlpha Engine:")
    print(f"  Trades: {result_alpha.get('total_trades', 0)}")
    print(f"  PF: {result_alpha.get('profit_factor', 0):.2f}")
    print(f"  Win Rate: {result_alpha.get('win_rate', 0):.1f}%")
    print(f"  Final Balance: ${result_alpha.get('final_balance', 0):.2f}")
    print("="*30)
    
    # Validation minimum requirements
    assert result_alpha.get('total_trades', 0) > 0, "Alpha Engine generated NO trades"
    print("\n✓ Alpha Engine validation PASSED")

if __name__ == "__main__":
    run_comparison()
