import pytest
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from src.database.models import Trade
# We expect this import to fail initially
from src.portfolio.correlation import calculate_correlation, build_equity_curve

def create_mock_trades(start_time, pnl_sequence):
    trades = []
    current_time = start_time
    for pnl in pnl_sequence:
        trades.append(Trade(
            timestamp=current_time,
            profit_loss=Decimal(str(pnl))
        ))
        current_time += timedelta(days=1)
    return trades

def test_perfect_correlation():
    # Dos estrategias idénticas deben tener corr = 1.0
    start = datetime(2024, 1, 1)
    trades_a = create_mock_trades(start, [100, 200, -50, 100])
    trades_b = create_mock_trades(start, [100, 200, -50, 100])
    
    corr = calculate_correlation(trades_a, trades_b)
    assert corr == pytest.approx(1.0, 0.01)

def test_inverse_correlation():
    # Espejos deben tener corr = -1.0
    start = datetime(2024, 1, 1)
    trades_a = create_mock_trades(start, [100, 100, 100])
    trades_b = create_mock_trades(start, [-100, -100, -100])
    
    corr = calculate_correlation(trades_a, trades_b)
    assert corr == pytest.approx(-1.0, 0.01)

def test_uncorrelated():
    # Random vs Random debería ser bajo
    start = datetime(2024, 1, 1)
    # A: 100, 100, 0, 0 -> Eq: 100, 200, 200, 200
    # B: 0, 0, 100, 100 -> Eq: 0, 0, 100, 200
    trades_a = create_mock_trades(start, [100, 100, 0, 0])
    trades_b = create_mock_trades(start, [0, 0, 100, 100])
    
    corr = calculate_correlation(trades_a, trades_b)
    assert -1.0 <= corr <= 1.0
