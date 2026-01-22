# tests/test_repository.py
import pytest
from datetime import datetime
from decimal import Decimal
import uuid

from src.database import get_db_session, init_db
from src.database.repository import (
    TradeRepository,
    PatternRepository,
    StrategyRepository,
    BacktestRunRepository,
    AgentLogRepository
)

@pytest.fixture(scope="module")
def setup_db():
    """Setup DB para tests"""
    init_db()
    yield
    # Cleanup si necesario

def test_trade_repository_create(setup_db):
    """Test crear trade"""
    with get_db_session() as db:
        trade_data = {
            'timestamp': datetime.utcnow(),
            'pair': 'BTCUSDT',
            'timeframe': '4h',
            'side': 'LONG',
            'entry_price': Decimal('96000.00'),
            'exit_price': Decimal('98000.00'),
            'stop_loss': Decimal('95000.00'),
            'take_profit': Decimal('100000.00'),
            'result': 'WIN',
            'profit_loss': Decimal('2000.00'),
            'profit_loss_pct': Decimal('2.08'),
            'risk_reward': Decimal('2.0'),
            'market_state': {
                'volatility': 0.5,
                'volume': 1500,
                'trend': 'bullish'
            },
            'strategy_version': 'TJR_v2.0',
            'backtest_run_id': uuid.uuid4()
        }
        
        trade = TradeRepository.create(db, trade_data)
        
        assert trade.id is not None
        assert trade.pair == 'BTCUSDT'
        assert trade.result == 'WIN'
        assert trade.market_state['volatility'] == 0.5

def test_trade_repository_get_losing_trades(setup_db):
    """Test obtener trades perdedores"""
    with get_db_session() as db:
        # Crear algunos trades de prueba
        run_id = uuid.uuid4()
        
        for i in range(5):
            TradeRepository.create(db, {
                'timestamp': datetime.utcnow(),
                'pair': 'ETHUSDT',
                'timeframe': '1d',
                'side': 'SHORT',
                'entry_price': Decimal('3000.00'),
                'exit_price': Decimal('3100.00'),
                'stop_loss': Decimal('3050.00'),
                'take_profit': Decimal('2900.00'),
                'result': 'LOSS',
                'profit_loss': Decimal('-100.00'),
                'market_state': {'test': True},
                'strategy_version': 'TJR_v2.0',
                'backtest_run_id': run_id
            })
        
        losing = TradeRepository.get_losing_trades(db, pair='ETHUSDT')
        
        assert len(losing) >= 5
        assert all(t.result == 'LOSS' for t in losing)
        assert all(t.pair == 'ETHUSDT' for t in losing)

def test_pattern_repository_create(setup_db):
    """Test crear pattern"""
    with get_db_session() as db:
        pattern_data = {
            'pattern_type': 'high_volatility_loss',
            'description': 'Trades perdedores con alta volatilidad',
            'conditions': {
                'volatility': {'min': 0.7},
                'volume': {'max': 1000}
            },
            'win_rate': Decimal('20.5'),
            'sample_size': 150,
            'confidence_score': Decimal('0.85'),
            'applicable_pairs': ['BTCUSDT', 'ETHUSDT'],
            'applicable_timeframes': ['4h', '1d']
        }
        
        pattern = PatternRepository.create(db, pattern_data)
        
        assert pattern.id is not None
        assert pattern.pattern_type == 'high_volatility_loss'
        assert pattern.is_active == True

def test_strategy_repository_create_and_approve(setup_db):
    """Test crear y aprobar estrategia"""
    with get_db_session() as db:
        strategy_data = {
            'name': 'TJR_ML_Enhanced_v1',
            'description': 'TJR con filtros ML',
            'base_strategy': 'TJR',
            'parameters': {
                'stop_loss': 2000,
                'risk_reward': 2.5
            },
            'filters': {
                'skip_high_volatility': True,
                'min_volume': 1000
            }
        }
        
        strategy = StrategyRepository.create(db, strategy_data)
        assert strategy.status == 'TESTING'
        
        # Actualizar resultados
        results = {
            'total_trades': 100,
            'win_rate': 55.5,
            'profit_factor': 1.85,
            'max_drawdown': 0.08,
            'sharpe_ratio': 1.5
        }
        
        strategy = StrategyRepository.update_backtest_results(
            db, strategy.strategy_id, results
        )
        assert strategy.win_rate == Decimal('55.5')
        
        # Aprobar
        strategy = StrategyRepository.approve(db, strategy.strategy_id)
        assert strategy.status == 'APPROVED'

def test_backtest_run_lifecycle(setup_db):
    """Test ciclo de vida de backtest run"""
    with get_db_session() as db:
        config = {
            'pairs': ['BTCUSDT'],
            'timeframes': ['4h'],
            'years': [2024]
        }
        
        # Crear
        run = BacktestRunRepository.create(db, config)
        assert run.status == 'RUNNING'
        
        # Actualizar progreso
        run = BacktestRunRepository.update_progress(db, run.run_id, 50, 2)
        assert run.completed_trades == 50
        assert run.failed_trades == 2
        
        # Completar
        run = BacktestRunRepository.complete(db, run.run_id)
        assert run.status == 'COMPLETED'
        assert run.completed_at is not None
