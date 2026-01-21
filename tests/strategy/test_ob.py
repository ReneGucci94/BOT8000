import pytest
from decimal import Decimal
from core.timeframe import Timeframe
from core.candle import Candle
from core.series import MarketSeries
from strategy.ob import detect_ob, OrderBlock, OBType

def create_candle(open_p, close_p, high_p, low_p, timestamp) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=Decimal(str(open_p)),
        close=Decimal(str(close_p)),
        high=Decimal(str(high_p)),
        low=Decimal(str(low_p)),
        volume=Decimal("100"),
        timeframe=Timeframe.M5
    )

def test_detect_bullish_ob_with_sweep_and_bos():
    """
    Scenario:
    1. Valid Swing Low at 100 (Liquidity).
    2. Price sweeps to 98 (Taking liquidity).
    3. Price reverses and breaks structure (BOS) at 105.
    4. The OB is the last RED candle before the move up started.
    """
    series = MarketSeries([])
    
    # 0. Swing Low setup
    # Green then Red then Green (Fractal Low at 100)
    series = series.add(create_candle(102, 100, 103, 99, 1000)) # Low 99 (Index 0)
    series = series.add(create_candle(100, 102, 103, 100, 2000)) # Green
    
    # 1. Sweep Phase
    # Candle going down to Sweep 99
    # This candle IS the OB candidate (Last Red)
    ob_candle = create_candle(102, 98, 103, 97, 3000) # Red. Low 97 < 99. SWEEP!
    series = series.add(ob_candle)
    
    # 2. Reversal / Expansion
    # Green candle starting move up
    series = series.add(create_candle(98, 103, 104, 98, 4000)) 
    
    # 3. BOS Phase
    # Need to break a recent High. Let's say high was at 103 (Index 0 High).
    # Current high is 104. Close is 103. NOT BOS YET if High was 103.
    # Let's add another big green candle closing above 103.
    series = series.add(create_candle(103, 110, 112, 103, 5000)) # Close 110 > 103 BOS!
    
    # Now we scan at index 4 (the BOS candle)
    # The function should look back and find the OB.
    ob = detect_ob(series, 4)
    
    assert ob is not None
    assert ob.type == OBType.BULLISH
    assert ob.top == Decimal("103") # High of OB candle
    assert ob.bottom == Decimal("97") # Low of OB candle
    assert ob.index == 2 # Index of ob_candle

def test_invalid_ob_no_sweep():
    """
    Scenario: BOS happens, but no previous low was swept.
    Just a Higher Low formation.
    """
    series = MarketSeries([])
    # Uptrending HL
    series = series.add(create_candle(100, 105, 106, 99, 1000)) # Low 99
    series = series.add(create_candle(105, 102, 106, 101, 2000)) # Retrace Low 101 (HL)
    series = series.add(create_candle(102, 110, 112, 102, 3000)) # Breakout BOS
    
    ob = detect_ob(series, 2)
    assert ob is None # No OB because no liquidity sweep occurred before this move
