# tests/core/test_market_cache.py
import pytest
from unittest.mock import MagicMock, patch
from src.core.market import MarketState
from src.core.series import MarketSeries

def test_market_state_cache_lazy_calculation():
    """Verificar que los indicadores calculados se guardan en cache y no se recalculan."""
    series = MarketSeries([])
    state = MarketState("BTCUSDT", series, series, series, series)
    
    # Necesitamos mockear una función de cálculo que aún no existe o que el state usará
    with patch('src.core.market.calculate_rsi', return_value=[50.0]) as mock_calc:
        # Primera llamada: debe calcular
        res1 = state.rsi
        assert res1 == [50.0]
        assert mock_calc.call_count == 1
        
        # Segunda llamada: debe retornar del cache
        res2 = state.rsi
        assert res2 == [50.0]
        assert mock_calc.call_count == 1  # No se debe haber llamado de nuevo
