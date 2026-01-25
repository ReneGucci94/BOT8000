# src/database/models.py
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Numeric, 
    Boolean, Text, CheckConstraint, Index, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    pair = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)
    
    # Prices
    entry_price = Column(Numeric(20, 8), nullable=False)
    exit_price = Column(Numeric(20, 8))
    stop_loss = Column(Numeric(20, 8), nullable=False)
    take_profit = Column(Numeric(20, 8), nullable=False)
    
    # Results
    result = Column(String(10))
    profit_loss = Column(Numeric(20, 8))
    profit_loss_pct = Column(Numeric(10, 4))
    risk_reward = Column(Numeric(10, 2))
    
    # Market state
    market_state = Column(JSONB, nullable=False)
    
    # Metadata
    strategy_version = Column(String(50), nullable=False)
    backtest_run_id = Column(UUID(as_uuid=True), nullable=False)
    worker_id = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("side IN ('LONG', 'SHORT')", name='check_side'),
        CheckConstraint("result IN ('WIN', 'LOSS', 'BREAKEVEN', 'OPEN')", name='check_result'),
        Index('idx_trades_pair_timeframe', 'pair', 'timeframe'),
        Index('idx_trades_result', 'result'),
        Index('idx_trades_timestamp', 'timestamp'),
        Index('idx_trades_backtest_run', 'backtest_run_id'),
        Index('idx_trades_market_state', 'market_state', postgresql_using='gin'),
    )

class Pattern(Base):
    __tablename__ = 'patterns'
    
    id = Column(Integer, primary_key=True)
    pattern_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    pattern_type = Column(String(100), nullable=False)
    description = Column(Text)
    conditions = Column(JSONB, nullable=False)
    
    # Metrics
    win_rate = Column(Numeric(5, 2))
    avg_profit = Column(Numeric(20, 8))
    sample_size = Column(Integer, nullable=False)
    confidence_score = Column(Numeric(5, 2))
    
    # Applicability
    applicable_pairs = Column(ARRAY(String))
    applicable_timeframes = Column(ARRAY(String))
    
    # Metadata
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_validated_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_patterns_type', 'pattern_type'),
        Index('idx_patterns_active', 'is_active'),
    )

class Strategy(Base):
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Configuration
    base_strategy = Column(String(50), nullable=False)
    parameters = Column(JSONB, nullable=False)
    filters = Column(JSONB)
    
    # Backtest results
    backtest_results = Column(JSONB)
    
    # Performance metrics
    total_trades = Column(Integer)
    win_rate = Column(Numeric(5, 2))
    profit_factor = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    
    # Status
    status = Column(String(20), default='TESTING')
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    tested_at = Column(DateTime)
    approved_at = Column(DateTime)
    
    __table_args__ = (
        CheckConstraint("status IN ('TESTING', 'APPROVED', 'REJECTED', 'ARCHIVED')", name='check_status'),
        Index('idx_strategies_status', 'status'),
        Index('idx_strategies_base', 'base_strategy'),
    )

class BacktestRun(Base):
    __tablename__ = 'backtest_runs'
    
    id = Column(Integer, primary_key=True)
    run_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    config = Column(JSONB, nullable=False)
    status = Column(String(20), default='RUNNING')
    
    # Stats
    total_trades = Column(Integer, default=0)
    completed_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Worker info
    workers = Column(JSONB)
    
    __table_args__ = (
        CheckConstraint("status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')", name='check_status'),
        Index('idx_backtest_runs_status', 'status'),
        Index('idx_backtest_runs_started', 'started_at'),
    )

class AgentLog(Base):
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50), nullable=False)
    log_level = Column(String(10), nullable=False)
    message = Column(Text, nullable=False)
    context = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name='check_log_level'),
        Index('idx_agent_logs_agent', 'agent_name'),
        Index('idx_agent_logs_level', 'log_level'),
        Index('idx_agent_logs_timestamp', 'timestamp'),
    )
