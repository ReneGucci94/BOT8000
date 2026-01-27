# tests/core/test_classifier.py
import pytest
from unittest.mock import MagicMock
from src.core.classifier import classify_regime
from src.core.regime import MarketRegime
from src.core.market import MarketState

def test_classify_high_volatility():
    """Prioridad 1: Alta volatilidad (ATR > 1.5 * Avg)."""
    state = MagicMock(spec=MarketState)
    state.atr = [2.0]
    state.atr_avg_14 = 1.0
    
    assert classify_regime(state) == MarketRegime.HIGH_VOLATILITY

def test_classify_trending_bullish():
    """Prioridad 2: Tendencia alcista (ADX > 25, EMAs bullish)."""
    state = MagicMock(spec=MarketState)
    state.atr = [1.0]
    state.atr_avg_14 = 1.0
    state.adx = 30.0
    state.ema_alignment = 'bullish'
    
    assert classify_regime(state) == MarketRegime.TRENDING_BULLISH

def test_classify_sideways_range():
    """Prioridad 3: Rango (ADX < 20)."""
    state = MagicMock(spec=MarketState)
    state.atr = [1.0]
    state.atr_avg_14 = 1.0
    state.adx = 15.0
    state.ema_alignment = 'neutral'
    
    assert classify_regime(state) == MarketRegime.SIDEWAYS_RANGE

def test_classify_breakout_pending():
    """Prioridad 4: Breakout Pending (Low Vol + Low ADX)."""
    state = MagicMock(spec=MarketState)
    state.atr = [0.5]
    state.atr_avg_14 = 1.0
    state.adx = 10.0
    
    assert classify_regime(state) == MarketRegime.BREAKOUT_PENDING
