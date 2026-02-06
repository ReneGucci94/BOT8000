"""
Tests para constraint projection.
Spec: Codex PARTE 3 - Constraints
"""
import pytest
from src.optimization.param_space import get_default_param_space
from src.optimization.constraints import project_constraints


def test_adx_constraint_sideways_less_than_trend():
    """
    Constraint: adx_sideways_threshold < adx_trend_threshold
    Spec: Codex PARTE 3.1 - Classifier constraints
    """
    space = get_default_param_space()
    
    # Caso violando constraint
    params = {
        "adx_trend_threshold": 25,
        "adx_sideways_threshold": 30,  # > trend (INVÁLIDO)
        **{k: v.default_value for k, v in space.params.items() 
           if k not in ["adx_trend_threshold", "adx_sideways_threshold"]}
    }
    
    # Proyectar
    projected = project_constraints(params, space)
    
    # Debe arreglarse
    assert projected["adx_sideways_threshold"] < projected["adx_trend_threshold"]


def test_atr_low_mult_less_than_one():
    """
    Constraint: atr_low_mult < 1.00
    Spec: Codex PARTE 3.1
    """
    space = get_default_param_space()
    
    # atr_low_mult ya está definido con max=0.85, pero validar projection
    params = space.get_defaults()
    params["atr_low_mult"] = 1.05  # Fuera de rango
    
    projected = project_constraints(params, space)
    
    # Debe clippearse a max
    assert projected["atr_low_mult"] <= 0.85


def test_all_params_clipped_to_bounds():
    """
    Projection debe clippear todos los params a sus rangos.
    """
    space = get_default_param_space()
    
    # Crear params inválidos (fuera de rangos)
    params = {
        "g_ob_quality": 5.0,  # max=2.0
        "g_momentum": -1.0,   # min=0.5
        "alpha_threshold": 0.9,  # max=0.75
        "adx_trend_threshold": 50,  # max=35
        "stop_loss_atr_mult": 0.5,  # min=1.0
        **{k: v.default_value for k, v in space.params.items() 
           if k not in ["g_ob_quality", "g_momentum", "alpha_threshold", 
                       "adx_trend_threshold", "stop_loss_atr_mult"]}
    }
    
    projected = project_constraints(params, space)
    
    # Verificar clipping
    assert projected["g_ob_quality"] == 2.0
    assert projected["g_momentum"] == 0.5
    assert projected["alpha_threshold"] == 0.75
    assert projected["adx_trend_threshold"] == 35
    assert projected["stop_loss_atr_mult"] == 1.0


def test_adx_constraint_fixed_when_both_invalid():
    """
    Si ambos ADX thresholds están mal, debe arreglar sideways primero.
    """
    space = get_default_param_space()
    
    params = {
        "adx_trend_threshold": 15,  # < min (20)
        "adx_sideways_threshold": 25,  # > trend
        **{k: v.default_value for k, v in space.params.items() 
           if k not in ["adx_trend_threshold", "adx_sideways_threshold"]}
    }
    
    projected = project_constraints(params, space)
    
    # Ambos deben estar en rango Y satisfacer constraint
    assert 20 <= projected["adx_trend_threshold"] <= 35
    assert 10 <= projected["adx_sideways_threshold"] <= 22
    assert projected["adx_sideways_threshold"] < projected["adx_trend_threshold"]


def test_projection_is_idempotent():
    """
    Proyectar params válidos no debe cambiarlos.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    projected = project_constraints(params, space)
    
    # Debe ser idéntico
    assert projected == params


def test_int_params_stay_int():
    """
    Params de tipo INT deben seguir siendo int después de projection.
    """
    space = get_default_param_space()
    params = {
        "adx_trend_threshold": 25.7,  # Float inválido
        "adx_sideways_threshold": 15.3,
        **{k: v.default_value for k, v in space.params.items() 
           if k not in ["adx_trend_threshold", "adx_sideways_threshold"]}
    }
    
    projected = project_constraints(params, space)
    
    assert isinstance(projected["adx_trend_threshold"], int)
    assert isinstance(projected["adx_sideways_threshold"], int)
