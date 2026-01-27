# tests/agents/test_trading_agent_base.py
import pytest
from unittest.mock import MagicMock
from src.agents.trading_agent import TradingAgent
from src.core.regime import MarketRegime
from src.core.market import MarketState

def test_trading_agent_should_activate():
    """Verificar lógica de activación por régimen."""
    class MockAgent(TradingAgent):
        pass
    
    # Agente que solo se activa en TRENDING_BULLISH
    agent = MockAgent(alpha_weights={}, active_regimes=[MarketRegime.TRENDING_BULLISH])
    
    assert agent.should_activate(MarketRegime.TRENDING_BULLISH) is True
    assert agent.should_activate(MarketRegime.SIDEWAYS_RANGE) is False

def test_trading_agent_generate_signal_calls_combiner():
    """Verificar que generate_signal delega al combiner."""
    class MockAgent(TradingAgent):
        pass
    
    agent = MockAgent(alpha_weights={}, active_regimes=[])
    # Mockeamos el combiner interno
    agent.combiner = MagicMock()
    mock_signal = MagicMock()
    agent.combiner.get_signal.return_value = mock_signal
    
    state = MagicMock(spec=MarketState)
    signal = agent.generate_signal(state)
    
    assert signal == mock_signal
    # Verificar que usó el threshold default (0.6)
    agent.combiner.get_signal.assert_called_with(state, threshold=0.6)
