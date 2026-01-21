import pytest
from decimal import Decimal
from core.timeframe import Timeframe
from core.candle import Candle
from core.series import MarketSeries
from strategy.structure import detect_bos, StructureEvent, StructureType

def create_candle(open_p, close_p, high_p, low_p, timestamp=100) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=Decimal(str(open_p)),
        close=Decimal(str(close_p)),
        high=Decimal(str(high_p)),
        low=Decimal(str(low_p)),
        volume=Decimal("100"),
        timeframe=Timeframe.M5
    )

def test_detect_bullish_bos():
    """
    Setup: Valid High at 110.
    Trigger: Candle body closes > 110.
    """
    # 0: Green (High 110)
    c1 = create_candle(100, 105, 110, 90, timestamp=1000)
    # 1: Red (Validates high)
    c2 = create_candle(105, 100, 108, 95, timestamp=2000)
    # 2: Green Breakout Candle (Close 112 > 110)
    c3 = create_candle(100, 112, 115, 98, timestamp=3000)
    
    series = MarketSeries([c1, c2, c3])
    
    # Check index 2 (The breakout candle)
    event = detect_bos(series, 2)
    
    assert event is not None
    assert event.type == StructureType.BOS_BULLISH
    assert event.price == Decimal("110") # The broken level
    assert event.broken_index == 0 # Index of the high that was broken

def test_detect_no_bos_wick_only():
    """
    Setup: High at 110.
    Trigger: Candle Wick goes to 112, but Close is 109. NO BOS.
    """
    c1 = create_candle(100, 105, 110, 90, 1000)
    c2 = create_candle(105, 100, 108, 95, 2000)
    c3 = create_candle(100, 109, 112, 98, 3000) # Close < 110
    
    series = MarketSeries([c1, c2, c3])
    
    event = detect_bos(series, 2)
    assert event is None

def test_detect_bearish_bos():
    """
    Setup: Valid Low at 90.
    Trigger: Candle body closes < 90.
    """
    # 0: Red (Low 90)
    c1 = create_candle(100, 95, 102, 90, 1000) 
    # 1: Green (Validates low)
    c2 = create_candle(95, 98, 100, 92, 2000)
    # 2: Red Breakdown (Close 88 < 90)
    c3 = create_candle(98, 88, 99, 85, 3000)
    
    series = MarketSeries([c1, c2, c3])
    
    event = detect_bos(series, 2)
    assert event is not None
    assert event.type == StructureType.BOS_BEARISH
    assert event.price == Decimal("90")
    assert event.broken_index == 0
