"""
Tests para parameter space definition.
Spec: Codex PARTE 3
"""
import pytest
from src.optimization.param_space import (
    ParamSpace,
    ParamDef,
    ParamType,
    get_default_param_space
)


def test_param_space_contains_all_required_params():
    """
    Debe contener los 13 parámetros especificados en Codex PARTE 3.1
    """
    space = get_default_param_space()
    
    # Pure Alpha global multipliers (5)
    assert "g_ob_quality" in space.params
    assert "g_momentum" in space.params
    assert "g_volatility" in space.params
    assert "g_liquidity" in space.params
    assert "g_ml_confidence" in space.params
    
    # Alpha threshold (1)
    assert "alpha_threshold" in space.params
    
    # Classifier thresholds (4)
    assert "adx_trend_threshold" in space.params
    assert "adx_sideways_threshold" in space.params
    assert "atr_high_mult" in space.params
    assert "atr_low_mult" in space.params
    
    # Execution/Risk (3)
    assert "stop_loss_atr_mult" in space.params
    assert "take_profit_r_mult" in space.params
    assert "risk_per_trade_pct" in space.params
    
    # Total: 13 parámetros
    assert len(space.params) == 13


def test_param_ranges_match_codex_spec():
    """
    Rangos deben coincidir exactamente con Codex PARTE 3.1
    """
    space = get_default_param_space()
    
    # Pure Alpha multipliers
    assert space.params["g_ob_quality"].min_value == 0.50
    assert space.params["g_ob_quality"].max_value == 2.00
    
    assert space.params["g_momentum"].min_value == 0.50
    assert space.params["g_momentum"].max_value == 2.00
    
    assert space.params["g_volatility"].min_value == 0.50
    assert space.params["g_volatility"].max_value == 2.00
    
    assert space.params["g_liquidity"].min_value == 0.50
    assert space.params["g_liquidity"].max_value == 2.00
    
    assert space.params["g_ml_confidence"].min_value == 0.00
    assert space.params["g_ml_confidence"].max_value == 1.50
    
    # Alpha threshold
    assert space.params["alpha_threshold"].min_value == 0.45
    assert space.params["alpha_threshold"].max_value == 0.75
    
    # Classifier
    assert space.params["adx_trend_threshold"].min_value == 20
    assert space.params["adx_trend_threshold"].max_value == 35
    
    assert space.params["adx_sideways_threshold"].min_value == 10
    assert space.params["adx_sideways_threshold"].max_value == 22
    
    assert space.params["atr_high_mult"].min_value == 1.20
    assert space.params["atr_high_mult"].max_value == 2.00
    
    assert space.params["atr_low_mult"].min_value == 0.45
    assert space.params["atr_low_mult"].max_value == 0.85
    
    # Execution
    assert space.params["stop_loss_atr_mult"].min_value == 1.00
    assert space.params["stop_loss_atr_mult"].max_value == 3.50
    
    assert space.params["take_profit_r_mult"].min_value == 1.00
    assert space.params["take_profit_r_mult"].max_value == 4.00
    
    assert space.params["risk_per_trade_pct"].min_value == 0.25
    assert space.params["risk_per_trade_pct"].max_value == 1.25


def test_default_values_are_reasonable():
    """
    Valores default deben estar dentro de rangos.
    """
    space = get_default_param_space()
    
    for name, param in space.params.items():
        default = param.default_value
        assert param.min_value <= default <= param.max_value, \
            f"{name} default {default} fuera de rango [{param.min_value}, {param.max_value}]"


def test_param_types_correct():
    """
    Tipos de parámetros deben ser correctos (float o int).
    """
    space = get_default_param_space()
    
    # Float params
    float_params = [
        "g_ob_quality", "g_momentum", "g_volatility", 
        "g_liquidity", "g_ml_confidence",
        "alpha_threshold",
        "atr_high_mult", "atr_low_mult",
        "stop_loss_atr_mult", "take_profit_r_mult",
        "risk_per_trade_pct"
    ]
    
    for name in float_params:
        assert space.params[name].param_type == ParamType.FLOAT
    
    # Int params
    int_params = ["adx_trend_threshold", "adx_sideways_threshold"]
    
    for name in int_params:
        assert space.params[name].param_type == ParamType.INT


def test_sample_random_params_in_range():
    """
    sample_random() debe generar parámetros dentro de rangos.
    """
    space = get_default_param_space()
    
    # Sample 100 veces
    for _ in range(100):
        params = space.sample_random(seed=None)
        
        # Verificar que cada param está en rango
        for name, value in params.items():
            param_def = space.params[name]
            assert param_def.min_value <= value <= param_def.max_value, \
                f"{name}={value} fuera de rango"


def test_sample_random_reproducible_with_seed():
    """
    Con mismo seed, debe generar mismos parámetros.
    """
    space = get_default_param_space()
    
    params1 = space.sample_random(seed=42)
    params2 = space.sample_random(seed=42)
    
    assert params1 == params2


def test_get_defaults():
    """
    get_defaults() debe retornar dict con valores default.
    """
    space = get_default_param_space()
    defaults = space.get_defaults()
    
    assert len(defaults) == 13
    
    for name, value in defaults.items():
        assert value == space.params[name].default_value
