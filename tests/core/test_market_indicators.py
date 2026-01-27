# tests/core/test_market_indicators.py
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from src.core.market import MarketState
from src.core.series import MarketSeries

def test_market_state_adx_lazy():
    """Verificar que el ADX es lazy and cached."""
    series = MarketSeries([])
    state = MarketState("BTCUSDT", series, series, series, series)
    
    with patch('src.core.market.calculate_adx', return_value=30.0) as mock_adx:
        # First call
        assert state.adx == 30.0
        assert mock_adx.call_count == 1
        
        # Subsequent call
        assert state.adx == 30.0
        assert mock_adx.call_count == 1

def test_market_state_ema_alignment_bullish():
    """Verificar alineación alcista."""
    series = MarketSeries([])
    state = MarketState("BTCUSDT", series, series, series, series)
    
    # Mocking calculate_ema to simulate Bullish (EMA 20 > EMA 50)
    with patch('src.core.market.calculate_ema', side_effect=[100.0, 90.0]):
        assert state.ema_alignment == 'bullish'

def test_market_state_ema_alignment_bearish():
    """Verificar alineación bajista."""
    series = MarketSeries([])
    state = MarketState("BTCUSDT", series, series, series, series)
    
    # Mocking calculate_ema to simulate Bearish (EMA 20 < EMA 50)
    with patch('src.core.market.calculate_ema', side_effect=[90.0, 100.0]):
        assert state.ema_alignment == 'bearish'
