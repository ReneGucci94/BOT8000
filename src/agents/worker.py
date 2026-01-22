# src/agents/worker.py
from typing import Dict, Any, List, Optional
from pathlib import Path
from decimal import Decimal
import uuid
from datetime import datetime
import statistics

from src.agents.base import BaseAgent
from src.database import get_db_session
from src.database.repository import TradeRepository, BacktestRunRepository
from src.utils.data_loader import load_binance_csv
from src.strategy.engine import TJRStrategy
from src.simulation.broker import InMemoryBroker
from src.execution.risk import RiskManager
from src.execution.executor import TradeExecutor
from src.core.market import MarketState
from src.core.timeframe import Timeframe

class OptimizerWorker(BaseAgent):
    """
    Worker individual que corre backtests para un par/timeframe
    
    Guarda cada trade en DB con market_state completo
    """
    
    def __init__(self, worker_id: str):
        super().__init__(f"Worker-{worker_id}")
        self.worker_id = worker_id
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar backtest y guardar trades en DB
        """
        pair = config['pair']
        timeframe_str = config['timeframe']
        timeframe = Timeframe(timeframe_str)
        year = config['year']
        months = config.get('months', list(range(1, 13)))
        backtest_run_id = config['backtest_run_id']
        
        self.log('INFO', f"Starting backtest for {pair} {timeframe_str} {year}")
        
        # Load all candles for the year
        all_candles = []
        data_dir = Path("data/raw")
        
        for month in months:
            filename = f"{pair}-{timeframe_str}-{year}-{month:02d}.csv"
            filepath = data_dir / filename
            
            if not filepath.exists():
                self.log('WARNING', f"File not found: {filename}")
                continue
            
            try:
                candles = load_binance_csv(str(filepath), timeframe)
                all_candles.extend(candles)
            except Exception as e:
                self.log('ERROR', f"Failed to load {filename}: {str(e)}")
        
        if not all_candles:
            raise ValueError(f"No data found for {pair} {timeframe_str} {year}")
        
        total_candles = len(all_candles)
        self.log('INFO', f"Total candles to process: {total_candles}")
        
        # Initialize trading components
        strategy = TJRStrategy(
            fixed_stop_loss=Decimal(str(config['stop_loss'])),
            take_profit_multiplier=Decimal(str(config['take_profit_multiplier']))
        )
        
        broker = InMemoryBroker(
            balance=Decimal(str(config['initial_balance'])),
            fee_rate=Decimal(str(config['fee_rate']))
        )
        
        risk_manager = RiskManager(
            risk_percent=Decimal(str(config['risk_per_trade_pct']))
        )
        
        executor = TradeExecutor(
            broker=broker,
            risk_manager=risk_manager,
            strategy=strategy
        )
        
        market = MarketState.empty(pair)
        trades_saved = 0
        
        for i, candle in enumerate(all_candles):
            # Update market state
            market = market.update(candle)
            
            # Execute worker logic (Update broker -> Analysis -> Execution)
            executor.process_candle(candle, market, timeframe)
            
            # Check for completed trades (new implementation in broker)
            closed_positions = broker.get_closed_positions()
            
            if len(closed_positions) > trades_saved:
                # Save new closed positions to DB
                with get_db_session() as db:
                    for position in closed_positions[trades_saved:]:
                        # Extract market state features
                        # Use last 50 candles for context
                        context_candles = all_candles[max(0, i-50):i]
                        market_state_features = self._extract_market_state(
                            candle,
                            context_candles
                        )
                        
                        trade_data = {
                            # Realistically, the timestamp of entry is better, but here we use candle.timestamp for simplicity
                            'timestamp': datetime.fromtimestamp(candle.timestamp / 1000),
                            'pair': pair,
                            'timeframe': timeframe_str,
                            'side': position.side.value,
                            'entry_price': position.entry_price,
                            'exit_price': position.exit_price,
                            'stop_loss': position.stop_loss,
                            'take_profit': position.take_profit,
                            'result': 'WIN' if position.pnl > 0 else 'LOSS',
                            'profit_loss': position.pnl,
                            'profit_loss_pct': (position.pnl / (position.entry_price * position.quantity) * 100) if position.entry_price > 0 else 0,
                            'risk_reward': float(config['take_profit_multiplier']),
                            'market_state': market_state_features,
                            'strategy_version': 'TJR_ML_v3_Worker',
                            'backtest_run_id': backtest_run_id,
                            'worker_id': self.worker_id
                        }
                        
                        TradeRepository.create(db, trade_data)
                        trades_saved += 1
            
            # Update progress every 500 candles
            if i % 500 == 0:
                self.update_progress(
                    i,
                    total_candles,
                    f"Processed {i}/{total_candles} candles, {trades_saved} trades"
                )
        
        # Final stats
        final_balance = broker.get_balance()
        total_trades = len(closed_positions)
        winning_trades = sum(1 for p in closed_positions if p.pnl > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(p.pnl for p in closed_positions if p.pnl > 0)
        total_loss = abs(sum(p.pnl for p in closed_positions if p.pnl < 0))
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
        
        result = {
            'pair': pair,
            'timeframe': timeframe_str,
            'year': year,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'final_balance': float(final_balance),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(float(profit_factor), 2),
            'trades_saved_to_db': trades_saved
        }
        
        self.log('INFO', f"Backtest completed: {total_trades} trades, win rate {win_rate:.2f}%")
        
        return result
    
    def _extract_market_state(self, current_candle, historical_candles: List) -> Dict[str, Any]:
        """
        Extraer features de market state para ML
        """
        if not historical_candles:
            return {'error': 'no_historical_data'}
        
        # Price features
        closes = [float(c.close) for c in historical_candles]
        highs = [float(c.high) for c in historical_candles]
        lows = [float(c.low) for c in historical_candles]
        volumes = [float(c.volume) for c in historical_candles]
        
        current_price = float(current_candle.close)
        
        # Volatility (ATR approximation)
        price_ranges = [h - l for h, l in zip(highs, lows)]
        atr = statistics.mean(price_ranges[-14:]) if len(price_ranges) >= 14 else 0
        volatility = (atr / current_price) if current_price > 0 else 0
        
        # Volume analysis
        avg_volume = statistics.mean(volumes)
        current_volume = float(current_candle.volume)
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Trend
        if len(closes) >= 20:
            sma_20 = statistics.mean(closes[-20:])
            trend = 'bullish' if current_price > sma_20 else 'bearish'
        else:
            trend = 'unknown'
        
        # Price change
        if len(closes) >= 2:
            price_change = (closes[-1] - closes[-2]) / closes[-2] * 100
        else:
            price_change = 0
        
        return {
            'price': current_price,
            'atr': round(atr, 4),
            'volatility': round(volatility, 4),
            'volume': current_volume,
            'avg_volume': round(avg_volume, 2),
            'volume_ratio': round(volume_ratio, 2),
            'trend': trend,
            'price_change_pct': round(price_change, 2),
            'candles_in_history': len(historical_candles)
        }
