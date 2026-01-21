import pytest
from decimal import Decimal
from execution.risk import RiskManager, RiskConfig

def test_position_sizing_calculation():
    """
    Scenario:
    Balance: 10,000
    Risk: 1% ($100)
    Entry: 50,000
    SL: 49,000 (Diff 1,000)
    
    Expected Qty = Risk ($100) / Diff ($1000) = 0.1
    """
    config = RiskConfig(risk_percentage=Decimal("0.01"))
    manager = RiskManager(config)
    
    qty = manager.calculate_position_size(
        account_balance=Decimal("10000"),
        entry_price=Decimal("50000"),
        stop_loss=Decimal("49000")
    )
    
    assert qty == Decimal("0.1")

def test_position_sizing_short():
    """
    Scenario Short:
    Balance: 10,000
    Risk: 1% ($100)
    Entry: 50,000
    SL: 51,000 (Diff 1,000)
    
    Expected Qty = 100 / 1000 = 0.1 (Absolute value)
    """
    config = RiskConfig(risk_percentage=Decimal("0.01"))
    manager = RiskManager(config)
    
    qty = manager.calculate_position_size(
        account_balance=Decimal("10000"),
        entry_price=Decimal("50000"),
        stop_loss=Decimal("51000")
    )
    
    assert qty == Decimal("0.1")

def test_zero_division_protection():
    """Entry == SL should raise ValueError or return 0."""
    config = RiskConfig(risk_percentage=Decimal("0.01"))
    manager = RiskManager(config)
    
    with pytest.raises(ValueError, match="Stop Loss cannot be equal to Entry"):
        manager.calculate_position_size(
            account_balance=Decimal("10000"),
            entry_price=Decimal("50000"),
            stop_loss=Decimal("50000")
        )

def test_min_lot_size():
    """
    If calculated size < min_lot, return 0? Or min_lot?
    Risk Manager implies strict risk control. 
    If we can't afford the trade risk-wise (size too small for precision?), usually return 0.
    But let's assume we just return the raw calculation for now, maybe rounded.
    Let's check precision.
    """
    # Risk $100. Diff $100,000 (Bitcoin mooning?). Qty = 0.001.
    pass
