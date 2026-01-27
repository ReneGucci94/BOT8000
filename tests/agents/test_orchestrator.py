# tests/agents/test_orchestrator.py
import pytest
from unittest.mock import MagicMock, patch
from src.agents.orchestrator import MSCOrchestrator
from src.core.regime import MarketRegime
from src.core.market import MarketState
from src.execution.executor import TradeSignal
from src.execution.broker import OrderSide

def test_orchestrator_selects_specialist():
    """Verificar que el orquestador delega al agente correcto."""
    orch = MSCOrchestrator()
    state = MagicMock(spec=MarketState)
    state.timestamp = 123456789
    
    # Mockeamos el clasificador para que retorne TRENDING_BULLISH
    with patch('src.agents.orchestrator.classify_regime', return_value=MarketRegime.TRENDING_BULLISH):
        # Mockeamos el TrendHunterAgent dentro del orquestador
        mock_agent = MagicMock()
        mock_signal = TradeSignal("BTCUSDT", OrderSide.BUY, 40000, 38000, 44000)
        mock_agent.generate_signal.return_value = mock_signal
        
        orch.agents[MarketRegime.TRENDING_BULLISH] = mock_agent
        
        signal = orch.get_signal(state)
        
        assert signal == mock_signal
        # Verificar metadata inyectada
        assert signal.metadata['agent'] == 'MagicMock' # O el nombre del mock
        assert signal.metadata['regime'] == 'trending_bullish'

def test_orchestrator_sideways_default():
    """Verificar que usa MeanReversion en Sideways."""
    orch = MSCOrchestrator()
    state = MagicMock(spec=MarketState)
    
    with patch('src.agents.orchestrator.classify_regime', return_value=MarketRegime.SIDEWAYS_RANGE):
        with patch.object(orch.agents[MarketRegime.SIDEWAYS_RANGE], 'generate_signal', return_value=None) as mock_gen:
            signal = orch.get_signal(state)
            assert signal is None
            assert mock_gen.called
