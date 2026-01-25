# tests/alphas/test_momentum.py
import pytest
from unittest.mock import MagicMock, patch
from src.alphas.momentum import Alpha_Momentum
from src.core.market import MarketState

def test_momentum_bullish_score():
    """RSI alto debe dar score positivo."""
    alpha = Alpha_Momentum()
    state = MagicMock(spec=MarketState)
    # Simulamos RSI > 50 (alcista)
    state.rsi = [65.0]
    
    score = alpha.get_score(state)
    assert 0 < score <= 1.0

def test_momentum_bearish_score():
    """RSI bajo debe dar score negativo."""
    alpha = Alpha_Momentum()
    state = MagicMock(spec=MarketState)
    # Simulamos RSI < 50 (bajista)
    state.rsi = [35.0]
    
    score = alpha.get_score(state)
    assert -1.0 <= score < 0

def test_momentum_neutral_score():
    """RSI cerca de 50 debe dar score cercano a cero."""
    alpha = Alpha_Momentum()
    state = MagicMock(spec=MarketState)
    state.rsi = [50.0]
    
    score = alpha.get_score(state)
    assert abs(score) < 0.1
