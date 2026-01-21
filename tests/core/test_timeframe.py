import pytest
from core.timeframe import Timeframe

def test_timeframe_values():
    """Verify Timeframe enum has required TJR values."""
    assert Timeframe.M5.value == "5m"
    assert Timeframe.M15.value == "15m"
    assert Timeframe.H1.value == "1h"
    assert Timeframe.H4.value == "4h"

def test_timeframe_from_string():
    """Verify we can create Timeframe from string."""
    assert Timeframe("5m") == Timeframe.M5
    assert Timeframe("4h") == Timeframe.H4
    
    with pytest.raises(ValueError):
        Timeframe("invalid")
