# tests/alphas/test_ml_confidence.py
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.alphas.ml_confidence import Alpha_ML_Confidence
from src.core.market import MarketState

def test_ml_confidence_high_prob_score():
    """Alta probabilidad del modelo debe dar score positivo."""
    # Mock del analyzer
    mock_analyzer = MagicMock()
    mock_analyzer.predict_proba.return_value = 0.8  # 80% win prob
    
    alpha = Alpha_ML_Confidence(analyzer=mock_analyzer)
    state = MagicMock(spec=MarketState)
    state.h4 = MagicMock()
    # Mock length >= 50
    state.h4.__len__.return_value = 100
    
    # Mock del extractor para evitar calculos reales en tests unitarios
    with patch('src.alphas.ml_confidence.FeatureExtractor') as mock_ext_cls:
        mock_ext = mock_ext_cls.return_value
        mock_ext.add_all_features.return_value = pd.DataFrame({'f1': [1]})
        
        score = alpha.get_score(state)
        # (0.8 - 0.5) * 2 = 0.6
        assert score == pytest.approx(0.6)

def test_ml_confidence_low_prob_score():
    """Baja probabilidad del modelo debe dar score negativo."""
    mock_analyzer = MagicMock()
    mock_analyzer.predict_proba.return_value = 0.2  # 20% win prob
    
    alpha = Alpha_ML_Confidence(analyzer=mock_analyzer)
    state = MagicMock(spec=MarketState)
    state.h4 = MagicMock()
    state.h4.__len__.return_value = 100
    
    with patch('src.alphas.ml_confidence.FeatureExtractor') as mock_ext_cls:
        mock_ext = mock_ext_cls.return_value
        mock_ext.add_all_features.return_value = pd.DataFrame({'f1': [1]})
        
        score = alpha.get_score(state)
        # (0.2 - 0.5) * 2 = -0.6
        assert score == pytest.approx(-0.6)

def test_ml_confidence_neutral_score():
    """Probabilidad balanceada (0.5) debe dar score cero."""
    mock_analyzer = MagicMock()
    mock_analyzer.predict_proba.return_value = 0.5
    
    alpha = Alpha_ML_Confidence(analyzer=mock_analyzer)
    state = MagicMock(spec=MarketState)
    state.h4 = MagicMock()
    state.h4.__len__.return_value = 100
    
    with patch('src.alphas.ml_confidence.FeatureExtractor') as mock_ext_cls:
        mock_ext = mock_ext_cls.return_value
        mock_ext.add_all_features.return_value = pd.DataFrame({'f1': [1]})
        
        score = alpha.get_score(state)
        assert score == 0.0
