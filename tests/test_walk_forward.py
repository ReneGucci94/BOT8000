import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

# Import will be available after we create the script, 
# for now we define the test expectation based on the design.
# We will use sys.path hack to import from scripts if needed or just assume structure.

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking the OptimizerWorker since we don't want to run real backtests in unit test
@pytest.fixture
def mock_worker():
    with patch('scripts.validate_walk_forward.OptimizerWorker') as MockWorker:
        instance = MockWorker.return_value
        # Default mock return
        instance.run.return_value = {
            'total_trades': 10,
            'win_rate': 50.0,
            'profit_factor': 1.5,
            'final_balance': 10500.0,
            'max_drawdown_pct': 5.0
        }
        yield MockWorker

def test_window_generation(mock_worker):
    from scripts.validate_walk_forward import WalkForwardValidator
    
    validator = WalkForwardValidator()
    windows = validator.generate_windows()
    
    assert len(windows) == 9
    
    # Check first window (Train Jan-Mar, Test Apr)
    # Note: We are only running Test period in this specific simplified request, 
    # or are we simulating Full WFV? 
    # The prompt said: "Window 1: Train Ene-Mar -> Test Abr". 
    # Usually WFV runs optimization on Train and then validation on Test.
    # However, since we are just "Validating" the current strategy (which is fixed/optimized manually),
    # we might just be running the Test period. 
    # Let's assume the script primarily runs the Test period to measure out-of-sample performance.
    
    assert windows[0]['id'] == 1
    assert windows[0]['train_months'] == [1, 2, 3]
    assert windows[0]['test_month'] == 4
    
    # Check last window
    assert windows[-1]['id'] == 9
    assert windows[-1]['train_months'] == [9, 10, 11]
    assert windows[-1]['test_month'] == 12

def test_metrics_aggregation(mock_worker):
    from scripts.validate_walk_forward import WalkForwardValidator
    
    validator = WalkForwardValidator()
    
    # Mock results for 2 windows
    results = [
        {'profit_factor': 1.5, 'win_rate': 60.0},
        {'profit_factor': 0.5, 'win_rate': 40.0}, # Bad window
        {'profit_factor': 2.0, 'win_rate': 50.0}
    ]
    
    stats = validator.calculate_statistics(results)
    
    # Avg PF: (1.5 + 0.5 + 2.0) / 3 = 1.333
    assert abs(stats['avg_pf'] - 1.33) < 0.01
    
    # Consistency Score (Std Dev)
    # Mean: 1.333
    # Vars: (1.5-1.33)^2 + (0.5-1.33)^2 + (2.0-1.33)^2 
    #       0.027 + 0.694 + 0.444 = 1.165
    # Var = 1.165 / 3 = 0.388 (or /2 for sample std dev)
    # StdDev = approx 0.6 - 0.7
    assert 'consistency_score' in stats
    assert stats['consistency_score'] > 0

def test_full_flow_run(mock_worker):
    from scripts.validate_walk_forward import WalkForwardValidator
    
    validator = WalkForwardValidator()
    
    # Mock running
    mock_worker_instance = mock_worker.return_value
    mock_worker_instance.run.side_effect = [
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
        {'profit_factor': 1.0, 'total_trades': 5, 'final_balance': 10000},
    ]
    
    summary = validator.run()
    
    # Should have called worker run 9 times
    assert mock_worker_instance.run.call_count == 9
    assert len(summary['window_results']) == 9
    assert summary['stats']['avg_pf'] == 1.0
