# tests/agents/test_alpha_integration.py
import pytest
from unittest.mock import MagicMock, patch
from src.agents.worker import OptimizerWorker
from decimal import Decimal

def test_worker_uses_alpha_engine_when_flag_active():
    """Verificar que el worker usa el Alpha Engine si el flag está activo."""
    worker = OptimizerWorker("integration-test")
    
    # Config con flag activo
    config = {
        'pair': 'BTCUSDT',
        'timeframe': '4h',
        'year': 2024,
        'months': [1],
        'backtest_run_id': '00000000-0000-0000-0000-000000000000',
        'stop_loss': 2000,
        'take_profit_multiplier': 2.0,
        'initial_balance': 10000,
        'fee_rate': 0.001,
        'risk_per_trade_pct': 1.0,
        'use_ml_model': False,
        'use_alpha_engine': True  # ACTIVADO
    }
    
    # Mock de componentes para evitar ejecución real
    mock_candle = MagicMock()
    mock_candle.timestamp = 1704067200000.0
    mock_candle.close = Decimal("40000")
    mock_candle.volume = Decimal("100")
    
    with patch('src.agents.worker.load_binance_csv', return_value=[mock_candle]):
        with patch('src.agents.worker.Path.exists', return_value=True):
            with patch('src.agents.worker.AlphaCombiner') as mock_combiner_cls:
                mock_combiner = mock_combiner_cls.return_value
                mock_combiner.get_signal.return_value = None # No trade for now
                
                # Mock de persistencia para evitar errores de DB
                with patch('src.agents.worker.TradeRepository.create'):
                    worker.run(config)
                    
                    # Verificar que se instanció el Combiner
                    assert mock_combiner_cls.called
                    # Verificar que se llamó a get_signal
                    assert mock_combiner.get_signal.called

def test_worker_uses_legacy_when_flag_inactive():
    """Verificar que el worker usa TJRStrategy legacy si el flag está inactivo."""
    worker = OptimizerWorker("legacy-test")
    
    config = {
        'pair': 'BTCUSDT',
        'timeframe': '4h',
        'year': 2024,
        'months': [1],
        'backtest_run_id': '00000000-0000-0000-0000-000000000000',
        'stop_loss': 2000,
        'take_profit_multiplier': 2.0,
        'initial_balance': 10000,
        'fee_rate': 0.001,
        'risk_per_trade_pct': 1.0,
        'use_ml_model': False,
        'use_alpha_engine': False  # INACTIVO (Default)
    }
    
    mock_candle = MagicMock()
    mock_candle.timestamp = 1704067200000.0
    mock_candle.close = Decimal("40000")
    mock_candle.volume = Decimal("100")
    
    with patch('src.agents.worker.load_binance_csv', return_value=[mock_candle]):
        with patch('src.agents.worker.Path.exists', return_value=True):
            with patch('src.agents.worker.TJRStrategy') as mock_strat_cls:
                mock_strat = mock_strat_cls.return_value
                # IMPORTANTE: El mock de analyze debe retornar None para evitar el flujo de ejecución
                mock_strat.analyze.return_value = None 
                
                with patch('src.agents.worker.AlphaCombiner') as mock_combiner_cls:
                    mock_comp = mock_combiner_cls.return_value
                    mock_comp.get_signal.return_value = None
                    
                    with patch('src.agents.worker.TradeRepository.create'):
                        worker.run(config)
                        
                        # Verificar que llamó a TJRStrategy.analyze
                        assert mock_strat.analyze.called
                        # Verificar que NO se usó el AlphaCombiner para señales
                        # (Notese que el worker lo instancia en el setup pero no debe llamar get_signal)
                        assert not mock_comp.get_signal.called
