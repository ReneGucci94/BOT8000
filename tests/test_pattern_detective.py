# tests/test_pattern_detective.py
import pytest
from decimal import Decimal
import uuid
from datetime import datetime
import pandas as pd

from src.agents.pattern_detective import PatternDetective
from src.database import get_db_session, init_db
from src.database.repository import TradeRepository, PatternRepository

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    yield

def test_pattern_detective_run(setup_db):
    """Test que el detective encuentra patrones en datos sesgados."""
    run_id = uuid.uuid4()
    
    with get_db_session() as db:
        # Generar trades artificiales: 
        # Si volatilidad > 0.8 -> LOSS (100% de las veces)
        # Si volatilidad <= 0.8 -> WIN (100% de las veces)
        for i in range(50):
            vol = 0.9 if i < 25 else 0.1
            res = 'LOSS' if vol > 0.8 else 'WIN'
            
            TradeRepository.create(db, {
                'timestamp': datetime.utcnow(),
                'pair': 'BTCUSDT',
                'timeframe': '1h',
                'side': 'LONG',
                'entry_price': Decimal("50000"),
                'exit_price': Decimal("51000"),
                'stop_loss': Decimal("49000"),
                'take_profit': Decimal("52000"),
                'result': res,
                'market_state': {'volatility': vol, 'volume': 1000},
                'strategy_version': 'test',
                'backtest_run_id': run_id
            })
            
    agent = PatternDetective()
    config = {
        'backtest_run_id': str(run_id),
        'min_sample_size': 10,
        'max_win_rate_threshold': 20.0
    }
    
    result = agent.execute(config)
    
    assert result['patterns_found'] >= 1
    assert result['total_trades_analyzed'] == 50
    
    # Verificar que el patrón guardado tenga sentido
    with get_db_session() as db:
        patterns = PatternRepository.get_active_patterns(db)
        # Debería haber un patrón indicando alta volatilidad = riesgo
        assert any("volatility > 0.8" in str(p.conditions) or "volatility > 0.5" in str(p.conditions) for p in patterns)
        assert any(float(p.win_rate) < 10.0 for p in patterns)
