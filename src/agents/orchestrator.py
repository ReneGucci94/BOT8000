# src/agents/orchestrator.py
from typing import Dict, Any, List, Optional
import uuid
from pathlib import Path
import pandas as pd

from src.agents.base import BaseAgent
from src.agents.data_agent import DataAgent
from src.agents.optimizer_swarm import OptimizerSwarm
from src.agents.pattern_detective import PatternDetective
from src.agents.strategy_mutator import StrategyMutator
from src.agents.validator import ValidatorAgent
from src.ml.analyzer import PatternAnalyzer
from src.database import get_db_session
from src.database.repository import TradeRepository
from src.utils.data_loader import load_binance_csv
from src.core.timeframe import Timeframe

class OrchestratorAgent(BaseAgent):
    """
    Agente Maestro que coordina el flujo completo de ML.
    Data -> Optimization -> Detection/Training -> Mutation -> Validation
    """
    
    def __init__(self):
        super().__init__("Orchestrator")
        
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar pipeline completo.
        """
        pairs = config.get('pairs', ['BTCUSDT'])
        years = config.get('years', [2024])
        # Separar Train/Val
        train_months = config.get('train_months', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        val_months = config.get('val_months', [10, 11, 12])
        
        # 1. DATA AGENT
        self.log('INFO', "--- Fase 1: Recolección de Datos ---")
        data_agent = DataAgent()
        data_res = data_agent.execute({
            'pairs': pairs,
            'timeframes': ['4h'],
            'years': years,
            'months': sorted(list(set(train_months + val_months)))
        })
        
        # 2. OPTIMIZER SWARM (Training Data Generation)
        self.log('INFO', "--- Fase 2: Generación de Datos de Entrenamiento (Swarm) ---")
        optimizer = OptimizerSwarm(num_workers=4)
        # Corremos estrategias bases para generar muchos trades y aprender de sus errores/aciertos
        opt_res = optimizer.execute({
            'pairs': pairs,
            'timeframes': ['4h'],
            'years': years,
            'months': train_months,
            # Explorar un rango amplio para generar variedad de trades
            'stop_losses': [1500, 2000, 2500], 
            'risk_rewards': [1.5, 2.0],
            'fee_rate': 0.001,
            'initial_balance': 10000,
            'risk_per_trade_pct': 1.0
        })
        run_id = opt_res['backtest_run_id']
        
        # 2.5 ML TRAINING
        self.log('INFO', "--- Fase 2.5: Entrenamiento de Modelo ML (Pattern Analyzer) ---")
        analyzer_metrics = self._train_ml_model(run_id, pairs[0], '4h', years[0], train_months)
        self.log('INFO', f"Modelo entrenado. Accuracy: {analyzer_metrics.get('accuracy', 0):.2f}")

        # 3. PATTERN DETECTIVE (Reglas Explícitas)
        self.log('INFO', "--- Fase 3: Análisis de Patrones de Falla (Reglas) ---")
        detective = PatternDetective()
        det_res = detective.execute({
            'backtest_run_id': run_id,
            'min_sample_size': 10
        })
        
        # 4. STRATEGY MUTATOR
        self.log('INFO', "--- Fase 4: Mutación de Estrategias ---")
        mutator = StrategyMutator()
        mut_res = mutator.execute({
            'base_strategy_name': 'TJR_Base',
            'num_mutations': config.get('num_mutations', 3),
            'apply_ml_filters': True, # Esto usa los patrones del detective (reglas)
            'initial_params': {'stop_loss': 2000, 'take_profit_multiplier': 2.0}
        })
        
        # 5. VALIDATOR (Con Modelo ML activado)
        self.log('INFO', "--- Fase 5: Validación Cruzada (con Filtro ML Predictivo) ---")
        # Aquí el Validator usará el worker, que a su vez cargará el modelo entrenado en 2.5
        validator = ValidatorAgent()
        val_res = validator.execute({
            'validation_period': {'year': years[0], 'months': val_months},
            'criteria': {'min_profit_factor': 1.1, 'min_win_rate': 40.0}
            # Nota: ValidatorAgent hardcodea la conf del worker por ahora, 
            # pero asumiremos que el worker lee 'use_ml_model' si lo inyectamos o si es default.
            # Idealmente Validator debería permitir inyectar config extra.
            # Por ahora, confiamos en que Worker buscará el pickle si existe.
        })
        
        self.log('INFO', f"--- Pipeline Finalizado. Aprobadas: {val_res['approved_count']} ---")
        
        return {
            'backtest_run_id': str(run_id),
            'ml_metrics': analyzer_metrics,
            'patterns_found': det_res['patterns_found'],
            'mutations_created': mut_res['count'],
            'approved_strategies': val_res['approved_count'],
            'summary': val_res['results']
        }

    def _train_ml_model(self, run_id, pair, timeframe_str, year, months) -> Dict[str, float]:
        """Helper para entrenar el modelo con datos del backtest."""
        try:
            # 1. Cargar trades de DB
            with get_db_session() as db:
                trades = TradeRepository.get_by_backtest_run(db, uuid.UUID(str(run_id)))
            
            if not trades:
                return {'error': 'No trades found'}
                
            trades_df = pd.DataFrame([{
                'timestamp': t.timestamp,
                'result': t.result,
                'pair': str(t.pair),
                'entry_price': float(t.entry_price)
            } for t in trades])
            
            # 2. Cargar Velas (Features)
            # Reconstruir dataset de velas usadas
            all_candles = []
            for m in months:
                path = Path(f"data/raw/{pair}-{timeframe_str}-{year}-{m:02d}.csv")
                if path.exists():
                    all_candles.extend(load_binance_csv(str(path), Timeframe(timeframe_str)))
            
            candles_df = pd.DataFrame([{
                'timestamp': pd.to_datetime(c.timestamp, unit='ms'),
                'open': float(c.open),
                'high': float(c.high),
                'low': float(c.low),
                'close': float(c.close),
                'volume': float(c.volume)
            } for c in all_candles])
            
            # 3. Train
            analyzer = PatternAnalyzer()
            metrics = analyzer.train(candles_df, trades_df)
            return metrics
            
        except Exception as e:
            self.log('ERROR', f"ML Training failed: {e}")
            return {'error': str(e)}
