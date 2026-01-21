import pytest
from decimal import Decimal
from core.timeframe import Timeframe
from core.candle import Candle
from core.series import MarketSeries
from strategy.fractals import is_valid_low, is_valid_high
from strategy.structure import detect_bos, StructureType
from strategy.fvg import detect_fvg, FVGType
from strategy.ob import detect_ob, OBType

def create_candle(open_p, close_p, high_p, low_p, timestamp=1000) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=Decimal(str(open_p)),
        close=Decimal(str(close_p)),
        high=Decimal(str(high_p)),
        low=Decimal(str(low_p)),
        volume=Decimal("100"),
        timeframe=Timeframe.M5
    )

def test_tjr_strategy_confluence_scenario():
    """
    Simulate a perfect TJR Long Setup:
    1. Swing High established (Liquidty target).
    2. Swing Low established.
    3. Price dumps to Sweep the Low (Liquidity Grab).
    4. Price reverses strongly, creating an OB.
    5. Price creates a FVG during expansion.
    6. Price breaks the Swing High (BOS).
    
    We verify detection of all these elements at the BOS moment.
    """
    series = MarketSeries([])
    ts = 1000
    
    # 1. Establish Range (High at 105, Low at 100)
    # Candle 0: Low 99.
    # Candle 1: High 105 (Swing High).
    # Candle 2: Low 100 (Swing Low). 
    c0 = create_candle(101, 102, 103, 99, ts); ts+=60 # Low 99 (start fractal)
    c1 = create_candle(102, 104, 105, 101, ts); ts+=60 # High 105 (Green)
    c2 = create_candle(104, 101, 104, 100, ts); ts+=60 # Low 100 (Red)
    
    series = series.add(c0).add(c1).add(c2)
    
    # Verify Fractals
    # Index 1 is High? (Green i, Red i+1? Need i+1).
    # Index 2 is Low? (Red i, Green i+1? Need next).
    
    # 2. Sweep Logic (Target Low 99 from c0, or maybe Low 100 from c2?)
    # TJR: Sweep of *valid* swing.
    # We need index 0 to be a valid swing low.
    # c0 is Green or Red? 101->102 (Green).
    # For Valid Low we need Red->Green.
    # Let's adjust c0 to be a Valid Low (Red->Green).
    # We need a candle BEFORE c0.
    
    # New Scenario Design:
    series = MarketSeries([])
    ts = 1000
    
    # Setup Pre-Liquidity
    # C-1: Red (To form low with C0)
    c_pre = create_candle(102, 100, 103, 99, ts); ts+=60 # Low 99
    # C0: Green (Forms LOW at C-1? No, Red->Green means Low is at Red, so C-1 is Low 99)
    c0 = create_candle(100, 103, 104, 100, ts); ts+=60 
    
    # C1: High 105 Setup
    # C1 Green
    c1 = create_candle(103, 105, 105, 102, ts); ts+=60
    # C2 Red (Forms HIGH at C1, High 105)
    c2 = create_candle(105, 102, 105, 101, ts); ts+=60
    
    series = series.add(c_pre).add(c0).add(c1).add(c2)
    
    # Assert Intermediate State
    # Is Valid Low at index 0? (c_pre=Red, c0=Green). Yes. Low=99.
    assert is_valid_low(series, 0) is True
    # Is Valid High at index 2? (c1=Green, c2=Red). Yes. High=105.
    assert is_valid_high(series, 2) is True
    
    # 3. Sweep Phase
    # Price needs to go below 99 (The valid low).
    # C3: Big Red dumping to 98 (Sweep).
    # This C3 is the OB candidate (Last Red before move).
    c3 = create_candle(102, 98, 103, 97, ts); ts+=60 # Close 98, Low 97.
    series = series.add(c3)
    
    # 4. Expansion Phase & FVG
    # C4: Big Green. 98 -> 104.
    # Gap check: Prev candle (C2) High was 105? No wait, FVG is Candle i-2 vs i.
    # Setup for FVG:
    # C3 (OB): High 103.
    # C4: Big Green. Range 97-104.
    # C5: Another Green breaking out. Low > C3 High?
    c4 = create_candle(98, 104, 104, 98, ts); ts+=60
    
    # 5. BOS Phase
    # Break High 105.
    # C5: Green. 104 -> 108. Low 104.
    # FVG Check: C3 High (103) vs C5 Low (104). GAP! 103-104.
    c5 = create_candle(104, 108, 110, 104, ts); ts+=60
    
    series = series.add(c4).add(c5)
    
    # 6. Verify Strategy Points at C5 (index 6, if 0-based... pre,0,1,2,3,4,5 -> len 7. Index 6.)
    current_idx = 6
    
    # A. Verify BOS
    # Did we break High 105 (from index 2)?
    # C5 Close 108 > 105. Yes.
    bos = detect_bos(series, current_idx)
    assert bos is not None
    assert bos.type == StructureType.BOS_BULLISH
    assert bos.price == Decimal("105")
    
    # B. Verify FVG
    # Created by C3, C4, C5 sequence? (Indices 4, 5, 6)
    # C3 High 103. C5 Low 104. Gap 103-104.
    fvg = detect_fvg(series, current_idx)
    assert fvg is not None
    assert fvg.type == FVGType.BULLISH
    assert fvg.bottom == Decimal("103")
    assert fvg.top == Decimal("104")
    
    # C. Verify Order Block
    # Should find C3 (Index 4) as OB.
    # Requires: BOS (Yes), Sweep (97 < 99, Yes).
    ob = detect_ob(series, current_idx)
    assert ob is not None
    assert ob.type == OBType.BULLISH
    assert ob.index == 4 # C3
    assert ob.bottom == Decimal("97")
    
    print("\nStrategy Confluence Verified: 1.Valid Low/High -> 2.Sweep -> 3.OB -> 4.FVG -> 5.BOS")
