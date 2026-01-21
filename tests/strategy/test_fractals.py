import pytest
from decimal import Decimal
from core.timeframe import Timeframe
from core.candle import Candle
from core.series import MarketSeries
# Strategy module import will fail initially
from strategy.fractals import is_valid_high, is_valid_low

def create_candle(open_p, close_p, high_p, low_p, timestamp=100) -> Candle:
    """Helper to create minimal valid candles."""
    return Candle(
        timestamp=timestamp,
        open=Decimal(str(open_p)),
        close=Decimal(str(close_p)),
        high=Decimal(str(high_p)),
        low=Decimal(str(low_p)),
        volume=Decimal("100"),
        timeframe=Timeframe.M5
    )

def test_valid_high_green_red():
    """
    TJR Valid High: Green Candle -> Red Candle.
    High is likely the green one, but strict def is pattern.
    Actually TJR def: Green Candle followed by Red Candle.
    The 'high' is the green candle's high. 
    (Assuming we check the pattern at the GREEN candle's index)
    Wait, logic: if I am at index i (Green), checks i+1 (Red).
    """
    # 0: Green
    c1 = create_candle(100, 105, 110, 90) # Green
    # 1: Red
    c2 = create_candle(105, 100, 108, 95) # Red
    
    series = MarketSeries([c1, c2])
    
    # Check at index 0 (The Green Candle)
    assert is_valid_high(series, 0) is True

def test_invalid_high_green_green():
    """Green -> Green is NOT a valid high pattern start."""
    c1 = create_candle(100, 105, 110, 90) # Green
    c2 = create_candle(105, 108, 112, 104) # Green
    
    series = MarketSeries([c1, c2])
    assert is_valid_high(series, 0) is False

def test_valid_low_red_green():
    """
    TJR Valid Low: Red Candle -> Green Candle.
    """
    # 0: Red
    c1 = create_candle(100, 90, 102, 80) # Red
    # 1: Green
    c2 = create_candle(90, 95, 98, 85) # Green
    
    series = MarketSeries([c1, c2])
    assert is_valid_low(series, 0) is True

def test_invalid_low_red_red():
    """Red -> Red is NOT a valid low pattern."""
    c1 = create_candle(100, 90, 102, 80) # Red
    c2 = create_candle(90, 85, 92, 70) # Red
    
    series = MarketSeries([c1, c2])
    assert is_valid_low(series, 0) is False

def test_fractal_out_of_bounds():
    """Check handling of last candle (can't determine next)."""
    c1 = create_candle(100, 105, 110, 90)
    series = MarketSeries([c1])
    
    assert is_valid_high(series, 0) is False
    assert is_valid_low(series, 0) is False
