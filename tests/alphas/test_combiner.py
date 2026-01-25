# tests/alphas/test_combiner.py
import pytest
from unittest.mock import MagicMock
from src.alphas.combiner import AlphaCombiner
from src.core.market import MarketState
from src.execution.executor import TradeSignal

def test_combiner_aggregate_score():
    """Verificar suma ponderada de scores."""
    alpha1 = MagicMock()
    alpha1.get_score.return_value = 0.5
    
    alpha2 = MagicMock()
    alpha2.get_score.return_value = 1.0
    
    # Combiner con pesos 1.0 y 2.0
    combiner = AlphaCombiner([
        (alpha1, 1.0),
        (alpha2, 2.0)
    ])
    
    state = MagicMock(spec=MarketState)
    score = combiner.get_aggregate_score(state)
    
    # expected = (0.5 * 1.0 + 1.0 * 2.0) / (1.0 + 2.0) = 2.5 / 3.0 = 0.8333
    assert score == pytest.approx(0.8333, abs=0.0001)

def test_combiner_get_signal_long():
    """Verificar que genera señal LONG si supera threshold."""
    alpha = MagicMock()
    alpha.get_score.return_value = 0.8
    
    combiner = AlphaCombiner([(alpha, 1.0)])
    state = MagicMock(spec=MarketState)
    state.symbol = "BTCUSDT"
    
    signal = combiner.get_signal(state, threshold=0.6)
    
    assert signal is not None
    assert signal.side.value == 'BUY'
    # Confidence is the score
    assert signal.confidence == 0.8

def test_combiner_get_signal_short():
    """Verificar que genera señal SHORT si es inferior a -threshold."""
    alpha = MagicMock()
    alpha.get_score.return_value = -0.7
    
    combiner = AlphaCombiner([(alpha, 1.0)])
    state = MagicMock(spec=MarketState)
    state.symbol = "BTCUSDT"
    
    signal = combiner.get_signal(state, threshold=0.6)
    
    assert signal is not None
    assert signal.side.value == 'SELL'
    assert signal.confidence == 0.7

def test_combiner_no_signal_below_threshold():
    """Verificar que no genera señal si el score es bajo."""
    alpha = MagicMock()
    alpha.get_score.return_value = 0.3
    
    combiner = AlphaCombiner([(alpha, 1.0)])
    state = MagicMock(spec=MarketState)
    
    signal = combiner.get_signal(state, threshold=0.6)
    assert signal is None
