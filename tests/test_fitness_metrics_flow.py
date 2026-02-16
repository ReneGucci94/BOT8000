import pytest
from src.optimization.fitness import SegmentMetrics

def test_metrics_conversion():
    # Simulate Worker output (percentages)
    worker_result = {
        "total_trades": 10,
        "return": 5.0,        # 5%
        "max_drawdown": 10.0, # 10%
        "sharpe": 1.5,
        "profit_factor": 2.0,
        "gross_profit": 1000.0,
        "gross_loss": 500.0
    }
    
    # Simulate run_wfo.py conversion logic
    metrics = SegmentMetrics(
        trades=worker_result.get("total_trades", 0),
        return_pct=worker_result.get("return", 0.0) / 100.0 if worker_result.get("return") else 0.0,
        maxdd=worker_result.get("max_drawdown", 0.0) / 100.0 if worker_result.get("max_drawdown") else 0.0,
        sharpe=worker_result.get("sharpe", 0.0),
        pf=worker_result.get("profit_factor", 0.0),
        gross_profit=worker_result.get("gross_profit", 0.0),
        gross_loss=worker_result.get("gross_loss", 0.0)
    )
    
    # Verify SegmentMetrics holds DECIMALS
    assert metrics.return_pct == 0.05
    assert metrics.maxdd == 0.10
    assert metrics.sharpe == 1.5
    assert metrics.trades == 10
    
def test_metrics_conversion_zero_values():
    # Simulate Worker output (zeros/None)
    worker_result = {
        "total_trades": 0,
        "return": 0.0,
        "max_drawdown": 0.0,
        "sharpe": 0.0,
        "profit_factor": 0.0,
        "gross_profit": 0.0,
        "gross_loss": 0.0
    }
    
    metrics = SegmentMetrics(
        trades=worker_result.get("total_trades", 0),
        return_pct=worker_result.get("return", 0.0) / 100.0 if worker_result.get("return") else 0.0,
        maxdd=worker_result.get("max_drawdown", 0.0) / 100.0 if worker_result.get("max_drawdown") else 0.0,
        sharpe=worker_result.get("sharpe", 0.0),
        pf=worker_result.get("profit_factor", 0.0),
        gross_profit=worker_result.get("gross_profit", 0.0),
        gross_loss=worker_result.get("gross_loss", 0.0)
    )
    
    assert metrics.return_pct == 0.0
    assert metrics.maxdd == 0.0
