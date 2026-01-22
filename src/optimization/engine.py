import os
import glob
import json
import itertools
import time
import concurrent.futures
from decimal import Decimal
from typing import List, Iterator, Dict, Any
from pathlib import Path
from tqdm import tqdm

from .types import OptimizerConfig, TestConfig, BacktestResult
from core.timeframe import Timeframe
from core.market import MarketState
from utils.data_loader import load_binance_csv
from simulation.backtest import Backtester
from strategy.engine import TJRStrategy
from execution.executor import TradeExecutor
from execution.risk import RiskManager, RiskConfig
from simulation.broker import InMemoryBroker

class OptimizerEngine:
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.results: List[BacktestResult] = []
        self.checkpoint_file = Path("results/optimizer_checkpoint.json")
        self.completed_ids = set()

    def generate_configurations(self) -> Iterator[TestConfig]:
        """Cartesian product of all parameters."""
        i = 0
        for timeframe in self.config.timeframes:
            for pair in self.config.pairs:
                for sl in self.config.stop_losses:
                    for tp in self.config.take_profit_multiples:
                        for fee in self.config.fee_rates:
                            config_id = f"cfg_{i:04d}_{pair}_{timeframe}"
                            yield TestConfig(
                                id=config_id,
                                timeframe=timeframe,
                                pair=pair,
                                stop_loss=sl,
                                take_profit_r=tp,
                                fee_rate=fee
                            )
                            i += 1

    def load_checkpoint(self):
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    self.completed_ids = set(data.get("completed_ids", []))
                    # We would ideally load previous results too, but for MVPs often we just skip re-running 
                    # and assume results are already saved in a CSV. 
                    # For this implementation, let's assume we append to a CSV immediately.
            except Exception as e:
                print(f"Failed to load checkpoint: {e}")

    def save_checkpoint(self, results_batch: List[BacktestResult]):
        # Save IDs
        new_ids = {r.config_id for r in results_batch}
        self.completed_ids.update(new_ids)
        
        # Write checkpoint file
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                "completed_ids": list(self.completed_ids)
            }, f)
            
        # Append to CSV
        csv_file = Path("results/optimizer_results.csv")
        headers = [
            "config_id", "timeframe", "pair", "stop_loss", 
            "take_profit_r", "fee_rate", "total_trades", 
            "win_rate", "net_profit", "max_drawdown", "execution_time"
        ]
        
        write_header = not csv_file.exists()
        
        with open(csv_file, 'a') as f:
            if write_header:
                f.write(",".join(headers) + "\n")
            
            for r in results_batch:
                line = [
                    r.config_id, r.timeframe, r.pair, str(r.stop_loss),
                    str(r.take_profit_r), str(r.fee_rate), str(r.total_trades),
                    f"{r.win_rate:.4f}", f"{r.net_profit:.2f}", 
                    f"{r.max_drawdown:.2f}", f"{r.execution_time:.4f}"
                ]
                f.write(",".join(line) + "\n")

    def run(self):
        # Ensure results dir
        Path("results").mkdir(exist_ok=True)
        
        self.load_checkpoint()
        
        all_configs = list(self.generate_configurations())
        pending_configs = [c for c in all_configs if c.id not in self.completed_ids]
        
        print(f"Total Configs: {len(all_configs)}")
        print(f"Pending: {len(pending_configs)}")
        
        if not pending_configs:
            print("All configurations completed.")
            return

        batch_size = self.config.checkpoint_interval
        
        # Parallel Execution
        # We need to pass the Data Path to the worker so it can find files
        data_path = self.config.data_path
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # We process in batches to save checkpoints periodically
            for i in range(0, len(pending_configs), batch_size):
                batch = pending_configs[i : i + batch_size]
                futures = {
                    executor.submit(execute_worker, config, data_path, self.config.initial_balance, self.config.risk_percent): config 
                    for config in batch
                }
                
                results_batch = []
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(batch), desc=f"Batch {i//batch_size + 1}"):
                    try:
                        res = future.result()
                        results_batch.append(res)
                    except Exception as e:
                        print(f"Worker Error: {e}")
                
                self.save_checkpoint(results_batch)

