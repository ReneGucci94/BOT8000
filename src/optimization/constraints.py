"""
Constraint projection para parameter space.
Spec: Codex PARTE 3 - Constraints
"""
from typing import Dict, Any
from src.optimization.param_space import ParamSpace, ParamType


def project_constraints(
    params: Dict[str, Any],
    space: ParamSpace
) -> Dict[str, Any]:
    """
    Proyecta parámetros al espacio válido aplicando constraints.
    
    Constraints según Codex PARTE 3:
    1. Clip todos los params a [min, max]
    2. adx_sideways_threshold < adx_trend_threshold
    3. atr_low_mult < 1.00 (ya garantizado por max=0.85)
    
    Args:
        params: Dict de parámetros (pueden ser inválidos)
        space: ParamSpace con definiciones
        
    Returns:
        Dict de parámetros proyectados (válidos)
    """
    # Paso 1: Clip todos los params a rangos
    projected = params.copy()
    
    for name, param in space.params.items():
        if name in projected:
            val = projected[name]
            # Clip bounds
            val = max(param.min_value, min(val, param.max_value))
            
            # Enforce types
            if param.param_type == ParamType.INT:
                val = int(val)
            
            projected[name] = val
            
    # Paso 2: Arreglar ADX constraint (adx_sideways_threshold < adx_trend_threshold)
    # Sideways range: [10, 22]
    # Trend range: [20, 35]
    
    if "adx_sideways_threshold" in projected and "adx_trend_threshold" in projected:
        sideways = projected["adx_sideways_threshold"]
        trend = projected["adx_trend_threshold"]
        
        if sideways >= trend:
            # Fix: Ensure sideways is strictly less than trend
            # Prefer lowering sideways if possible, or raising trend if sideways is already at min?
            # Given trend min is 20, and sideways valid range is [10, 22].
            # If trend is 20, sideways must be < 20. Max valid sideways is 19.
            # So `min(sideways, trend - 1)` should always work and be valid > 10
            # since trend >= 20 => trend - 1 >= 19 >= 10.
            
            new_sideways = min(sideways, trend - 1)
            projected["adx_sideways_threshold"] = new_sideways
            
    return projected
