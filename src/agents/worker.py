# src/agents/worker.py
from typing import Dict, Any, List, Optional
from pathlib import Path
from decimal import Decimal
import uuid
from datetime import datetime
import statistics
import pandas as pd
import numpy as np
import math

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
        self.db_failures = 0
        self._cached_features_map: Optional[pd.DataFrame] = None
        self._cached_candles_id: Optional[int] = None

    
    def run(self, config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Ejecutar backtest y guardar trades en DB
        
        Args:
            config: Base configuration
            **kwargs: Overrides/Additional params (params, warmup_data, initial_balance, etc.)
        """
        # Merge kwargs into config (kwargs take precedence)
        config = {**config, **kwargs}
        
        pair = config.get('pair', 'BTCUSDT') # Default for safety
        timeframe_str = config.get('timeframe', '4h')

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
        
        
        # Extract WFO Params (Optimization)
        # Using config.get('params') which comes from GA
        wfo_params = config.get('params')
        if wfo_params is None:
            wfo_params = {}
            # self.log('DEBUG', "No WFO params provided, using defaults")
        
        # Alpha Engine Setup (Task 6.9)
        use_alpha_engine = config.get('use_alpha_engine', False)
        if use_alpha_engine:
            self.log('INFO', "Alpha Engine active for signal generation")
            
            # Map WFO params to Alpha Weights
            # Defaults match the original hardcoded values if not optimizing
            w_ob = wfo_params.get('g_ob_quality', 1.5)
            w_mom = wfo_params.get('g_momentum', 2.0)
            w_vol = wfo_params.get('g_volatility', 0.5)
            w_ml = wfo_params.get('g_ml_confidence', 1.0)
            w_liq = wfo_params.get('g_liquidity', 0.8)
            
            # Iniciar alphas con los pesos definidos por el usuario / GA
            self._combiner = AlphaCombiner([
                (Alpha_OB_Quality(), w_ob),
                (Alpha_Momentum(), w_mom),
                (Alpha_Volatility(), w_vol),
                (Alpha_ML_Confidence(analyzer=analyzer), w_ml),
                (Alpha_Liquidity(), w_liq)
            ])
        
        # MSC Orchestrator Setup (Task 8.5)
        use_msc = config.get('use_msc', False)
        orchestrator = None
        if use_msc:
            self.log('INFO', "MSC Orchestrator active (Layer 1 Brain)")
            # Pass optimized thresholds if available
            # Note: MSCOrchestrator might need to be updated to accept these, 
            # or we set them after init. For now, we just init it.
            orchestrator = MSCOrchestrator()
        
        self.log('INFO', f"Starting backtest for {pair} {timeframe_str} {year}")
        
        # Load data (Memory vs Disk)
        candles_arg = config.get('candles')
        warmup_candles_arg = config.get('warmup_candles', [])
        
        if candles_arg:
            # In-memory execution (WFO/Optimization)
            # Combine warmup + main data for feature calculation
            all_candles = warmup_candles_arg + candles_arg
            # Trading starts after warmup
            start_index = len(warmup_candles_arg)
            self.log('INFO', f"Using in-memory data: {len(candles_arg)} main + {len(warmup_candles_arg)} warmup candles")
        else:
            # Disk loading (Legacy/Manual run)
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
                
            # Legacy: warmup_data might be passed but not prepended to file data
            # Use strict approach: if loaded from disk, start_index=0 (unless warmup logic added later)
            start_index = 0
            
            # Legacy warmup handling (kept for compatibility if needed, but discouraged)
            # If warmup_data passed in kwargs but loading from disk, we prepend it?
            # For now, keep simple: disk loading = 0 offset.
        
        total_candles = len(all_candles)
        self.log('INFO', f"Total candles to process: {total_candles} (Start trading at index {start_index})")
        
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
        
        # Optimization for Mac M1: Cache features if candles haven't changed (Task 8.9)
        current_candles_id = id(all_candles)
        if self._cached_candles_id == current_candles_id and self._cached_features_map is not None:
            features_map = self._cached_features_map
        else:
            # Calculate features (Expensive operation)
            self.log('INFO', f"Calculating features for {len(all_candles)} candles...")
            df_features = self.feature_extractor.add_all_features(df_candles)
            features_map = df_features.set_index('timestamp')
            # Store in cache
            self._cached_features_map = features_map
            self._cached_candles_id = current_candles_id
        
        # Initialize trading components
        # Strategy Params
        # Allow WFO params to override config defaults
        stop_loss_param = config.get('stop_loss', 100)
        # If optimization param 'stop_loss_atr_mult' exists, we might pass it.
        # TJRStrategy currently takes fixed SL. We need to update TJRStrategy 
        # to support ATR multiplier if we want to optimize it.
        # For now, we create it assuming TJRStrategy will support it or we pass it via **kwargs if flexible?
        # Let's assume we update TJRStrategy signature.
        
        str_stop_loss = wfo_params.get('fixed_stop_loss', config.get('stop_loss')) # Only if optimizing fixed
        # But param_space uses 'stop_loss_atr_mult'. 
        atr_mult_sl = wfo_params.get('stop_loss_atr_mult', None)
        
        take_profit_mult = wfo_params.get('take_profit_r_mult', config.get('take_profit_multiplier', 2.0))
        
        strategy = TJRStrategy(
            fixed_stop_loss=Decimal(str(str_stop_loss)) if str_stop_loss else None,
            take_profit_multiplier=Decimal(str(take_profit_mult)),
            stop_loss_atr_multiplier=Decimal(str(atr_mult_sl)) if atr_mult_sl else None
        )
        
        broker = InMemoryBroker(
            balance=Decimal(str(config.get('initial_balance', config['initial_balance']))),
            fee_rate=Decimal(str(config['fee_rate']))
        )
        
        from src.execution.risk import RiskConfig # Import needed inside or at top
        
        # Risk Params
        risk_pct = wfo_params.get('risk_per_trade_pct', config.get('risk_per_trade_pct', 1.0))
        max_portfolio_risk = config.get('max_portfolio_risk', None)
        use_dd_scaling = config.get('use_dd_scaling', False)
        
        from src.execution.risk import RiskConfig  # Ensure import is available

        risk_manager = RiskManager(
            config=RiskConfig(
                risk_percentage=Decimal(str(risk_pct)) / 100,
                max_portfolio_risk=Decimal(str(max_portfolio_risk)) if max_portfolio_risk else None,
                use_dd_scaling=use_dd_scaling
            )
        )
        
        executor = TradeExecutor(
            broker=broker,
            risk_manager=risk_manager,
            strategy=strategy
        )
        
        market = MarketState.empty(pair)
        
        # --- Warmup Phase (Integrated) ---
        # No explicit separate loop needed as features are calc on all_candles
        # Just ensure market state is updated for warmup part
        # Logic below handles it via 'start_index' skipping trade logic
                    
        trades_saved = 0
        filtered_trades = 0
        pending_trades = []
        
        
        # Extract WFO params if present (redundant reassignment but keeping for clarity if used later)
        # wfo_params extracted at top of run()
        
        for i, candle in enumerate(all_candles):
            # Update market state
            market = market.update(candle)
            
            # Logic manual para poder interceptar la señal
            if hasattr(broker, 'update_positions'):
                broker.update_positions(candle.close)
            
            # SKIP TRADING during Warmup
            if i < start_index:
                continue

            if not broker.get_positions():
                # Bifurcation (Task 8.5)
                signal = None
                if use_msc and orchestrator:
                    # Use decide() with params
                    signal = orchestrator.decide(market, params=wfo_params)
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
                        
                        entry_price = candle.close
                        
                        # --- Dynamic SL/TP Calculation (WFO) ---
                        if wfo_params:
                            atr_mult = float(wfo_params.get('stop_loss_atr_mult', 1.5))
                            tp_r_mult = float(wfo_params.get('take_profit_r_mult', 2.0))
                            
                            # Get ATR
                            current_atr = market.atr[-1] if market.atr else 0.0
                            if current_atr == 0.0:
                                 # Fallback if ATR not ready
                                 sl_dist = Decimal(str(config['stop_loss']))
                            else:
                                 sl_dist = Decimal(str(current_atr)) * Decimal(str(atr_mult))
                                 
                            tp_dist = sl_dist * Decimal(str(tp_r_mult))
                            
                        else:
                            # Legacy Fixed Logic
                            sl_dist = Decimal(str(config['stop_loss']))
                            tp_dist = sl_dist * Decimal(str(config['take_profit_multiplier']))
                        
                        if signal.side.value == 'BUY':
                            stop_loss = entry_price - sl_dist
                            take_profit = entry_price + tp_dist
                        else:
                            stop_loss = entry_price + sl_dist
                            take_profit = entry_price - tp_dist
                            
                        # Create actual execution signal based on current candle price
                        # Note: We keep the same side and confidence, but provide real prices
                        signal = TS(
                            symbol=signal.symbol,
                            side=signal.side,
                            entry_price=entry_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
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
        
        # Final Flush (blocks outside loop)
        if pending_trades:
            self._flush_trades(pending_trades)
        
        # Final stats
        closed_positions = broker.get_closed_positions()
        final_balance = broker.get_balance()
        total_trades = len(closed_positions)
        result = self._calculate_metrics(
            final_balance=final_balance,
            initial_balance=Decimal(str(config.get("initial_balance", 10000))),
            pair=pair,
            timeframe_str=timeframe_str,
            year=year,
            trades_saved=trades_saved,
            filtered_trades=filtered_trades,
            closed_positions=closed_positions,
            equity_curve=broker.equity_curve
        )
        
        # Extract win_rate from result for logging
        win_rate = result.get('win_rate', 0.0)
        self.log('INFO', f"Backtest finished. WinRate: {win_rate:.2f}%. ML Filtered: {filtered_trades} trades.")
        
        return result
    
    def _calculate_metrics(
        self, 
        final_balance, 
        initial_balance, 
        pair, 
        timeframe_str, 
        year, 
        trades_saved, 
        filtered_trades, 
        closed_positions, 
        equity_curve
    ) -> Dict[str, Any]:
        """Calculate comprehensive backtest metrics for WFO fitness function"""
        total_trades = len(closed_positions)
        
        # Guard against zero trades to avoid -inf/NaN in fitness
        if total_trades == 0:
            return {
                'pair': pair,
                'timeframe': timeframe_str,
                'year': year,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'final_balance': float(final_balance),
                'net_profit': 0.0,
                'return': 0.0,
                'win_rate': 0.0,
                'gross_profit': 0.0,
                'gross_loss': 0.0,
                'profit_factor': 1.0,
                'max_drawdown': 0.0,
                'max_drawdown_pct': 0.0,
                'sharpe': 0.0,
                'trades_saved_to_db': trades_saved,
                'ml_filtered_trades': filtered_trades
            }

        winning_trades = sum(1 for p in closed_positions if p.pnl > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100)
        
        gross_profit = float(sum(p.pnl for p in closed_positions if p.pnl > 0))
        gross_loss = float(abs(sum(p.pnl for p in closed_positions if p.pnl < 0)))
        
        # PF Logic: Cap at 10.0 if no loss, avoid 0.0 for winners
        if gross_loss == 0:
            profit_factor = 10.0 if gross_profit > 0 else 1.0
        else:
            profit_factor = gross_profit / gross_loss
            
        net_profit = float(final_balance - initial_balance)
        return_pct = (net_profit / float(initial_balance) * 100) if initial_balance > 0 else 0.0
        
        # Max Drawdown Calculation
        max_drawdown = 0.0
        if equity_curve:
            peak = float(equity_curve[0])
            for val in equity_curve:
                val_f = float(val)
                if val_f > peak:
                    peak = val_f
                if peak > 0:
                    dd = (peak - val_f) / peak
                    if dd > max_drawdown:
                        max_drawdown = dd
        
        max_drawdown_pct = max_drawdown * 100.0
        
        # Sharpe Ratio (Simple, non-annualized, good for relative fitness)
        sharpe = 0.0
        if equity_curve and len(equity_curve) > 1:
            eq = [float(x) for x in equity_curve]
            # Calculate returns series
            rets = []
            for i in range(1, len(eq)):
                if eq[i-1] > 0:
                    rets.append((eq[i] / eq[i-1]) - 1.0)
            
            if len(rets) >= 2:
                std = statistics.pstdev(rets)
                if std > 0:
                    sharpe = (statistics.mean(rets) / std) * math.sqrt(len(rets))
        
        return {
            'pair': pair,
            'timeframe': timeframe_str,
            'year': year,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'final_balance': float(final_balance),
            'net_profit': float(net_profit),
            'return': round(return_pct, 2),              # REQUIRED by run_wfo
            'win_rate': round(win_rate, 2),
            'gross_profit': round(gross_profit, 2),       # REQUIRED by fitness
            'gross_loss': round(gross_loss, 2),            # REQUIRED by fitness
            'profit_factor': round(float(profit_factor), 4),
            'max_drawdown': round(max_drawdown_pct, 2),    # REQUIRED by fitness (in %)
            'max_drawdown_pct': round(max_drawdown_pct, 2),
            'sharpe': round(float(sharpe), 4),             # REQUIRED by fitness
            'trades_saved_to_db': trades_saved,
            'ml_filtered_trades': filtered_trades
        }

    def _extract_market_state(self, current_candle, historical_candles: List) -> Dict[str, Any]:
        """Legacy manual extraction (fallback)"""
        if not historical_candles: return {}
        # Simple extraction for fallback
        return {'price': float(current_candle.close), 'volume': float(current_candle.volume)}

    def _flush_trades(self, trades: List[Dict]):
        """Persist a batch of trades to DB"""
        if not trades: return
        if self.db_failures > 0: return  # Skip if DB is down
        
        # Optimization for Mac M1: Disable DB persistence during WFO optimization (Task 8.9)
        # We identify optimization runs by their backtest_run_id (wfo_subtrain/wfo_valtrain)
        if trades[0].get('backtest_run_id') in ['wfo_subtrain', 'wfo_valtrain']:
            return
        
        try:
            with get_db_session() as db:
                for t in trades:
                    TradeRepository.create(db, t)
        except Exception as e:
            self.db_failures += 1
            self.log('WARNING', f"DB connection failed. Disabling persistence for this worker. Error: {str(e)}")