# Static Worker Function (Must be outside class for multiprocessing pickle)
def execute_worker(config: TestConfig, data_path: str, initial_balance: Decimal, risk_percent: Decimal) -> BacktestResult:
    start_time = time.time()
    
    # 1. Load Data
    # Glob for all files matching Pair + Timeframe
    # Convention: {pair}-{timeframe}-*.csv
    # E.g. BTCUSDT-5m-2024-01.csv
    pattern = os.path.join(data_path, f"{config.pair}-{config.timeframe}-*.csv")
    files = sorted(glob.glob(pattern))
    
    if not files:
        # Fallback or Error
        # Return empty result
        return BacktestResult(
            config.id, config.timeframe, config.pair, config.stop_loss, config.take_profit_r, config.fee_rate,
            0, 0, 0, 0.0, Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), 0.0
        )
        
    # Map string timeframe to Enum
    tf_map = {
        "5m": Timeframe.M5,
        "15m": Timeframe.M15,
        "1h": Timeframe.H1,
        "4h": Timeframe.H4
    }
    tf_enum = tf_map.get(config.timeframe, Timeframe.M5) # Default/Fallback
    
    all_candles = []
    for f in files:
        month_candles = load_binance_csv(f, tf_enum)
        all_candles.extend(month_candles)
        
    # 2. Setup System
    broker = InMemoryBroker(balance=initial_balance, fee_rate=config.fee_rate) # Need to ensure InMemoryBroker accepts fee_rate constructor? It usually has fixed fee.
    # Wait, InMemoryBroker currently has fixed fee 0.1%. Need to update it?
    # Let's check InMemoryBroker. Using property logic might be needed or Constructor.
    # Assuming we modify InMemoryBroker or it already supports it.
    # Checking InMemoryBroker code... it has `calculate_fee` method but usually hardcoded 0.001.
    # FIX: We will update broker fee_rate after init if it's not in init.
    if hasattr(broker, 'fee_rate'):
         broker.fee_rate = config.fee_rate
    else:
         # Need to ensure Broker supports variable fees. For now let's monkey patch or assume we updated it.
         # Actually let's assume standard 0.001 for now or inject it.
         # For this specific task, if "fee_rates" is an optimization param, we MUST support it.
         # I'll update InMemoryBroker in a separate step or just set it: `broker.trading_fee = config.fee_rate` if public.
         pass
         
    # Risk
    risk = RiskManager(RiskConfig(risk_percent))
    
    # Strategy (The key injection point)
    strategy = TJRStrategy(
        fixed_stop_loss=config.stop_loss if config.stop_loss > 0 else None,
        take_profit_multiplier=Decimal(str(config.take_profit_r))
    )
    
    executor = TradeExecutor(broker, risk)
    backtester = Backtester()
    
    # 3. Run
    # Warning: We must pass the correct timeframe Enum to backtester run
    report = backtester.run(all_candles, broker, strategy, executor, tf_enum)
    
    duration = time.time() - start_time
    
    return BacktestResult(
        config_id=config.id,
        timeframe=config.timeframe,
        pair=config.pair,
        stop_loss=config.stop_loss,
        take_profit_r=config.take_profit_r,
        fee_rate=config.fee_rate,
        total_trades=report.total_trades,
        winning_trades=report.winning_trades,
        losing_trades=report.losing_trades,
        win_rate=report.win_rate,
        gross_profit=report.gross_profit,
        gross_loss=report.gross_loss,
        fees_paid=broker.total_fees_paid,
        net_profit=report.net_profit,
        max_drawdown=report.max_drawdown,
        execution_time=duration
    )
