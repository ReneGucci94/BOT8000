# tests/test_orchestrator.py
import pytest
import uuid

from src.agents.orchestrator import OrchestratorAgent

@pytest.fixture
def mock_agents(monkeypatch):
    class MockAgent:
        def __init__(self, *args, **kwargs): pass
        def execute(self, config):
            if "Data" in str(self.__class__): return {'status': 'ok'}
            if "Optimizer" in str(self.__class__): return {'backtest_run_id': uuid.uuid4()}
            if "Pattern" in str(self.__class__): return {'patterns_found': 2}
            if "Mutator" in str(self.__class__): return {'count': 3}
            if "Validator" in str(self.__class__): return {'approved_count': 1, 'results': []}
            return {}

    monkeypatch.setattr('src.agents.orchestrator.DataAgent', type('DataAgent', (MockAgent,), {}))
    monkeypatch.setattr('src.agents.orchestrator.OptimizerSwarm', type('OptimizerSwarm', (MockAgent,), {}))
    monkeypatch.setattr('src.agents.orchestrator.PatternDetective', type('PatternDetective', (MockAgent,), {}))
    monkeypatch.setattr('src.agents.orchestrator.StrategyMutator', type('StrategyMutator', (MockAgent,), {}))
    monkeypatch.setattr('src.agents.orchestrator.ValidatorAgent', type('ValidatorAgent', (MockAgent,), {}))

def test_orchestrator_run(mock_agents):
    agent = OrchestratorAgent()
    config = {
        'pairs': ['BTCUSDT'],
        'years': [2024],
        'train_months': [1],
        'val_months': [2],
        'num_mutations': 1
    }
    
    result = agent.execute(config)
    
    assert result['patterns_found'] == 2
    assert result['mutations_created'] == 3
    assert result['approved_strategies'] == 1
    assert 'backtest_run_id' in result
