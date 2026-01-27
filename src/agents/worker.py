# src/agents/worker.py
from typing import Dict, Any, List, Optional
from pathlib import Path
from decimal import Decimal
import uuid
from datetime import datetime
import statistics
import pandas as pd
import numpy as np

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
from src.ml.features import FeatureExtractor
from src.ml.analyzer import PatternAnalyzer

# Alphas
from src.alphas.ob_quality import Alpha_OB_Quality
from src.alphas.momentum import Alpha_Momentum
from src.alphas.volatility import Alpha_Volatility
from src.alphas.ml_confidence import Alpha_ML_Confidence
from src.alphas.liquidity import Alpha_Liquidity
from src.alphas.combiner import AlphaCombiner
from src.agents.orchestrator import MSCOrchestrator

class OptimizerWorker(BaseAgent):
    """
    Worker individual que corre backtests para un par/timeframe
    
    Guarda cada trade en DB con market_state completo
    """
    
    def __init__(self, worker_id: str):
        super().__init__(f"Worker-{worker_id}")
        self.worker_id = worker_id
        self.feature_extractor = FeatureExtractor()
        self._combiner: Optional[AlphaCombiner] = None
    
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
        
        # ML Config
        use_ml = config.get('use_ml_model', False)
        ml_model_path = config.get('ml_model_path', 'data/models/rf_model_v1.pkl')
        ml_threshold = config.get('ml_prob_threshold', 0.6)
        
        analyzer = None
        if use_ml:
            analyzer = PatternAnalyzer(ml_model_path)
            if not analyzer.is_trained:
                self.log('WARNING', "ML Model requested but no trained model found. Running without ML.")
                analyzer = None # Fallback
            else:
                self.log('INFO', f"Running with ML Filter (Threshold: {ml_threshold})")
        
        # Alpha Engine Setup (Task 6.9)
        use_alpha_engine = config.get('use_alpha_engine', False)
        if use_alpha_engine:
            self.log('INFO', "Alpha Engine active for signal generation")
            # Iniciar alphas con los pesos definidos por el usuario
            self._combiner = AlphaCombiner([
                (Alpha_OB_Quality(), 1.5),
                (Alpha_Momentum(), 2.0),
                (Alpha_Volatility(), 0.5),
                (Alpha_ML_Confidence(analyzer=analyzer), 1.0),
                (Alpha_Liquidity(), 0.8)
            ])
        
        # MSC Orchestrator Setup (Task 8.5)
        use_msc = config.get('use_msc', False)
        orchestrator = None
        if use_msc:
            self.log('INFO', "MSC Orchestrator active (Layer 1 Brain)")
            orchestrator = MSCOrchestrator()
        
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
        
        # Pre-compute features for performance if ML is needed or for reporting
        # Convert candles to DataFrame for feature extraction
        df_candles = pd.DataFrame([{
            'timestamp': c.timestamp,
            'open': float(c.open),
            'high': float(c.high),
            'low': float(c.low),
            'close': float(c.close),
            'volume': float(c.volume)
        } for c in all_candles])
        
        # Check timestamps
        df_candles['timestamp'] = pd.to_datetime(df_candles['timestamp'], unit='ms')
        
        # Calculate features
        self.log('INFO', "Calculating features...")
        df_features = self.feature_extractor.add_all_features(df_candles)
        
        # Re-align features with candles list (dropna might have removed some initial rows)
        # We need to map candle index to feature row
        # Simple map by timestamp
        features_map = df_features.set_index('timestamp')
        
        # Initialize trading components
        strategy = TJRStrategy(
            fixed_stop_loss=Decimal(str(config['stop_loss'])),
            take_profit_multiplier=Decimal(str(config['take_profit_multiplier']))
        )
        
        broker = InMemoryBroker(
            balance=Decimal(str(config['initial_balance'])),
            fee_rate=Decimal(str(config['fee_rate']))
        )
        
        from src.execution.risk import RiskConfig # Import needed inside or at top
        risk_manager = RiskManager(
            config=RiskConfig(risk_percentage=Decimal(str(config['risk_per_trade_pct'])) / 100)
        )
        
        executor = TradeExecutor(
            broker=broker,
            risk_manager=risk_manager,
            strategy=strategy
        )
        
        market = MarketState.empty(pair)
        trades_saved = 0
        filtered_trades = 0
        pending_trades = []
        
        for i, candle in enumerate(all_candles):
            # Update market state
            market = market.update(candle)
            
            # Logic manual para poder interceptar la señal
            if hasattr(broker, 'update_positions'):
                broker.update_positions(candle.close)
            
            if not broker.get_positions():
                # Bifurcation (Task 8.5)
                signal = None
                if use_msc and orchestrator:
                    signal = orchestrator.get_signal(market)
                elif use_alpha_engine and self._combiner:
                    signal = self._combiner.get_signal(market, threshold=config.get('alpha_threshold', 0.6))
                else:
                    signal = strategy.analyze(market, timeframe)
                
                # Check for signal validity and normalize for execution
                if signal:
                    # In case of MSC/Alpha, we might have 0.0 placeholders or need Decimal conversion
                    # For signals coming from MSC/Alpha, we overrideSL/TP/Price with current candle data
                    # unless it's already properly set (Compatibility layer)
                    if hasattr(signal, 'metadata') or signal.entry_price == 0.0:
                        from src.execution.executor import TradeSignal as TS
                        # Create actual execution signal based on current candle price
                        # Note: We keep the same side and confidence, but provide real prices
                        signal = TS(
                            symbol=signal.symbol,
                            side=signal.side,
                            entry_price=candle.close,
                            stop_loss=candle.close - (Decimal(str(config['stop_loss'])) if signal.side.value == 'BUY' else -Decimal(str(config['stop_loss']))),
                            take_profit=candle.close + (Decimal(str(config['stop_loss'])) * Decimal(str(config['take_profit_multiplier'])) if signal.side.value == 'BUY' else -Decimal(str(config['stop_loss'])) * Decimal(str(config['take_profit_multiplier']))),
                            confidence=signal.confidence,
                            metadata=getattr(signal, 'metadata', None)
                        )
                    
                    is_allowed = True
                    prob = 0.0
                    
                    if analyzer:
                        # Buscamos features para esta vela
                        ts_key = pd.to_datetime(candle.timestamp, unit='ms')
                        if ts_key in features_map.index:
                            feats = features_map.loc[[ts_key]]
                            prob = analyzer.predict_proba(feats)
                            
                            if prob < ml_threshold:
                                is_allowed = False
                                filtered_trades += 1
                                # self.log('DEBUG', f"Trade blocked by ML: Prob {prob:.2f} < {ml_threshold}")
                        else:
                            # Si no hay features (e.g. primeras velas), default allow or block?
                            # Default allow suele ser mejor para evitar 0 data, pero si falta feature es riesgo.
                            pass
                            
                    if is_allowed:
                        executor.execute_trade(signal)
            
            # Check for completed trades
            closed_positions = broker.get_closed_positions()
            
            # Batch Persistence Logic
            new_closed_count = len(closed_positions)
            if new_closed_count > trades_saved:
                # Accumulate pending writes
                for position in closed_positions[trades_saved:]:
                    # Usar features pre-calculadas si existen
                    ts_key = pd.to_datetime(candle.timestamp, unit='ms')
                    market_features = {}
                    
                    if ts_key in features_map.index:
                        # Convertir panda Series a dict
                        market_features_series = features_map.loc[ts_key]
                        # Handle duplicate timestamps if any (robustness)
                        if isinstance(market_features_series, pd.DataFrame):
                            market_features_series = market_features_series.iloc[0]
                        market_features = market_features_series.to_dict()
                        # Sanitize types
                        market_features = {k: float(v) if isinstance(v, (np.float32, np.float64)) else v for k,v in market_features.items()}
                    else:
                        market_features = self._extract_market_state(candle, all_candles[max(0, i-50):i])
                        
                    trade_record = {
                        'timestamp': datetime.fromtimestamp(candle.timestamp / 1000),
                        'pair': pair,
                        'symbol': pair,
                        'timeframe': timeframe_str,
                        'side': 'LONG' if position.side.value == 'BUY' else 'SHORT',
                        'entry_price': position.entry_price,
                        'exit_price': position.exit_price,
                        'stop_loss': position.stop_loss,
                        'take_profit': position.take_profit,
                        'result': 'WIN' if position.pnl > 0 else 'LOSS',
                        'profit_loss': position.pnl,
                        'profit_loss_pct': (position.pnl / (position.entry_price * position.quantity) * 100) if position.entry_price > 0 else 0,
                        'risk_reward': float(config['take_profit_multiplier']),
                        'market_state': market_features,
                        'strategy_version': config.get('strategy_version', 'MSC_v1_Worker' if use_msc else 'TJR_ML_v3_Worker'),
                        'backtest_run_id': backtest_run_id,
                        'worker_id': self.worker_id,
                        # Layer 1 Metrics (Task 8.5)
                        'agent_name': position.metadata.get('agent', 'Legacy') if hasattr(position, 'metadata') and position.metadata else 'Legacy',
                        'market_regime': position.metadata.get('regime', 'Unknown') if hasattr(position, 'metadata') and position.metadata else 'Unknown'
                    }
                    pending_trades.append(trade_record)
                
                trades_saved = new_closed_count
            
            # Flush batch every 50 trades or if many pending
            if len(pending_trades) >= 50:
                self._flush_trades(pending_trades)
                pending_trades = []
            
            # Update progress every 1000 candles
            if i % 1000 == 0:
                self.update_progress(
                    i,
                    total_candles,
                    f"Processed {i}/{total_candles}. Saved: {trades_saved}. ML Blocked: {filtered_trades}"
                )
        
        # Final Flush
        if pending_trades:
            self._flush_trades(pending_trades)
        
        # Final stats
        final_balance = broker.get_balance()
        total_trades = len(closed_positions)
        winning_trades = sum(1 for p in closed_positions if p.pnl > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(p.pnl for p in closed_positions if p.pnl > 0)
        total_loss = abs(sum(p.pnl for p in closed_positions if p.pnl < 0))
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
        
        # Max Drawdown (Task 8.6)
        equity_curve = broker.equity_curve
        max_drawdown = 0.0
        if equity_curve:
            peak = equity_curve[0]
            for val in equity_curve:
                if val > peak:
                    peak = val
                drawdown = (peak - val) / peak
                if drawdown > max_drawdown:
                    max_drawdown = float(drawdown)
        
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
            'max_drawdown_pct': round(max_drawdown * 100, 2),
            'trades_saved_to_db': trades_saved,
            'ml_filtered_trades': filtered_trades
        }
        
        self.log('INFO', f"Backtest finished. WinRate: {win_rate:.2f}%. ML Filtered: {filtered_trades} trades.")
        
        return result
    
    def _extract_market_state(self, current_candle, historical_candles: List) -> Dict[str, Any]:
        """Legacy manual extraction (fallback)"""
        if not historical_candles: return {}
        # Simple extraction for fallback
        return {'price': float(current_candle.close), 'volume': float(current_candle.volume)}

    def _flush_trades(self, trades: List[Dict]):
        """Persist a batch of trades to DB"""
        if not trades: return
        try:
            with get_db_session() as db:
                for t in trades:
                    TradeRepository.create(db, t)
        except Exception as e:
            self.log('ERROR', f"Failed to flush trades batch: {str(e)}")
