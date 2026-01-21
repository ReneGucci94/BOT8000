from decimal import Decimal
from core.candle import Candle
from core.series import MarketSeries
from core.timeframe import Timeframe
from core.types import Price, Volume

def test_core_architecture_flow():
    """
    Integration test verifying that:
    1. We can create Types
    2. We can create Candles with those Types
    3. We can store Candles in MarketSeries
    4. Immutability is preserved throughout
    """
    
    # 1. Primitives
    p1 = Price("1.0500")
    p2 = Price("1.0600")
    
    # 2. Timeframe
    tf = Timeframe.H1
    assert tf.value == "1h"
    
    # 3. Candle Creation
    c1 = Candle(
        timestamp=1000, 
        open=p1, high=p2, low=p1, close=p1, 
        volume=Volume("100"), 
        timeframe=tf, 
        complete=True
    )
    
    # 4. Series Creation
    series_v1 = MarketSeries([c1])
    assert series_v1.current == c1
    
    # 5. Evolution (Add new candle)
    c2 = Candle(
        timestamp=2000,
        open=p1, high=p2, low=p1, close=p2,
        volume=Volume("200"),
        timeframe=tf,
        complete=False
    )
    
    series_v2 = series_v1.add(c2)
    
    # 6. Verify State
    assert len(series_v1) == 1
    assert len(series_v2) == 2
    assert series_v2.last_closed == c1  # c2 is incomplete
    assert series_v2.current == c2
    
    print("Architecture Integration Verified: Types -> Candle -> Series OK")
