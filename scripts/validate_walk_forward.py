
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from src.agents.worker import OptimizerWorker

class WalkForwardValidator:
    def __init__(self):
        self.year = 2024
        self.base_config = {
            'pair': 'BTCUSDT',
            'timeframe': '4h',
            'year': self.year,
            'stop_loss': 2000,
            'take_profit_multiplier': 2.0,
            'initial_balance': 10000,
            'fee_rate': 0.001,
            'risk_per_trade_pct': 1.0,
            'use_msc': True,  # Use MSC (v3) as requested
            'use_alpha_engine': False,
            'alpha_threshold': 0.1
        }
    
    def generate_windows(self) -> List[Dict[str, Any]]:
        """
        Generate 9 rolling windows:
        W1: Train [1,2,3] -> Test 4
        ...
        W9: Train [9,10,11] -> Test 12
        """
        windows = []
        for i in range(1, 10):
            train_start = i
            train_end = i + 2
            test_month = i + 3
            windows.append({
                'id': i,
                'train_months': list(range(train_start, train_end + 1)),
                'test_month': test_month,
                'label': f"Train {train_start}-{train_end} -> Test {test_month}"
            })
        return windows

    def run(self) -> Dict[str, Any]:
        """Execute the WFV process."""
        windows = self.generate_windows()
        window_results = []
        
        print("\n=== STARTING WALK-FORWARD VALIDATION (MSC v3) ===")
        print(f"Data: {self.year} | Windows: {len(windows)}\n")
        
        for win in windows:
            print(f"Running Window {win['id']}: {win['label']}...")
            
            # NOTE: Normally we would Optimize on Train then Validate on Test.
            # For this validation request, we are assuming the Strategy logic is constant (Layer 1 Brain)
            # and we just want to see how it performs on the Out-of-Sample month.
            # So we only run the backtest on the 'test_month'.
            
            worker = OptimizerWorker(f"WFV-Win{win['id']}")
            config = self.base_config.copy()
            config['months'] = [win['test_month']]
            config['backtest_run_id'] = str(uuid.uuid4())
            
            try:
                result = worker.run(config)
                
                # Add window metadata
                result['window_id'] = win['id']
                result['test_month'] = win['test_month']
                window_results.append(result)
                
                print(f"-> Result: PF {result.get('profit_factor', 0):.2f} | WR {result.get('win_rate', 0)}% | Trades {result.get('total_trades', 0)}")
                
            except Exception as e:
                print(f"-> Error in Window {win['id']}: {e}")
                # Append empty/failed result to keep index alignment? Or just skip using
                window_results.append({
                     'window_id': win['id'],
                     'test_month': win['test_month'],
                     'profit_factor': 0.0,
                     'win_rate': 0.0,
                     'total_trades': 0,
                     'final_balance': 10000.0,
                     'max_drawdown_pct': 0.0
                })
        
        # Calculate stats
        stats = self.calculate_statistics(window_results)
        
        return {
            'window_results': window_results,
            'stats': stats
        }
    
    def calculate_statistics(self, results: List[Dict]) -> Dict[str, float]:
        if not results:
            return {}
            
        pfs = [r.get('profit_factor', 0) for r in results]
        wrs = [r.get('win_rate', 0) for r in results]
        bals = [r.get('final_balance', 10000) for r in results]
        
        avg_pf = float(np.mean(pfs))
        std_pf = float(np.std(pfs))
        
        avg_wr = float(np.mean(wrs))
        
        # Total return of the system (compounding or sum?)
        # Sum of net profits:
        total_profit = sum(b - 10000 for b in bals)
        final_system_balance = 10000 + total_profit
        
        return {
            'avg_pf': round(avg_pf, 2),
            'consistency_score': round(std_pf, 2),
            'avg_win_rate': round(avg_wr, 1),
            'total_profit': round(total_profit, 2),
            'final_est_balance': round(final_system_balance, 2)
        }

    def print_report(self, summary: Dict):
        print("\n" + "="*80)
        print("WALK-FORWARD VALIDATION REPORT")
        print("="*80)
        
        print(f"{'Window':<8} | {'Test Month':<12} | {'Trades':<8} | {'WinRate':<10} | {'PF':<6} | {'Balance':<12} | {'MaxDD':<8}")
        print("-" * 80)
        
        for res in summary['window_results']:
            print(f"W{res.get('window_id', 0):<7} | "
                  f"{res.get('test_month', 0):<12} | "
                  f"{res.get('total_trades', 0):<8} | "
                  f"{res.get('win_rate', 0):.1f}%{' ':<5} | "
                  f"{res.get('profit_factor', 0):.2f}{' ':<2} | "
                  f"${res.get('final_balance', 0):<11,.2f} | "
                  f"{res.get('max_drawdown_pct', 0):.1f}%")
        
        print("-" * 80)
        stats = summary['stats']
        print(f"\nAVERAGE PROFIT FACTOR: {stats.get('avg_pf', 0)} (Target > 1.2)")
        print(f"CONSISTENCY SCORE (StdDev): {stats.get('consistency_score', 0)} (Target < 0.5)")
        print(f"ESTIMATED TOTAL BALANCE: ${stats.get('final_est_balance', 0):,.2f}")
        print("="*80)

if __name__ == "__main__":
    validator = WalkForwardValidator()
    summary = validator.run()
    validator.print_report(summary)
