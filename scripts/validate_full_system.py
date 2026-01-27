# scripts/validate_full_system.py
import sys
import os
# Asegurar que el root del proyecto esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.worker import OptimizerWorker
import uuid

def run_full_comparison():
    # Dataset: BTCUSDT 4h, todo 2024
    # Nota: El user pidió meses 1-12.
    config_base = {
        'pair': 'BTCUSDT',
        'timeframe': '4h',
        'year': 2024,
        'months': list(range(1, 13)),  # Ene-Dic
        'stop_loss': 2000,
        'take_profit_multiplier': 2.0,
        'initial_balance': 10000,
        'fee_rate': 0.001,
        'risk_per_trade_pct': 1.0,
        'alpha_threshold': 0.1 # Threshold bajo para asegurar que veamos actividad en este test de validación
    }
    
    results = {}
    
    # Test 1: Legacy TJR
    print("\n=== Test 1: Legacy TJR ===")
    worker1 = OptimizerWorker("legacy")
    config1 = {**config_base, 'backtest_run_id': str(uuid.uuid4()), 'use_msc': False, 'use_alpha_engine': False}
    results['legacy'] = worker1.run(config1)
    
    # Test 2: Alpha Engine
    print("\n=== Test 2: Alpha Engine ===")
    worker2 = OptimizerWorker("alpha")
    config2 = {**config_base, 'use_alpha_engine': True, 'use_msc': False, 'backtest_run_id': str(uuid.uuid4())}
    results['alpha'] = worker2.run(config2)
    
    # Test 3: MSC Orchestrator
    print("\n=== Test 3: MSC Orchestrator ===")
    worker3 = OptimizerWorker("msc")
    config3 = {**config_base, 'use_msc': True, 'use_alpha_engine': False, 'backtest_run_id': str(uuid.uuid4())}
    results['msc'] = worker3.run(config3)
    
    # Comparación
    print("\n" + "="*60)
    print("COMPARACIÓN DE SISTEMAS (2024 COMPLETO)")
    print("="*60)
    
    # Tabla simple
    print(f"{'Sistema':<20} | {'Trades':<8} | {'WinRate':<10} | {'PF':<6} | {'Balance':<12} | {'MaxDD':<8}")
    print("-" * 75)
    
    for system, result in results.items():
        print(f"{system.upper():<20} | "
              f"{result.get('total_trades', 0):<8} | "
              f"{result.get('win_rate', 0):.1f}%{' ':<5} | "
              f"{result.get('profit_factor', 0):.2f}{' ':<2} | "
              f"${result.get('final_balance', 0):<11,.2f} | "
              f"{result.get('max_drawdown_pct', 0):.1f}%")
    
    print("="*60)
    
    # Validación mínima
    assert results['msc'].get('total_trades', 0) > 0, "MSC no generó trades"
    print("\n✓ Full system validation PASSED")

if __name__ == "__main__":
    run_full_comparison()
