# tests/test_validator.py
import pytest
from decimal import Decimal
import uuid

from src.agents.validator import ValidatorAgent
from src.database import get_db_session, init_db
from src.database.repository import StrategyRepository

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    yield

def test_validator_run(setup_db, monkeypatch):
    # 1. Crear una estrategia TESTING en la DB
    strategy_id = uuid.uuid4()
    strat_name = f'Validator_Test_Strategy_{uuid.uuid4().hex[:6]}'
    with get_db_session() as db:
        StrategyRepository.create(db, {
            'strategy_id': strategy_id,
            'name': strat_name,
            'base_strategy': 'TJR',
            'parameters': {'stop_loss': 2000, 'take_profit_multiplier': 2.0},
            'status': 'TESTING'
        })
        
    # 2. Mockear OptimizerWorker para que devuelva un resultado exitoso
    class MockWorker:
        def __init__(self, name): pass
        def execute(self, config):
            return {
                'profit_factor': 2.5,
                'win_rate': 60.0,
                'total_trades': 10
            }
            
    monkeypatch.setattr('src.agents.validator.OptimizerWorker', MockWorker)
    
    agent = ValidatorAgent()
    config = {
        'validation_period': {'year': 2024, 'months': [1]},
        'criteria': {'min_profit_factor': 1.2, 'min_win_rate': 45.0}
    }
    
    result = agent.execute(config)
    
    assert result['approved_count'] == 1
    
    # 3. Verificar status en DB
    with get_db_session() as db:
        strat = StrategyRepository.get_by_status(db, 'APPROVED')
        assert any(s.strategy_id == strategy_id for s in strat)
