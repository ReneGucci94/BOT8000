# tests/test_strategy_mutator.py
import pytest
from decimal import Decimal
import uuid

from src.agents.strategy_mutator import StrategyMutator
from src.database import get_db_session, init_db
from src.database.repository import PatternRepository, StrategyRepository

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    yield

def test_strategy_mutator_run(setup_db):
    # 1. Crear un patrón en la DB para que el mutator lo use
    with get_db_session() as db:
        PatternRepository.create(db, {
            'pattern_type': 'test_risk',
            'description': 'High volatility risk',
            'conditions': ['volatility > 0.8'],
            'win_rate': Decimal("10.0"),
            'sample_size': 50,
            'is_active': True
        })
        
    agent = StrategyMutator()
    config = {
        'base_strategy_name': 'TJR_Base',
        'num_mutations': 2,
        'apply_ml_filters': True,
        'initial_params': {
            'stop_loss': 2000,
            'take_profit_multiplier': 2.0
        }
    }
    
    result = agent.execute(config)
    
    assert result['count'] == 2
    assert len(result['mutations_created']) == 2
    
    # 2. Verificar que se grabaron en la DB
    with get_db_session() as db:
        strategies = StrategyRepository.get_by_status(db, 'TESTING')
        assert len(strategies) >= 2
        
        # Verificar que al menos una tenga filtros ML
        has_ml_filter = any(s.filters and 'ml_avoidance' in s.filters for s in strategies)
        assert has_ml_filter
