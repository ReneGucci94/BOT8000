import pytest
from core.candle import Candle
from core.series import MarketSeries
from core.timeframe import Timeframe
from core.types import Price, Volume

def create_candle(ts: int, complete: bool = True) -> Candle:
    return Candle(
        timestamp=ts,
        open=Price("100"), high=Price("110"), low=Price("90"), close=Price("105"),
        volume=Volume("100"),
        timeframe=Timeframe.M5,
        complete=complete
    )

def test_series_creation_and_sorting():
    """Verify series stores candles and auto-sorts them."""
    c1 = create_candle(1000)
    c2 = create_candle(2000)
    c3 = create_candle(3000)
    
    # Pass unsorted
    series = MarketSeries([c2, c1, c3])
    
    # Should be sorted by timestamp
    assert series.candles[0] == c1
    assert series.candles[1] == c2
    assert series.candles[2] == c3
    assert len(series) == 3

def test_series_immutability_on_add():
    """Verify add() returns a NEW instance and leaves original untouched."""
    c1 = create_candle(1000)
    s1 = MarketSeries([c1])
    
    c2 = create_candle(2000)
    s2 = s1.add(c2)
    
    # s2 has both
    assert len(s2) == 2
    assert s2.candles[1] == c2
    
    # s1 STILL has only 1 (immutability check)
    assert len(s1) == 1
    assert s1.candles[0] == c1
    assert s1 is not s2

def test_series_get_last_closed():
    """Verify we can get the last completed candle."""
    c1 = create_candle(1000, complete=True)
    c2 = create_candle(2000, complete=False) # Open candle
    
    series = MarketSeries([c1, c2])
    
    assert series.current == c2  # Latest (even if open)
    assert series.last_closed == c1 # Latest complete

def test_series_empty_access():
    """Verify behavior on empty series."""
    series = MarketSeries([])
    assert len(series) == 0
    with pytest.raises(IndexError):
        _ = series.current
