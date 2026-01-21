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
