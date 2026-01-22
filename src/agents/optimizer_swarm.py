# src/agents/optimizer_swarm.py
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor, as_completed
import uuid
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.worker import OptimizerWorker
from src.database import get_db_session
from src.database.repository import BacktestRunRepository

class OptimizerSwarm(BaseAgent):
    """
    Orquestador de múltiples workers paralelos
    
    Crea un backtest run y distribuye trabajo entre workers
    """
    
    def __init__(self, num_workers: int = 4):
        super().__init__("OptimizerSwarm")
        self.num_workers = num_workers
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribuir backtests entre workers paralelos
        
        Args:
            config: {
                'pairs': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'],
                'timeframes': ['4h', '1d'],
                'years': [2024],
                'months': [1, 2, ..., 12],
                'stop_losses': [1000, 1500, 2000],
                'risk_rewards': [1.5, 2.0, 2.5],
                'fee_rates': [0.001, 0.0004],
                'initial_balance': 10000,
                'risk_per_trade_pct': 1.0
            }
        """
        # Create backtest run en DB
        run_id = uuid.uuid4()
        
        with get_db_session() as db:
            run = BacktestRunRepository.create(db, config)
            run_id = run.run_id
        
        self.log('INFO', f"Created backtest run {run_id}")
        
        # Generate all configuration combinations
        configs = self._generate_configs(config, run_id)
        total_configs = len(configs)
        
        self.log('INFO', f"Generated {total_configs} configurations to test with {self.num_workers} workers")
        
        # Execute in parallel
        results = []
        completed = 0
        failed = 0
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as pool:
            # Submit all tasks
            # Note: _run_worker must be at module level or static if using ProcessPool on some systems
            # but usually within a class method it needs to be carefully handled.
            # In Python, we often use a helper function at the top level.
            future_to_config = {
                pool.submit(_execute_worker_task, i, cfg): cfg
                for i, cfg in enumerate(configs)
            }
            
            # Process as they complete
            for future in as_completed(future_to_config):
                cfg = future_to_config[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    self.update_progress(
                        completed + failed,
                        total_configs,
                        f"Completed {completed}/{total_configs} configs. Latest: {cfg['pair']} {cfg['timeframe']}"
                    )
                
                except Exception as e:
                    self.log('ERROR', f"Config failed for {cfg['pair']} {cfg['timeframe']}: {str(e)}")
                    failed += 1
        
        # Update backtest run status
        with get_db_session() as db:
            BacktestRunRepository.complete(db, run_id)
        
        final_result = {
            'backtest_run_id': str(run_id),
            'total_configs': total_configs,
            'completed': completed,
            'failed': failed,
            'results': results
        }
        
        self.log('INFO', f"Optimizer swarm completed: {completed} successful, {failed} failed")
        
        return final_result
    
    def _generate_configs(self, config: Dict[str, Any], run_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Generar todas las combinaciones de configuraciones"""
        pairs = config.get('pairs', [])
        timeframes = config.get('timeframes', [])
        years = config.get('years', [])
        months = config.get('months', list(range(1, 13)))
        stop_losses = config.get('stop_losses', [1000])
        risk_rewards = config.get('risk_rewards', [2.0])
        fee_rates = config.get('fee_rates', [0.001])
        
        combinations = []
        
        for pair in pairs:
            for timeframe in timeframes:
                for year in years:
                    for sl in stop_losses:
                        for rr in risk_rewards:
                            for fee in fee_rates:
                                combinations.append({
                                    'pair': pair,
                                    'timeframe': timeframe,
                                    'year': year,
                                    'months': months,
                                    'stop_loss': sl,
                                    'take_profit_multiplier': rr,
                                    'fee_rate': fee,
                                    'initial_balance': config.get('initial_balance', 10000),
                                    'risk_per_trade_pct': config.get('risk_per_trade_pct', 1.0),
                                    'backtest_run_id': run_id
                                })
        
        return combinations

def _execute_worker_task(worker_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function for ProcessPoolExecutor"""
    worker = OptimizerWorker(f"W{worker_id}")
    return worker.execute(config)
