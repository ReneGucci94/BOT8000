# src/database/repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, Float
import uuid

from src.database.models import Trade, Pattern, Strategy, BacktestRun, AgentLog

class TradeRepository:
    """Repository para operaciones CRUD de trades"""
    
    @staticmethod
    def create(db: Session, trade_data: Dict[str, Any]) -> Trade:
        """Crear nuevo trade"""
        trade = Trade(**trade_data)
        db.add(trade)
        db.flush()  # Get ID sin commit
        return trade
    
    @staticmethod
    def bulk_create(db: Session, trades_data: List[Dict[str, Any]]) -> List[Trade]:
        """Crear múltiples trades (optimizado)"""
        trades = [Trade(**data) for data in trades_data]
        db.bulk_save_objects(trades)
        db.flush()
        return trades
    
    @staticmethod
    def get_by_id(db: Session, trade_id: uuid.UUID) -> Optional[Trade]:
        """Obtener trade por ID"""
        return db.query(Trade).filter(Trade.trade_id == trade_id).first()
    
    @staticmethod
    def get_by_backtest_run(db: Session, run_id: uuid.UUID) -> List[Trade]:
        """Obtener todos los trades de un backtest run"""
        return db.query(Trade).filter(Trade.backtest_run_id == run_id).all()
    
    @staticmethod
    def get_losing_trades(
        db: Session, 
        pair: Optional[str] = None,
        timeframe: Optional[str] = None,
        limit: int = 1000
    ) -> List[Trade]:
        """Obtener trades perdedores con filtros opcionales"""
        query = db.query(Trade).filter(Trade.result == 'LOSS')
        
        if pair:
            query = query.filter(Trade.pair == pair)
        if timeframe:
            query = query.filter(Trade.timeframe == timeframe)
        
        return query.order_by(desc(Trade.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_winning_trades(
        db: Session,
        pair: Optional[str] = None,
        timeframe: Optional[str] = None,
        limit: int = 1000
    ) -> List[Trade]:
        """Obtener trades ganadores con filtros opcionales"""
        query = db.query(Trade).filter(Trade.result == 'WIN')
        
        if pair:
            query = query.filter(Trade.pair == pair)
        if timeframe:
            query = query.filter(Trade.timeframe == timeframe)
        
        return query.order_by(desc(Trade.timestamp)).limit(limit).all()
    
    @staticmethod
    def count_by_result(db: Session, backtest_run_id: uuid.UUID) -> Dict[str, int]:
        """Contar trades por resultado"""
        results = db.query(
            Trade.result,
            func.count(Trade.id)
        ).filter(
            Trade.backtest_run_id == backtest_run_id
        ).group_by(Trade.result).all()
        
        return {result: count for result, count in results}
    
    @staticmethod
    def get_trades_by_market_conditions(
        db: Session,
        volatility_min: Optional[float] = None,
        volatility_max: Optional[float] = None,
        volume_min: Optional[float] = None,
        limit: int = 1000
    ) -> List[Trade]:
        """Obtener trades filtrando por condiciones de mercado en JSONB"""
        query = db.query(Trade)
        
        if volatility_min is not None:
            query = query.filter(
                Trade.market_state['volatility'].astext.cast(Float) >= volatility_min
            )
        if volatility_max is not None:
            query = query.filter(
                Trade.market_state['volatility'].astext.cast(Float) <= volatility_max
            )
        if volume_min is not None:
            query = query.filter(
                Trade.market_state['volume'].astext.cast(Float) >= volume_min
            )
        
        return query.limit(limit).all()

class PatternRepository:
    """Repository para operaciones CRUD de patterns"""
    
    @staticmethod
    def create(db: Session, pattern_data: Dict[str, Any]) -> Pattern:
        """Crear nuevo pattern"""
        pattern = Pattern(**pattern_data)
        db.add(pattern)
        db.flush()
        return pattern
    
    @staticmethod
    def get_active_patterns(db: Session) -> List[Pattern]:
        """Obtener patterns activos"""
        return db.query(Pattern).filter(Pattern.is_active == True).all()
    
    @staticmethod
    def get_by_type(db: Session, pattern_type: str) -> List[Pattern]:
        """Obtener patterns por tipo"""
        return db.query(Pattern).filter(Pattern.pattern_type == pattern_type).all()
    
    @staticmethod
    def get_high_confidence(db: Session, min_confidence: float = 0.7) -> List[Pattern]:
        """Obtener patterns con alta confianza"""
        return db.query(Pattern).filter(
            Pattern.confidence_score >= min_confidence,
            Pattern.is_active == True
        ).order_by(desc(Pattern.confidence_score)).all()
    
    @staticmethod
    def deactivate(db: Session, pattern_id: uuid.UUID) -> bool:
        """Desactivar un pattern"""
        pattern = db.query(Pattern).filter(Pattern.pattern_id == pattern_id).first()
        if pattern:
            pattern.is_active = False
            db.flush()
            return True
        return False

class StrategyRepository:
    """Repository para operaciones CRUD de strategies"""
    
    @staticmethod
    def create(db: Session, strategy_data: Dict[str, Any]) -> Strategy:
        """Crear nueva estrategia"""
        strategy = Strategy(**strategy_data)
        db.add(strategy)
        db.flush()
        return strategy
    
    @staticmethod
    def get_by_status(db: Session, status: str) -> List[Strategy]:
        """Obtener estrategias por status"""
        return db.query(Strategy).filter(Strategy.status == status).all()
    
    @staticmethod
    def get_approved(db: Session, limit: int = 10) -> List[Strategy]:
        """Obtener estrategias aprobadas ordenadas por performance"""
        return db.query(Strategy).filter(
            Strategy.status == 'APPROVED'
        ).order_by(
            desc(Strategy.profit_factor)
        ).limit(limit).all()
    
    @staticmethod
    def update_backtest_results(
        db: Session,
        strategy_id: uuid.UUID,
        results: Dict[str, Any]
    ) -> Optional[Strategy]:
        """Actualizar resultados de backtest"""
        strategy = db.query(Strategy).filter(
            Strategy.strategy_id == strategy_id
        ).first()
        
        if strategy:
            strategy.backtest_results = results
            strategy.total_trades = results.get('total_trades')
            strategy.win_rate = results.get('win_rate')
            strategy.profit_factor = results.get('profit_factor')
            strategy.max_drawdown = results.get('max_drawdown')
            strategy.sharpe_ratio = results.get('sharpe_ratio')
            strategy.tested_at = datetime.utcnow()
            db.flush()
        
        return strategy
    
    @staticmethod
    def approve(db: Session, strategy_id: uuid.UUID) -> Optional[Strategy]:
        """Aprobar estrategia"""
        strategy = db.query(Strategy).filter(
            Strategy.strategy_id == strategy_id
        ).first()
        
        if strategy:
            strategy.status = 'APPROVED'
            strategy.approved_at = datetime.utcnow()
            db.flush()
        
        return strategy

class BacktestRunRepository:
    """Repository para operaciones CRUD de backtest runs"""
    
    @staticmethod
    def create(db: Session, config: Dict[str, Any]) -> BacktestRun:
        """Crear nuevo backtest run"""
        run = BacktestRun(
            run_id=uuid.uuid4(),
            config=config,
            status='RUNNING'
        )
        db.add(run)
        db.flush()
        return run
    
    @staticmethod
    def update_progress(
        db: Session,
        run_id: uuid.UUID,
        completed: int,
        failed: int
    ) -> Optional[BacktestRun]:
        """Actualizar progreso del run"""
        run = db.query(BacktestRun).filter(
            BacktestRun.run_id == run_id
        ).first()
        
        if run:
            run.completed_trades = completed
            run.failed_trades = failed
            db.flush()
        
        return run
    
    @staticmethod
    def complete(db: Session, run_id: uuid.UUID) -> Optional[BacktestRun]:
        """Marcar run como completado"""
        run = db.query(BacktestRun).filter(
            BacktestRun.run_id == run_id
        ).first()
        
        if run:
            run.status = 'COMPLETED'
            run.completed_at = datetime.utcnow()
            if run.started_at:
                duration = (run.completed_at - run.started_at).total_seconds()
                run.duration_seconds = int(duration)
            db.flush()
        
        return run
    
    @staticmethod
    def get_active(db: Session) -> List[BacktestRun]:
        """Obtener runs activos"""
        return db.query(BacktestRun).filter(
            BacktestRun.status == 'RUNNING'
        ).all()

class AgentLogRepository:
    """Repository para logs de agentes"""
    
    @staticmethod
    def log(
        db: Session,
        agent_name: str,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentLog:
        """Crear log entry"""
        log = AgentLog(
            agent_name=agent_name,
            log_level=level,
            message=message,
            context=context
        )
        db.add(log)
        db.flush()
        return log
    
    @staticmethod
    def get_by_agent(
        db: Session,
        agent_name: str,
        limit: int = 100
    ) -> List[AgentLog]:
        """Obtener logs de un agente"""
        return db.query(AgentLog).filter(
            AgentLog.agent_name == agent_name
        ).order_by(desc(AgentLog.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_errors(db: Session, limit: int = 100) -> List[AgentLog]:
        """Obtener logs de errores"""
        return db.query(AgentLog).filter(
            AgentLog.log_level.in_(['ERROR', 'CRITICAL'])
        ).order_by(desc(AgentLog.timestamp)).limit(limit).all()
