"""
Parameter space definition para WFO.
Spec: Codex PARTE 3
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any
import random


class ParamType(Enum):
    """Tipo de parámetro."""
    FLOAT = "float"
    INT = "int"


@dataclass
class ParamDef:
    """
    Definición de un parámetro optimizable.
    """
    name: str
    param_type: ParamType
    min_value: float
    max_value: float
    default_value: float
    description: str = ""


class ParamSpace:
    """
    Espacio de parámetros del sistema MSC v3.
    Define todos los params optimizables, rangos, y defaults.
    """
    
    def __init__(self, params: Dict[str, ParamDef]):
        """
        Args:
            params: Dict de nombre → ParamDef
        """
        self.params = params
    
    def sample_random(self, seed: int = None) -> Dict[str, Any]:
        """
        Genera un set de parámetros aleatorios dentro de rangos.
        
        Args:
            seed: Random seed para reproducibilidad
            
        Returns:
            Dict de nombre → valor
        """
        if seed is not None:
            random.seed(seed)
            
        result = {}
        for name, param in self.params.items():
            if param.param_type == ParamType.FLOAT:
                val = random.uniform(param.min_value, param.max_value)
                result[name] = round(val, 2)  # Rounding for cleanliness, though not strictly required
            else:
                val = random.randint(int(param.min_value), int(param.max_value))
                result[name] = val
        return result
    
    def get_defaults(self) -> Dict[str, Any]:
        """
        Retorna valores default de todos los parámetros.
        """
        return {name: param.default_value for name, param in self.params.items()}


def get_default_param_space() -> ParamSpace:
    """
    Crea el param space según Codex PARTE 3.1
    
    Returns:
        ParamSpace con 13 parámetros optimizables
    """
    params = {}
    
    # helper to add params easily
    def add_param(name, p_type, min_v, max_v, default):
        params[name] = ParamDef(name, p_type, min_v, max_v, default)

    # A) Pure Alpha global multipliers (5 params)
    add_param("g_ob_quality", ParamType.FLOAT, 0.50, 2.00, 1.0)
    add_param("g_momentum", ParamType.FLOAT, 0.50, 2.00, 1.0)
    add_param("g_volatility", ParamType.FLOAT, 0.50, 2.00, 1.0)
    add_param("g_liquidity", ParamType.FLOAT, 0.50, 2.00, 1.0)
    add_param("g_ml_confidence", ParamType.FLOAT, 0.00, 1.50, 1.0)
    
    # B) Alpha threshold (1 param)
    add_param("alpha_threshold", ParamType.FLOAT, 0.45, 0.75, 0.60)
    
    # C) Classifier thresholds (4 params)
    add_param("adx_trend_threshold", ParamType.INT, 20, 35, 25)
    add_param("adx_sideways_threshold", ParamType.INT, 10, 22, 15)
    add_param("atr_high_mult", ParamType.FLOAT, 1.20, 2.00, 1.50)
    add_param("atr_low_mult", ParamType.FLOAT, 0.45, 0.85, 0.65)
    
    # D) Execution/Risk (3 params)
    add_param("stop_loss_atr_mult", ParamType.FLOAT, 1.00, 3.50, 2.0)
    add_param("take_profit_r_mult", ParamType.FLOAT, 1.00, 4.00, 2.0)
    add_param("risk_per_trade_pct", ParamType.FLOAT, 0.25, 1.25, 1.0)
    
    return ParamSpace(params)
