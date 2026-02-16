
import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from src.agents.worker import OptimizerWorker
from src.simulation.broker import Broker

class MockBroker:
    def __init__(self):
        self.equity_curve = [10000, 10100, 10200, 10150, 10300]
        self.total_fees_paid = Decimal("10.0")

    def get_balance(self):
        return Decimal("10300")
        
    def get_positions(self):
        return []

class MockPosition:
    def __init__(self, pnl):
        self.pnl = Decimal(str(pnl))

def test_worker_result_contains_all_metrics():
    """
    Simulate a run result and check effectively ALL keys required by fitness.py
    and run_wfo.py are present and correct.
    """
    # 1. Setup Mock Worker with correct signature
    worker = OptimizerWorker(worker_id="test_worker")
    
    # Mock internal components
    worker.broker = MockBroker()
    worker.broker.closed_positions = [
        MockPosition(150),  # Win
        MockPosition(-50),  # Loss
        MockPosition(200)   # Win
    ]
    # Trade counts
    worker.total_trades = 3
    worker.winning_trades = 2
    worker.losing_trades = 1
    
    # Mock config that would be passed to run/init
    # In run(), config is merged. _calculate_metrics will likely need access to these.
    # We'll assume _calculate_metrics takes (initial_balance, pair, timeframe_str) 
    # OR uses self.config if we set it. Worker doesn't seem to store self.config globally in run.
    # Let's assume we pass the config dict to _calculate_metrics or it uses local vars.
    # For now, let's assume we are testing a new method:
    # _calculate_metrics(self, final_balance, initial_balance, pair, timeframe, year, trades_saved, filtered_trades)
    
    initial_balance = Decimal("10000")
    final_balance = Decimal("10300")
    
    # 2. Call the new method (which doesn't exist yet -> RED)
    # We expect this to return the dictionary with ALL keys
    result = worker._calculate_metrics(
        initial_balance=initial_balance,
        final_balance=final_balance,
        pair="BTCUSDT",
        timeframe_str="4h",
        year=2024,
        trades_saved=3,
        filtered_trades=0,
        closed_positions=worker.broker.closed_positions,
        equity_curve=[10000, 10150, 10100, 10300] # Mock positive equity curve
    )
    
    # 3. Assertions
    # Required keys by fitness.py / run_wfo.py
    required_keys = [
        "total_trades", "winning_trades", "losing_trades",
        "final_balance", "net_profit", "return", 
        "gross_profit", "gross_loss", "profit_factor",
        "max_drawdown", "sharpe", "win_rate"
    ]
    
    for key in required_keys:
        assert key in result, f"Key {key} missing from result"
        
    # Validation of values
    assert result["gross_profit"] == 350.0  # 150 + 200
    assert result["gross_loss"] == 50.0     # |-50|
    assert result["profit_factor"] == 7.0   # 350 / 50
    assert result["return"] == 3.0          # 300 / 10000 * 100
    assert result["max_drawdown"] >= 0.0    # Should be % (e.g. 0.5 not 0.005 if small)
    
    # Sharpe check (mock broker has positive equity curve)
    assert result["sharpe"] > 0.0
