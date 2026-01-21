import pytest
from decimal import Decimal
from simulation.backtest import Backtester, BacktestReport
from execution.broker import OrderSide

def test_backtest_report_calculations():
    # Mock data: 3 trades (2 wins, 1 loss)
    # Win 1: +100
    # Win 2: +200
    # Loss 1: -150
    equity_curve = [
        Decimal("10000"), 
        Decimal("10100"), 
        Decimal("10300"), 
        Decimal("10150")
    ]
    
    report = Backtester.calculate_report(
        initial_balance=Decimal("10000"),
        equity_curve=equity_curve,
        total_trades=3
    )
    
    assert report.total_trades == 3
    assert report.net_profit == Decimal("150")
    assert report.win_rate == pytest.approx(66.66, rel=0.01)
    assert report.max_drawdown >= Decimal("150") # From 10300 to 10150
