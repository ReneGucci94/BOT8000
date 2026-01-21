import pytest
from decimal import Decimal
from core.timeframe import Timeframe
from core.candle import Candle
from core.series import MarketSeries
from strategy.fvg import detect_fvg, FVG, FVGType

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

def test_detect_bullish_fvg():
    """
    Bullish FVG: Candle 1 High < Candle 3 Low.
    Gap exists between 100 and 102.
    """
    # 1: High 100
    c1 = create_candle(90, 95, 100, 85)
    # 2: Big green candle
    c2 = create_candle(95, 105, 108, 95)
    # 3: Low 102
    c3 = create_candle(105, 110, 115, 102)
    
    series = MarketSeries([c1, c2, c3])
    
    # Analyze window ending at index 2 (c3)
    fvg = detect_fvg(series, 2)
    
    assert fvg is not None
    assert fvg.type == FVGType.BULLISH
    assert fvg.top == Decimal("102")   # c3.low
    assert fvg.bottom == Decimal("100") # c1.high

def test_no_fvg_overlap():
    """
    Overlap: Candle 1 High >= Candle 3 Low.
    C1 High: 100. C3 Low: 99. No Gap.
    """
    c1 = create_candle(90, 95, 100, 85)
    c2 = create_candle(95, 100, 105, 95)
    c3 = create_candle(100, 105, 110, 99) # Low 99 touches 100
    
    series = MarketSeries([c1, c2, c3])
    
    fvg = detect_fvg(series, 2)
    assert fvg is None

def test_detect_bearish_fvg():
    """
    Bearish FVG: Candle 1 Low > Candle 3 High.
    Gap between 100 (C1 Low) and 98 (C3 High).
    """
    # 1: Low 100
    c1 = create_candle(110, 105, 112, 100)
    # 2: Big red
    c2 = create_candle(105, 95, 105, 90)
    # 3: High 98
    c3 = create_candle(95, 90, 98, 85)
    
    series = MarketSeries([c1, c2, c3])
    
    fvg = detect_fvg(series, 2)
    
    assert fvg is not None
    assert fvg.type == FVGType.BEARISH
    assert fvg.top == Decimal("100")  # c1.low
    assert fvg.bottom == Decimal("98") # c3.high
