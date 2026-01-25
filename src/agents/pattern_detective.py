# src/agents/pattern_detective.py
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, _tree
from decimal import Decimal
import uuid

from src.agents.base import BaseAgent
from src.database import get_db_session
from src.database.repository import TradeRepository, PatternRepository

class PatternDetective(BaseAgent):
    """
    Agente que analiza el historial de trades para detectar patrones correlacionados con el fracaso.
    """
    
    def __init__(self):
        super().__init__("PatternDetective")
        
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analizar trades y salvar patrones detectados.
        
        Args:
            config: {
                'backtest_run_id': uuid (opcional),
                'min_sample_size': 20,
                'max_win_rate_threshold': 35.0 # Solo nos interesan patrones que pierdan mucho
            }
        """
        run_id = config.get('backtest_run_id')
        min_samples = config.get('min_sample_size', 20)
        threshold = config.get('max_win_rate_threshold', 35.0)
        
        self.log('INFO', f"Iniciando detección de patrones peligrosos (threshold < {threshold}%)")
        
        data = []
        trade_pairs = set()
        trade_tfs = set()
        
        with get_db_session() as db:
            if run_id:
                trades_objs = TradeRepository.get_by_backtest_run(db, uuid.UUID(str(run_id)))
            else:
                from src.database.models import Trade
                trades_objs = db.query(Trade).limit(5000).all()
            
            if len(trades_objs) < min_samples:
                self.log('WARNING', f"Muestra muy pequeña ({len(trades_objs)}). Abortando.")
                return {'patterns_found': 0, 'reason': 'insufficient_data'}

            for t in trades_objs:
                features = t.market_state.copy()
                features['target'] = 1 if t.result == 'WIN' else 0
                data.append(features)
                trade_pairs.add(str(t.pair))
                trade_tfs.add(str(t.timeframe))
            
        # 2. Preparar Dataframe para ML
        df = pd.DataFrame(data)
        
        # Filtrar solo columnas numéricas para el árbol básica
        X = df.drop(columns=['target', 'trend', 'error'], errors='ignore').select_dtypes(include=[np.number])
        y = df['target']
        
        if X.empty:
            self.log('ERROR', "No hay features numéricas en market_state para analizar.")
            return {'patterns_found': 0, 'reason': 'no_numeric_features'}

        # 3. Entrenar Árbol de Decisión para reglas simples
        clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=min_samples)
        clf.fit(X, y)
        
        # 4. Extraer reglas del árbol
        patterns = self._extract_rules(clf, X.columns, X, y, threshold)
        
        # 5. Guardar en DB
        saved_count = 0
        with get_db_session() as db:
            for p in patterns:
                pattern_data = {
                    'pattern_type': 'market_condition_risk',
                    'description': f"Condiciones detectadas con win rate de {p['win_rate']}%",
                    'conditions': p['conditions'],
                    'win_rate': Decimal(str(p['win_rate'])),
                    'sample_size': p['sample_size'],
                    'confidence_score': Decimal("0.8"), # Constante para este agente básico
                    'applicable_pairs': list(trade_pairs),
                    'applicable_timeframes': list(trade_tfs),
                    'is_active': True
                }
                PatternRepository.create(db, pattern_data)
                saved_count += 1
                
        self.log('INFO', f"Detective finalizado. Se encontraron y guardaron {saved_count} patrones.")
        
        return {
            'patterns_found': saved_count,
            'total_trades_analyzed': len(data)
        }

    def _extract_rules(self, clf, feature_names, X, y, threshold):
        """Extrae reglas de las hojas del árbol que cumplen el threshold de perdidas."""
        tree_ = clf.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]

        patterns = []

        def recurse(node, depth, current_conditions):
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold_val = tree_.threshold[node]
                
                # Rama Izquierda ( <= threshold )
                left_cond = current_conditions.copy()
                left_cond.append(f"{name} <= {threshold_val:.4f}")
                recurse(tree_.children_left[node], depth + 1, left_cond)
                
                # Rama Derecha ( > threshold )
                right_cond = current_conditions.copy()
                right_cond.append(f"{name} > {threshold_val:.4f}")
                recurse(tree_.children_right[node], depth + 1, right_cond)
            else:
                # Estamos en una hoja. Calculamos win rate.
                node_samples = tree_.n_node_samples[node]
                values = tree_.value[node][0] # [[losses, wins]]
                wins = values[1]
                win_rate = (wins / node_samples) * 100
                
                if win_rate <= threshold:
                    patterns.append({
                        'conditions': current_conditions,
                        'win_rate': round(win_rate, 2),
                        'sample_size': int(node_samples)
                    })

        recurse(0, 1, [])
        return patterns
