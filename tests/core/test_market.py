import pytest
from core.market import MarketState
from core.series import MarketSeries
from core.timeframe import Timeframe

def test_market_state_initialization():
    """Verify MarketState requires all timeframe series."""
    # Create empty series for testing
    empty_series = MarketSeries([])
    
    state = MarketState(
        symbol="BTCUSDT",
        m5=empty_series,
        m15=empty_series,
        h1=empty_series,
        h4=empty_series
    )
    
    assert state.symbol == "BTCUSDT"
    assert isinstance(state.m5, MarketSeries)
    assert isinstance(state.h4, MarketSeries)

def test_market_state_empty_factory():
    """Verify convenience factory for empty state."""
    state = MarketState.empty("ETHUSDT")
    
    assert state.symbol == "ETHUSDT"
    assert len(state.m5) == 0
    assert len(state.h4) == 0
    
def test_market_state_immutability():
    """Verify fields cannot be reassigned."""
    state = MarketState.empty("SOLUSDT")
    with pytest.raises(Exception): # Frozen dataclass raises specific error
        state.symbol = "INVALID" # type: ignore

def test_market_state_update():
    """Verify update returns new state with correct series updated."""
    from core.candle import Candle
    from core.types import Timestamp, Price, Volume
    
    # Create dummy candle
    c_m5 = Candle(
        timestamp=1000,
        open=Price(100), high=Price(110), low=Price(90), close=Price(105),
        volume=Volume(100), timeframe=Timeframe.M5
    )
    
    state = MarketState.empty("BTC")
    new_state = state.update(c_m5)
    
    # Verify original state unchanged
    assert len(state.m5) == 0
    
    # Verify new state updated
    assert len(new_state.m5) == 1
    assert new_state.m5.current == c_m5
    
    # Verify other timeframes untouched
    assert len(new_state.h1) == 0

def test_market_state_update_different_timeframes():
    """Verify updates route to correct timeframe series."""
    from core.candle import Candle
    from core.types import Timestamp, Price, Volume
    
    state = MarketState.empty("ETH")
    
    # M5 Update
    c_m5 = Candle(
        timestamp=100, open=Price(1), high=Price(2), low=Price(0), close=Price(1),
        volume=Volume(10), timeframe=Timeframe.M5
    )
    state = state.update(c_m5)
    
    # H1 Update
    c_h1 = Candle(
        timestamp=100, open=Price(1), high=Price(2), low=Price(0), close=Price(1),
        volume=Volume(10), timeframe=Timeframe.H1
    )
    state = state.update(c_h1)
    
    assert len(state.m5) == 1
    assert len(state.h1) == 1
    assert len(state.m15) == 0

