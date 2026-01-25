# tests/alphas/test_ob_quality.py
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from src.alphas.ob_quality import Alpha_OB_Quality
from src.strategy.ob import OrderBlock, OBType
from src.core.market import MarketState

def test_ob_quality_bullish_score():
    """Verificar que un OB alcista produce un score positivo."""
    alpha = Alpha_OB_Quality()
    state = MagicMock(spec=MarketState)
    state.h4 = MagicMock()
    state.h4.__len__.return_value = 100
    
    mock_ob = OrderBlock(
        type=OBType.BULLISH,
        top=Decimal("41000"),
        bottom=Decimal("40000"),
        index=95
    )
    
    with patch('src.alphas.ob_quality.detect_ob', return_value=mock_ob):
        score = alpha.get_score(state)
        assert 0 < score <= 1.0

def test_ob_quality_bearish_score():
    """Verificar que un OB bajista produce un score negativo."""
    alpha = Alpha_OB_Quality()
    state = MagicMock(spec=MarketState)
    state.h4 = MagicMock()
    state.h4.__len__.return_value = 100
    
    mock_ob = OrderBlock(
        type=OBType.BEARISH,
        top=Decimal("41000"),
        bottom=Decimal("40000"),
        index=95
    )
    
    with patch('src.alphas.ob_quality.detect_ob', return_value=mock_ob):
        score = alpha.get_score(state)
        assert -1.0 <= score < 0

def test_ob_quality_no_ob_score():
    """Verificar que si no hay OB el score es zero."""
    alpha = Alpha_OB_Quality()
    state = MagicMock(spec=MarketState)
    state.h4 = MagicMock()
    state.h4.__len__.return_value = 100
    
    with patch('src.alphas.ob_quality.detect_ob', return_value=None):
        score = alpha.get_score(state)
        assert score == 0.0
