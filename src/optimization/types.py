from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from pathlib import Path

@dataclass(frozen=True)
class OptimizerConfig:
    timeframes: List[str]
    pairs: List[str]
    stop_losses: List[Decimal] # Fixed USD amount for SL (e.g. 500) or 0 for Structural
    take_profit_multiples: List[float]
    fee_rates: List[Decimal]
    initial_balance: Decimal
    risk_percent: Decimal
    data_path: str
    download_years: List[int]
    download_months: List[int]
    parallel: bool = True
    checkpoint_interval: int = 10

@dataclass(frozen=True)
class TestConfig:
    id: str
    timeframe: str
    pair: str
    stop_loss: Decimal
    take_profit_r: float
    fee_rate: Decimal

@dataclass(frozen=True)
class BacktestResult:
    config_id: str
    timeframe: str
    pair: str
    stop_loss: Decimal
    take_profit_r: float
    fee_rate: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    gross_profit: Decimal
    gross_loss: Decimal
    fees_paid: Decimal
    net_profit: Decimal
    max_drawdown: Decimal
    execution_time: float
