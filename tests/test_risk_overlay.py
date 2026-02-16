import pytest
from decimal import Decimal
from src.execution.risk import RiskManager, RiskConfig

def test_risk_manager_initialization():
    config = RiskConfig(risk_percentage=Decimal("0.01"))
    rm = RiskManager(config)
    assert rm.config.risk_percentage == Decimal("0.01")

def test_portfolio_heat_limit():
    # Config with 5% max portfolio risk
    config = RiskConfig(
        risk_percentage=Decimal("0.01"),
        max_portfolio_risk=Decimal("0.05")
    )
    rm = RiskManager(config)
    
    account_balance = Decimal("10000")
    entry = Decimal("100")
    sl = Decimal("90") # 10 distance
    # Base risk = 10000 * 0.01 = 100.
    # Qty = 100 / 10 = 10.
    
    # Case 1: Low heat (0 open risk) -> Full size
    qty = rm.calculate_position_size(
        account_balance=account_balance,
        entry_price=entry,
        stop_loss=sl,
        current_open_risk=Decimal("0")
    )
    assert qty == Decimal("10")
    
    # Case 2: High heat (4.5% open risk). Remaining cap = 0.5%.
    # Base risk request = 1%. Should be capped at 0.5%.
    # Qty should be half (5).
    qty_capped = rm.calculate_position_size(
        account_balance=account_balance,
        entry_price=entry,
        stop_loss=sl,
        current_open_risk=Decimal("450") # 4.5% of 10000
    )
    assert qty_capped == Decimal("5")

def test_drawdown_scaling():
    # Config with DD scaling enabled
    config = RiskConfig(
        risk_percentage=Decimal("0.01"),
        use_dd_scaling=True
    )
    rm = RiskManager(config)
    
    account_balance = Decimal("10000")
    entry = Decimal("100")
    sl = Decimal("90")
    # Base risk = 100
    # Qty = 10
    
    # Case 1: 0% Drawdown -> Full size
    qty = rm.calculate_position_size(
        account_balance=account_balance,
        entry_price=entry,
        stop_loss=sl,
        current_drawdown_pct=0.0
    )
    assert qty == Decimal("10")
    
    # Case 2: 10% Drawdown -> Multiplier 0.8
    # Formula: 1.0 - (0.10 * 2) = 0.8
    qty_dd = rm.calculate_position_size(
        account_balance=account_balance,
        entry_price=entry,
        stop_loss=sl,
        current_drawdown_pct=0.10
    )
    assert qty_dd == Decimal("8")
    
    # Case 3: 50% Drawdown -> Multiplier 0.2 (Floor)
    # Formula: 1.0 - (0.50 * 2) = 0.0 -> Floor 0.5? Plan said 0.5 floor?
    # Actually plan said "Formula: multiplier = max(0.5, 1.0 - (drawdown * 2)) (Aggressive scaling)."
    # Wait, plan said `max(0.5, ...)`
    # So for 50% DD -> 1 - 1 = 0 -> use 0.5.
    
    # Let's check 20% DD -> 1 - 0.4 = 0.6.
    qty_dd_20 = rm.calculate_position_size(
        account_balance=account_balance,
        entry_price=entry,
        stop_loss=sl,
        current_drawdown_pct=0.20
    )
    assert qty_dd_20 == Decimal("6")
