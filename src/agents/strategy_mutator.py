# src/agents/strategy_mutator.py
from typing import Dict, Any, List, Optional
import uuid
import random

from src.agents.base import BaseAgent
from src.database import get_db_session
from src.database.repository import StrategyRepository, PatternRepository

class StrategyMutator(BaseAgent):
    """
    Agente que crea variaciones de estrategias basadas en patrones ML detectados.
    """
    
    def __init__(self):
        super().__init__("StrategyMutator")
        
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear mutaciones de una estrategia base.
        
        Args:
            config: {
                'base_strategy_name': str,
                'num_mutations': int,
                'apply_ml_filters': bool
            }
        """
        base_name = config.get('base_strategy_name', 'TJR_Base')
        num_mutations = config.get('num_mutations', 3)
        use_ml = config.get('apply_ml_filters', True)
        
        self.log('INFO', f"Iniciando mutación de {base_name}")
        
        # 1. Obtener patrones activos si se requiere ML
        active_patterns_data = []
        if use_ml:
            with get_db_session() as db:
                patterns = PatternRepository.get_active_patterns(db)
                for p in patterns:
                    active_patterns_data.append({
                        'description': str(p.description),
                        'conditions': p.conditions
                    })
            self.log('INFO', f"Encontrados {len(active_patterns_data)} patrones ML para aplicar.")

        # 2. Generar mutaciones
        mutations_created = []
        
        for i in range(num_mutations):
            new_params = self._mutate_params(config.get('initial_params', {}))
            new_filters = {}
            
            if use_ml and active_patterns_data:
                # Seleccionar un patrón aleatorio para mitigar o todos
                pattern = random.choice(active_patterns_data)
                new_filters['ml_avoidance'] = {
                    'description': pattern['description'],
                    'conditions': pattern['conditions']
                }
            
            mutation_name = f"{base_name}_mut_{uuid.uuid4().hex[:6]}"
            
            strategy_data = {
                'name': mutation_name,
                'description': f"Mutación de {base_name} con {'filtros ML' if new_filters else 'parámetros variados'}",
                'base_strategy': base_name,
                'parameters': new_params,
                'filters': new_filters,
                'status': 'TESTING'
            }
            
            with get_db_session() as db:
                StrategyRepository.create(db, strategy_data)
                
            mutations_created.append(mutation_name)
            self.log('INFO', f"Creada mutación: {mutation_name}")
            
        return {
            'base_strategy': base_name,
            'mutations_created': mutations_created,
            'count': len(mutations_created)
        }
        
    def _mutate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica variaciones aleatorias a los parámetros base."""
        mutated = params.copy()
        
        # Ejemplo: variamos el SL o el RR ligeramente
        if 'stop_loss' in mutated:
            variation = random.uniform(0.9, 1.1)
            mutated['stop_loss'] = int(float(mutated['stop_loss']) * variation)
            
        if 'take_profit_multiplier' in mutated:
            variation = random.uniform(0.9, 1.1)
            mutated['take_profit_multiplier'] = round(float(mutated['take_profit_multiplier']) * variation, 2)
            
        return mutated
