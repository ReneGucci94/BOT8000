# tests/alphas/test_liquidity.py
import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from src.alphas.liquidity import Alpha_Liquidity
from src.core.market import MarketState

def test_liquidity_high_relative_volume():
    """Volumen alto relativo al promedio debe dar score positivo."""
    alpha = Alpha_Liquidity()
    state = MagicMock(spec=MarketState)
    
    # Mock H4 series with expanding volume
    # Mocking candles directly
    mock_candles = []
    for i in range(20):
        c = MagicMock()
        c.volume = Decimal("100")
        mock_candles.append(c)
    
    # Current candle with high volume
    curr = MagicMock()
    curr.volume = Decimal("300")
    mock_candles.append(curr)
    
    # Mock get_series to return a series with these candles
    series = MagicMock()
    series.__len__.return_value = len(mock_candles)
    series.get = lambda i: mock_candles[i]
    state.h4 = series
    
    score = alpha.get_score(state)
    assert score > 0

def test_liquidity_low_relative_volume():
    """Volumen bajo relativo al promedio debe dar score negativo."""
    alpha = Alpha_Liquidity()
    state = MagicMock(spec=MarketState)
    
    mock_candles = []
    for i in range(20):
        c = MagicMock()
        c.volume = Decimal("100")
        mock_candles.append(c)
    
    curr = MagicMock()
    curr.volume = Decimal("20")
    mock_candles.append(curr)
    
    series = MagicMock()
    series.__len__.return_value = len(mock_candles)
    series.get = lambda i: mock_candles[i]
    state.h4 = series
    
    score = alpha.get_score(state)
    assert score < 0
