import pytest
from decimal import Decimal
from dataclasses import FrozenInstanceError
from core.candle import Candle
from core.timeframe import Timeframe
from core.types import Price, Volume

def test_candle_valid_creation():
    """Verify we can create a valid candle."""
    c = Candle(
        timestamp=1000,
        open=Price("100.0"),
        high=Price("105.0"),
        low=Price("95.0"),
        close=Price("102.0"),
        volume=Volume("500.0"),
        timeframe=Timeframe.M5,
        complete=True
    )
    assert c.open == Decimal("100.0")
    assert c.complete is True

def test_candle_immutability():
    """Verify candle is immutable."""
    c = Candle(
        timestamp=1000,
        open=Price("100"), high=Price("102"), low=Price("98"), close=Price("101"),
        volume=Volume("100"), timeframe=Timeframe.M5
    )
    with pytest.raises(FrozenInstanceError):
        c.close = Price("200")  # type: ignore

def test_candle_invariants_high_low():
    """Verify high cannot be lower than low."""
    with pytest.raises(ValueError, match="High .* < Low"):
        Candle(
            timestamp=1000,
            open=Price("100"),
            high=Price("90"),  # Invalid: High < Low
            low=Price("95"),
            close=Price("100"),
            volume=Volume("100"),
            timeframe=Timeframe.M5
        )

def test_candle_invariants_volume():
    """Verify volume cannot be negative."""
    with pytest.raises(ValueError, match="Volume .* < 0"):
        Candle(
            timestamp=1000,
            open=Price("100"), high=Price("105"), low=Price("95"), close=Price("100"),
            volume=Volume("-1"), # Invalid
            timeframe=Timeframe.M5
        )

def test_candle_fail_fast_price_range():
    """Verify High must be >= max(Open, Close) and Low <= min(Open, Close)."""
    # This is a stricter TJR requirement: Candle wick rules
    
    # Case: High lower than Open
    with pytest.raises(ValueError):
        Candle(
            timestamp=1000,
            open=Price("100"), 
            high=Price("99"), # Invalid, Open is 100
            low=Price("90"), 
            close=Price("95"), 
            volume=Volume("100"), timeframe=Timeframe.M5
        )
