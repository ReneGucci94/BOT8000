# tests/alphas/test_volatility.py
import pytest
from unittest.mock import MagicMock
from src.alphas.volatility import Alpha_Volatility
from src.core.market import MarketState

def test_volatility_expansion_score():
    """Alta volatilidad (ATR > Promedio) debe dar score positivo."""
    alpha = Alpha_Volatility()
    state = MagicMock(spec=MarketState)
    # Simulamos ATR expanding: actual=2.0, promedio=1.0
    state.atr = [1.0] * 20 + [2.0]
    
    score = alpha.get_score(state)
    assert score > 0

def test_volatility_contraction_score():
    """Baja volatilidad (ATR < Promedio) debe dar score negativo."""
    alpha = Alpha_Volatility()
    state = MagicMock(spec=MarketState)
    # Simulamos ATR contracting: actual=0.5, promedio=1.0
    state.atr = [1.0] * 20 + [0.5]
    
    score = alpha.get_score(state)
    assert score < 0

def test_volatility_neutral_score():
    """Volatilidad promedio debe dar score cercano a cero."""
    alpha = Alpha_Volatility()
    state = MagicMock(spec=MarketState)
    state.atr = [1.0] * 21
    
    score = alpha.get_score(state)
    assert abs(score) < 0.1
