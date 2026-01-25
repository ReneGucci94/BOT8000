from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.worker import OptimizerWorker
from src.database import get_db_session
from src.database.repository import StrategyRepository, TradeRepository
from src.portfolio.correlation import calculate_correlation

class ValidatorAgent(BaseAgent):
    """
    Agente que valida estrategias en status TESTING usando el OptimizerWorker.
    Si pasan los criterios, las aprueba para producción.
    """
    
    def __init__(self):
        super().__init__("ValidatorAgent")
        
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar estrategias pendientes.
        
        Args:
            config: {
                'validation_period': {'year': 2024, 'months': [10, 11, 12]},
                'criteria': {'min_profit_factor': 1.2, 'min_win_rate': 45.0}
            }
        """
        # Support extended config for WFA
        val_periods = config.get('validation_periods', [])
        if not val_periods:
            val_periods = [config.get('validation_period', {'year': 2024, 'months': [11]})]
            
        criteria = config.get('criteria', {'min_profit_factor': 1.1, 'min_win_rate': 40.0})
        
        self.log('INFO', f"Validación: {len(val_periods)} periodos configurados.")
        
        # 1. Obtener estrategias TESTING
        pending_data = []
        with get_db_session() as db:
            pending_objs = StrategyRepository.get_by_status(db, 'TESTING')
            for obj in pending_objs:
                pending_data.append({
                    'strategy_id': obj.strategy_id,
                    'name': str(obj.name),
                    'parameters': obj.parameters.copy() if obj.parameters else {}
                })
            
        self.log('INFO', f"Encontradas {len(pending_data)} estrategias para validar.")
        
        results = []
        approved_count = 0
        
        for strategy in pending_data:
            # WFA: Strategy must pass ALL periods (Consistency)
            passed_all = True
            period_results = []
            
            for period in val_periods:
                worker_config = {
                    'pair': 'BTCUSDT', 
                    'timeframe': '4h',
                    'year': period['year'],
                    'months': period['months'],
                    'stop_loss': strategy['parameters'].get('stop_loss', 2000),
                    'take_profit_multiplier': strategy['parameters'].get('take_profit_multiplier', 2.0),
                    'fee_rate': 0.001,
                    'initial_balance': 10000,
                    'risk_per_trade_pct': 1.0,
                    'backtest_run_id': uuid.uuid4(),
                    'use_ml_model': config.get('use_ml_model', True),
                    'ml_prob_threshold': config.get('ml_prob_threshold', 0.6),
                    'strategy_version': strategy['name']  # Pass name for tracking
                }
                
                worker = OptimizerWorker(f"Validator_{strategy['name']}")
                try:
                    res = worker.execute(worker_config)
                    pf = res.get('profit_factor', 0)
                    wr = res.get('win_rate', 0)
                    
                    is_valid = pf >= criteria['min_profit_factor'] and wr >= criteria['min_win_rate']
                    period_results.append({'period': period, 'pf': pf, 'wr': wr, 'pass': is_valid})
                    
                    if not is_valid:
                        passed_all = False
                        break # Fail fast
                except Exception as e:
                    self.log('ERROR', f"Fallo validación {strategy['name']}: {e}")
                    passed_all = False
                    break
            
            status_update = {
                'name': strategy['name'],
                'passed': passed_all,
                'details': period_results
            }
            
            with get_db_session() as db:
                if passed_all:
                    # Pure Alpha Check: Correlation
                    is_correlated = False
                    candidate_trades = TradeRepository.get_by_strategy_version(db, strategy['name'])
                    
                    approved_strategies = StrategyRepository.get_approved(db, limit=100)
                    for existing in approved_strategies:
                        if existing.name == strategy['name']: continue # Skip self
                        
                        existing_trades = TradeRepository.get_by_strategy_version(db, existing.name)
                        if not existing_trades: continue
                            
                        corr = calculate_correlation(candidate_trades, existing_trades)
                        # Bridgewater rule: > 0.3 is too correlated
                        if corr > 0.3:
                            self.log('WARNING', f"❌ RECHAZADA por Correlación: {strategy['name']} vs {existing.name} (Corr: {corr:.2f})")
                            is_correlated = True
                            break
                    
                    if not is_correlated:
                        avg_pf = sum(d['pf'] for d in period_results) / len(period_results)
                        avg_wr = sum(d['wr'] for d in period_results) / len(period_results)
                        
                        StrategyRepository.approve(db, strategy['strategy_id'], avg_pf, avg_wr)
                        self.log('INFO', f"✅ APROBADA (Robust & Unique): {strategy['name']} (Avg PF: {avg_pf:.2f})")
                        approved_count += 1
                else:
                    self.log('WARNING', f"❌ RECHAZADA: {strategy['name']}")
            
            results.append(status_update)
            
        return {
            'total_validated': len(pending_data),
            'approved_count': approved_count,
            'results': results
        }
