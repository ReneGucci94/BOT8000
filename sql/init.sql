-- sql/init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla principal de trades
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    trade_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    pair VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('LONG', 'SHORT')),
    
    -- Precios
    entry_price DECIMAL(20,8) NOT NULL,
    exit_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8) NOT NULL,
    take_profit DECIMAL(20,8) NOT NULL,
    
    -- Resultados
    result VARCHAR(10) CHECK (result IN ('WIN', 'LOSS', 'BREAKEVEN', 'OPEN')),
    profit_loss DECIMAL(20,8),
    profit_loss_pct DECIMAL(10,4),
    risk_reward DECIMAL(10,2),
    
    -- Market state (JSONB para features ML)
    market_state JSONB NOT NULL,
    
    -- Metadata
    strategy_version VARCHAR(50) NOT NULL,
    backtest_run_id UUID NOT NULL,
    worker_id VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_trades_pair_timeframe ON trades(pair, timeframe);
CREATE INDEX idx_trades_result ON trades(result);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_backtest_run ON trades(backtest_run_id);
CREATE INDEX idx_trades_market_state ON trades USING GIN(market_state);

-- Tabla de patrones detectados por ML
CREATE TABLE IF NOT EXISTS patterns (
    id SERIAL PRIMARY KEY,
    pattern_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    pattern_type VARCHAR(100) NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL,
    
    -- Métricas
    win_rate DECIMAL(5,2),
    avg_profit DECIMAL(20,8),
    sample_size INTEGER NOT NULL,
    confidence_score DECIMAL(5,2),
    
    -- Aplicabilidad
    applicable_pairs TEXT[],
    applicable_timeframes TEXT[],
    
    -- Metadata
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_validated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_active ON patterns(is_active);

-- Tabla de estrategias generadas
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    strategy_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    -- Configuración
    base_strategy VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    filters JSONB,
    
    -- Resultados de backtest
    backtest_results JSONB,
    
    -- Performance metrics
    total_trades INTEGER,
    win_rate DECIMAL(5,2),
    profit_factor DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    sharpe_ratio DECIMAL(10,4),
    
    -- Estado
    status VARCHAR(20) DEFAULT 'TESTING' CHECK (status IN ('TESTING', 'APPROVED', 'REJECTED', 'ARCHIVED')),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    tested_at TIMESTAMP,
    approved_at TIMESTAMP
);

CREATE INDEX idx_strategies_status ON strategies(status);
CREATE INDEX idx_strategies_base ON strategies(base_strategy);

-- Tabla de backtest runs
CREATE TABLE IF NOT EXISTS backtest_runs (
    id SERIAL PRIMARY KEY,
    run_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    config JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    
    -- Stats
    total_trades INTEGER DEFAULT 0,
    completed_trades INTEGER DEFAULT 0,
    failed_trades INTEGER DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Worker info
    workers JSONB
);

CREATE INDEX idx_backtest_runs_status ON backtest_runs(status);
CREATE INDEX idx_backtest_runs_started ON backtest_runs(started_at);

-- Tabla de logs de agentes
CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    log_level VARCHAR(10) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    context JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_agent ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_level ON agent_logs(log_level);
CREATE INDEX idx_agent_logs_timestamp ON agent_logs(timestamp DESC);
